from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(lambda r: out(r), lambda e: out(e))
d.callback('First result')
d.callback('Second result')
print 'Finished'
