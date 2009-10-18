from twisted.internet.defer import Deferred
d = Deferred()
d.callback('Your result is served.')
print 'Finished'
