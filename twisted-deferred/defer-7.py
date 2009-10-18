from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(lambda r: out(r), lambda e: out(e))
d.errback(Exception('First error'))
d.callback('First result')
print 'Finished'
