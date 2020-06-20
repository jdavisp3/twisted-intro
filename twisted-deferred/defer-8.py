import sys

from twisted.internet.defer import Deferred

def got_poem(poem):
    print(poem)
    from twisted.internet import reactor
    reactor.stop()

def poem_failed(err):
    print('poem download failed', file=sys.stderr)
    print('I am terribly sorry', file=sys.stderr)
    print('try again later?', file=sys.stderr)
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallbacks(got_poem, poem_failed)

from twisted.internet import reactor

reactor.callWhenRunning(d.callback, 'Another short poem.')

reactor.run()
