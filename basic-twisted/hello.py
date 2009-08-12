
def hello():
    print 'Hello from the reactor loop!'

from twisted.internet import reactor

reactor.callWhenRunning(hello)

reactor.run()
