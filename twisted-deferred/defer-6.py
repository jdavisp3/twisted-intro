from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(lambda r: out(r), lambda e: out(e))
d.errback(Exception('First error'))
d.errback(Exception('Second error'))
print 'Finished'
