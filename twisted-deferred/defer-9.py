import sys

from twisted.internet.defer import Deferred

def got_poem(poem):
    print(poem)

def poem_failed(err):
    print('poem download failed', file=sys.stderr)
    print('I am terribly sorry', file=sys.stderr)
    print('try again later?', file=sys.stderr)

def poem_done(_):
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallbacks(got_poem, poem_failed)
d.addBoth(poem_done)

from twisted.internet import reactor

reactor.callWhenRunning(d.callback, 'Another short poem.')

reactor.run()
