from twisted.internet.defer import Deferred
d = Deferred()
d.errback(Exception('Something has gone wrong.'))
print 'Finished'
