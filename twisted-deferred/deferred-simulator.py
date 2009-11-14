#!/usr/bin/env python

import optparse

from twisted.internet import defer

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

    def draw(self, x, y, char):
        self.pixels[x,y] = char

    def __str__(self):
        width = max(p[0] for p in self.pixels)
        height = max(p[1] for p in self.pixels)

        s = ''

        for y in range(height):
            for x in range(width):
                s += self.pixels.get((x,y), ' ')
            s += '\n'

        return s
        

class Callback(object):

    height = 5

    def __init__(self, style, argument=None):
        self.style = style
        self.argument = argument

    @property
    def min_width(self):
        return len(repr(self)) + 4

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
            break

        pairs.append(pair)
           
    return pairs


def main():
    parse_args()
    print get_pairs()


if __name__ == '__main__':
    main()
