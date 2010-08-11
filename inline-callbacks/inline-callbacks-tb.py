
import traceback

from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def my_callbacks():
    yield 1
    traceback.print_stack()
    from twisted.internet import reactor
    reactor.stop()

from twisted.internet import reactor
reactor.callWhenRunning(my_callbacks)
reactor.run()
