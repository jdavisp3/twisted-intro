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


def get_next_pair():
    """Get the next callback/errback pair from the user."""

    print """\
Enter a callback/errback pair in the form:

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
"""


    def get_cb(parts):
        if not parts:
            raise BadInput('missing command')

        cmd = parts.pop(0).lower()

        for command in ('return', 'fail', 'passthru'):
            if command.startswith(cmd):
                cmd = command
                break
        else:
            raise BadInput('bad command', cmd)

        if cmd in ('return', 'fail'):
            if not parts:
                raise BadInput('missing argument')

            result = parts.pop(0)

            if cmd == 'return':
                return lambda res: result
            else:
                def callback(res):
                    raise Exception(result)
                return callback

            return lambda res: res

    line = raw_input()

    if not line:
        return None

    parts = line.strip().split()

    callback, errback = get_cb(), get_cb()

    if parts:
        raise BadInput('extra arguments')

    return callback, errback




def main():
    parse_args()


if __name__ == '__main__':
    main()
