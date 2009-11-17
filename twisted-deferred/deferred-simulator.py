#!/usr/bin/env python

import optparse

from twisted.internet import defer
from twisted.python.failure import Failure

__doc__ = """\
usage: %prog
A Deferred simulator. Use this to see how a particular
set of callbacks and errbacks will fire in a deferred.\
"""

class BadInput(Exception): pass


def parse_args():
    parser = optparse.OptionParser(usage=__doc__)

    options, args = parser.parse_args()

    if args:
        parser.error('No arguments supported.')


class Screen(object):
    """An ascii screen."""

    def __init__(self):
        self.pixels = {} # (x, y) -> char

    def draw_char(self, x, y, char):
        self.pixels[x,y] = char

    def draw_horiz_line(self, x, y, width):
        for i in range(width):
            self.draw_char(x + i, y, '-')

    def draw_vert_line(self, x, y, height):
        for i in range(height):
            self.draw_char(x, y + i, '|')

    def draw_text(self, x, y, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, char)

    def __str__(self):
        width = max([p[0] + 1 for p in self.pixels] + [0])
        height = max([p[1] + 1 for p in self.pixels] + [0])

        s = ''

        for y in range(height):
            for x in range(width):
                s += self.pixels.get((x,y), ' ')
            s += '\n'

        return s
        

class Callback(object):
    """A single callback or errback."""

    height = 5

    def __init__(self, style, argument=None):
        self.style = style
        self.argument = argument
        self.min_width = len(repr(self)) + 4

    def __call__(self, res):
        if self.style == 'return':
            return self.argument
        if self.style == 'fail':
            raise Exception(self.argument)
        return res

    def __repr__(self):
        if self.style == 'passthru':
            return 'passthru'
        return self.style + ' ' + self.argument

    def draw(self, screen, x, y, width):
        screen.draw_horiz_line(x, y, width)
        screen.draw_horiz_line(x, y + 4, width)
        screen.draw_vert_line(x, y + 1, 3)
        screen.draw_vert_line(x + width - 1, y + 1, 3)
        screen.draw_text(x + 1, y + 2, repr(self).center(width - 2))


class Chain(object):
    """A chain of callback/errback pairs."""

    def __init__(self, pairs):
        assert pairs
        self.pairs = pairs
        self.callback_width = max([p[0].min_width for p in self.pairs] + [0])
        self.callback_width = max([p[1].min_width for p in self.pairs]
                                  + [self.callback_width])
        self.width = self.callback_width * 2 + 2
        self.height = Callback.height * len(self.pairs)
        self.height += 3 * len(self.pairs[1:])

    def __repr__(self):
        s = ''
        for p in self.pairs:
            s += repr(p) + '\n'
        return s

    def draw_chain(self, screen, x, y):
        for callback, errback in self.pairs:
            callback.draw(screen, x, y, self.callback_width)
            errback.draw(screen, x + self.callback_width + 2,
                         y, self.callback_width)
            y += Callback.height + 3

    def draw_callback(self, screen, x, y, result):
        d = self.make_drawing_deferred(screen, x, y)
        d.callback(result)

    def draw_errback(self, screen, x, y, result):
        d = self.make_drawing_deferred(screen, x, y)
        d.errback(Exception(result))

    def make_drawing_deferred(self, screen, x, y):
        callback_mid_x = x - 1 + self.callback_width / 2

        errback_left_x = x + self.callback_width + 2
        errback_mid_x = errback_left_x + self.callback_width / 2

        class DrawState(object):
            last_x = None
            last_y = None

        state = DrawState()

        def wrap_callback(cb, x):
            def callback(res):
                cb.draw(screen, x, state.last_y, self.callback_width)
                if state.last_x == x:
                    screen.draw_vert_line(x - 1 + self.callback_width / 2,
                                          state.last_y - 3, 3)
                elif state.last_x < x:
                    screen.draw_vert_line(callback_mid_x, state.last_y - 3, 2)
                    screen.draw_vert_line(errback_mid_x, state.last_y - 2, 2)
                    screen.draw_horiz_line(callback_mid_x + 1,
                                           state.last_y - 2,
                                           errback_mid_x - callback_mid_x - 1)
                else:
                    screen.draw_vert_line(errback_mid_x, state.last_y - 3, 2)
                    screen.draw_vert_line(callback_mid_x, state.last_y - 2, 2)
                    screen.draw_horiz_line(callback_mid_x + 1,
                                           state.last_y - 2,
                                           errback_mid_x - callback_mid_x - 1)
                state.last_x = x
                state.last_y += cb.height + 3
                return cb(res)
            return callback

        def draw_start(res):
            if isinstance(res, Failure):
                screen.draw_text(errback_left_x, y,
                                 res.value.args[0].center(self.callback_width))
                state.last_x = errback_left_x
            else:
                screen.draw_text(x, y, res.center(self.callback_width))
                state.last_x = x
            state.last_y = y + 4
            return res

        d = defer.Deferred()

        d.addBoth(draw_start)

        for pair in self.pairs:
            callback = wrap_callback(pair[0], x)
            errback = wrap_callback(pair[1], errback_left_x)
            d.addCallbacks(callback, errback)

        return d


def get_next_pair():
    """Get the next callback/errback pair from the user."""

    def get_cb():
        if not parts:
            raise BadInput('missing command')

        cmd = parts.pop(0).lower()

        for command in ('return', 'fail', 'passthru'):
            if command.startswith(cmd):
                cmd = command
                break
        else:
            raise BadInput('bad command: %s' % cmd)

        if cmd in ('return', 'fail'):
            if not parts:
                raise BadInput('missing argument')
            return Callback(cmd, parts.pop(0))
        else:
            return Callback(cmd)

    line = raw_input()

    if not line:
        return None

    parts = line.strip().split()

    callback, errback = get_cb(), get_cb()

    if parts:
        raise BadInput('extra arguments')

    return callback, errback


def get_pairs():
    """Get the list of callback/errback pairs from the user."""

    print """\
Enter a callback/errback pairs in the form:

  CALLBACK ERRBACK

Where CALLBACK and ERRBACK are one of:

  return VALUE
  fail VALUE
  passthru

And where VALUE is a string of only letters and numbers (no spaces).

You can abbreviate return/failure/passthru as r/f/p.

Examples:

  r awesome f terrible  # callback returns 'awesome'
                        # and errback raises Exception('terrible')

  f googly p # callback raises Exception('googly')
             # and errback passes it's failure along

Enter a blank line when you are done.
"""

    pairs = []

    while True:
        try:
            pair = get_next_pair()
        except BadInput, e:
            print 'ERROR:', e
            continue

        if pair is None:
            if not pairs:
                print 'You must enter at least one pair.'
                continue
            else:
                break

        pairs.append(pair)
           
    return pairs


def main():
    parse_args()

    chain = Chain(get_pairs())

    screen = Screen()

    chain.draw_callback(screen, 0, 0, 'initial')
    chain.draw_errback(screen, chain.width + 12, 0, 'initial')

    print screen


if __name__ == '__main__':
    main()
