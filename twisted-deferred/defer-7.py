from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(out, out)
d.errback(Exception('First error'))
d.callback('First result')
print 'Finished'
