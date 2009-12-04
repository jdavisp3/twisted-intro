#!/usr/bin/env python

import optparse, sys

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

    help = "draw all three chains in one column"
    parser.add_option('--narrow', action='store_true', help=help)

    options, args = parser.parse_args()

    if args:
        parser.error('No arguments supported.')

    return options


class Screen(object):
    """An ascii screen."""

    def __init__(self):
        self.pixels = {} # (x, y) -> char

    def draw_char(self, x, y, char):
        self.pixels[x,y] = char

    def draw_horiz_line(self, x, y, width):
        for i in range(width):
            self.draw_char(x + i, y, '-')

    def draw_vert_line(self, x, y, height, end_arrow=False):
        for i in range(height):
            self.draw_char(x, y + i, '|')
        if end_arrow:
            self.draw_char(x - 1, y + height - 1, '\\')
            self.draw_char(x + 1, y + height - 1, '/')

    def draw_text(self, x, y, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, char)

    def clear(self):
        self.pixels.clear()

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
    """
    A widget representing a single callback or errback.

    Each callback widget has one of three styles:

      return - a callback that returns a given value
      fail - a callback that raises an Exception(value)
      passthru - a callback that returns its argument unchanged

    The widget is also a callable that behaves according
    to the widget's style.
    """

    height = 5

    def __init__(self, style, value=None):
        self.style = style
        self.value = value
        self.min_width = len('0123456*') + len('return ') + 3

    def __call__(self, res):
        if self.style == 'return':
            return self.value
        if self.style == 'fail':
            return Failure(Exception(self.value))
        return res

    @property
    def caption(self):
        if self.style == 'passthru':
            return 'passthru'
        return self.style + ' ' + self.value

    def format_value(self, res):
        if isinstance(res, Failure):
            return res.value.args[0] + '*'
        return res

    def draw_passive(self, screen, x, y, width):
        self.draw_box(screen, x, y, width)
        self.draw_text(screen, x, y + 2, width, self.caption)

    def draw_active(self, screen, x, y, width, res):
        self.draw_box(screen, x, y, width)
        self.draw_text(screen, x, y + 1, width, self.format_value(res))
        self.draw_text(screen, x, y + 3, width, self.format_value(self(res)))

    def draw_box(self, screen, x, y, width):
        screen.draw_horiz_line(x, y, width)
        screen.draw_horiz_line(x, y + 4, width)
        screen.draw_vert_line(x, y + 1, 3)
        screen.draw_vert_line(x + width - 1, y + 1, 3)

    def draw_text(self, screen, x, y, width, text):
        screen.draw_text(x + 1, y, text.center(width - 2))
        

class Deferred(object):
    """
    An widget for a deferred.

    It is initialize with a non-empty list of Callback pairs,
    representing a callback chain in a Twisted Deferred.
    """

    def __init__(self, pairs):
        assert pairs
        self.pairs = pairs
        self.callback_width = max([p[0].min_width for p in self.pairs] + [0])
        self.callback_width = max([p[1].min_width for p in self.pairs]
                                  + [self.callback_width])
        self.width = self.callback_width * 2 + 2
        self.height = Callback.height * len(self.pairs)
        self.height += 3 * len(self.pairs[1:])

    def draw(self, screen, x, y):
        """
        Draw a representation of the callback/errback chain
        on the given screen at the given coordinates.
        """
        for callback, errback in self.pairs:
            callback.draw_passive(screen, x, y, self.callback_width)
            errback.draw_passive(screen, x + self.callback_width + 2,
                                 y, self.callback_width)
            y += Callback.height + 3


class FiredDeferred(object):
    """
    A widget for a fired deferred.

    It is initialized with a Deferred widget (not a real deferred)
    and the method name ('callback' or 'errback') to draw the firing
    sequence for.
    """

    callback_y_offset = 4

    def __init__(self, deferred, method):
        self.deferred = deferred
        self.method = method
        self.height = deferred.height + 8
        self.width = deferred.width

    def draw(self, screen, x, y, result='initial'):
        d = self.make_drawing_deferred(screen, x, y)

        if self.method == 'callback':
            d.callback(result)
        else:
            d.errback(Exception(result))

    def make_drawing_deferred(self, screen, x, y):
        """
        Return a new deferred that, when fired, will draw its
        firing sequence onto the given screen at the given coordinates.
        """

        callback_width = self.deferred.callback_width

        callback_mid_x = x - 1 + callback_width / 2

        errback_left_x = x + callback_width + 2
        errback_mid_x = errback_left_x - 1 + callback_width / 2

        class DrawState(object):
            last_x = None
            last_y = None

        state = DrawState()

        def draw_connection(x):
            if state.last_x == x:
                screen.draw_vert_line(x - 1 + callback_width / 2,
                                      state.last_y - 3, 3, True)
                return

            if state.last_x < x:
                screen.draw_vert_line(callback_mid_x, state.last_y - 3, 2)
                screen.draw_vert_line(errback_mid_x,
                                      state.last_y - 2, 2, True)
            else:
                screen.draw_vert_line(errback_mid_x, state.last_y - 3, 2)
                screen.draw_vert_line(callback_mid_x,
                                      state.last_y - 2, 2, True)

            screen.draw_horiz_line(callback_mid_x + 1,
                                   state.last_y - 2,
                                   errback_mid_x - callback_mid_x - 1)

        def wrap_callback(cb, x):
            def callback(res):
                cb.draw_active(screen, x, state.last_y, callback_width, res)
                draw_connection(x)
                state.last_x = x
                state.last_y += cb.height + 3
                return cb(res)
            return callback

        def draw_value(res, y):
            if isinstance(res, Failure):
                text = res.value.args[0] + '*'
                text = text.center(callback_width + 20)
                screen.draw_text(errback_left_x - 10, y, text)
            else:
                screen.draw_text(x, y, res.center(callback_width))

        def draw_start(res):
            draw_value(res, y)
            if isinstance(res, Failure):
                state.last_x = errback_left_x
            else:
                state.last_x = x
            state.last_y = y + 4
            return res

        def draw_end(res):
            draw_value(res, state.last_y)
            if isinstance(res, Failure):
                draw_connection(errback_left_x)
            else:
                draw_connection(x)

        d = defer.Deferred()

        d.addBoth(draw_start)

        for pair in self.deferred.pairs:
            callback = wrap_callback(pair[0], x)
            errback = wrap_callback(pair[1], errback_left_x)
            d.addCallbacks(callback, errback)

        d.addBoth(draw_end)

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

            result = parts.pop(0)

            if len(result) > 6:
                raise BadInput('result more than 6 chars long', result)

            return Callback(cmd, result)
        else:
            return Callback(cmd)

    try:
        line = raw_input()
    except EOFError:
        sys.exit()

    if not line:
        return None

    parts = line.strip().split()

    callback, errback = get_cb(), get_cb()

    if parts:
        raise BadInput('extra arguments')

    return callback, errback


def get_pairs():
    """
    Get the list of callback/errback pairs from the user.
    They are returned as Callback widgets.
    """

    print """\
Enter a list of callback/errback pairs in the form:

  CALLBACK ERRBACK

Where CALLBACK and ERRBACK are one of:

  return VALUE
  fail VALUE
  passthru

And where VALUE is a string of only letters and numbers (no spaces),
no more than 6 characters long.

Each pair should be on a single line and you can abbreviate
return/fail/passthru as r/f/p.

Examples:

  r good f bad  # callback returns 'good'
                # and errback raises Exception('bad')

  f googly p    # callback raises Exception('googly')
                # and errback passes its failure along

Enter a blank line when you are done, and a diagram of the deferred
will be printed next to the firing patterns for both the callback()
and errback() methods. In the diagram, a value followed by '*' is
really an Exception wrapped in a Failure, i.e:

  value* == Failure(Exception(value))

You will want to make your terminal as wide as possible.
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


def draw_single_column(d, callback, errback):
    screen = Screen()

    screen.draw_text(0, 1, 'Deferred'.center(d.width))
    screen.draw_text(0, 2, '--------'.center(d.width))

    d.draw(screen, 0, 4)

    print screen

    screen.clear()

    screen.draw_text(0, 2, 'd.callback(initial)'.center(d.width))
    screen.draw_text(0, 3, '-------------------'.center(d.width))

    callback.draw(screen, 0, 5)

    print screen

    screen.clear()

    screen.draw_text(0, 2, 'd.errback(initial*)'.center(d.width))
    screen.draw_text(0, 3, '-------------------'.center(d.width))

    errback.draw(screen, 0, 5)

    print screen


def draw_multi_column(d, callback, errback):
    screen = Screen()

    screen.draw_text(0, 0, 'Deferred'.center(d.width))
    screen.draw_text(0, 1, '--------'.center(d.width))

    screen.draw_text(d.width + 6, 0, 'd.callback(initial)'.center(d.width))
    screen.draw_text(d.width + 6, 1, '-------------------'.center(d.width))

    screen.draw_text(2 * (d.width + 6), 0, 'd.errback(initial*)'.center(d.width))
    screen.draw_text(2 * (d.width + 6), 1, '-------------------'.center(d.width))

    d.draw(screen, 0, callback.callback_y_offset + 3)
    callback.draw(screen, d.width + 6, 3)
    errback.draw(screen, 2 * (d.width + 6), 3)

    screen.draw_vert_line(d.width + 3, 3, callback.height)
    screen.draw_vert_line(d.width + 3 + d.width + 6, 3, callback.height)

    print screen


def main():
    options = parse_args()

    d = Deferred(get_pairs())
    callback = FiredDeferred(d, 'callback')
    errback = FiredDeferred(d, 'errback')

    if options.narrow:
        draw_single_column(d, callback, errback)
    else:
        draw_multi_column(d, callback, errback)


if __name__ == '__main__':
    main()
