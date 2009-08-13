import traceback
from twisted.internet import reactor
reactor.callWhenRunning(traceback.print_stack)
reactor.run()
