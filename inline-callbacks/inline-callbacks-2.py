
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue

@inlineCallbacks
def my_callbacks_1():
    from twisted.internet import reactor

    print 'my_callbacks_1 first callback'
    d = Deferred()
    reactor.callLater(2, d.callback, None)
    yield d

    print 'my_callbacks_1 second callback'
    d = Deferred()
    reactor.callLater(2, d.callback, None)
    yield d

    print 'my_callbacks_1 third callback'
    returnValue(1)

@inlineCallbacks
def my_callbacks_err():
    from twisted.internet import reactor

    print 'my_callbacks_err first callback'
    d = Deferred()
    reactor.callLater(3, d.callback, None)
    yield d

    print 'my_callbacks_err second callback'
    d = Deferred()
    reactor.callLater(3, d.callback, None)
    yield d

    print 'my_callbacks_err third callback'
    raise Exception('uh oh')

def got_result(res):
    print 'got result:', res

def got_error(err):
    print 'got error:', err

def run_callbacks():
    d1 = my_callbacks_1()
    d1.addCallbacks(got_result, got_error)

    d2 = my_callbacks_err()
    d2.addCallbacks(got_result, got_error)

    from twisted.internet import reactor

    def callbacks_finished(_):
        callbacks_finished.count += 1
        if callbacks_finished.count == 2:
            print 'all done'
            reactor.stop()
    callbacks_finished.count = 0

    d1.addBoth(callbacks_finished)
    d2.addBoth(callbacks_finished)


from twisted.internet import reactor
reactor.callWhenRunning(run_callbacks)
reactor.run()
