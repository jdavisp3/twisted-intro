import sys, time

from twisted.internet.defer import Deferred

def start_chain(_):
    print "The start of the callback chain."

def blocking_poem(_):
    def delayed_write(s, delay):
        time.sleep(delay)
        sys.stdout.write(s)
        sys.stdout.flush()

    delayed_write('\n', 0)
    delayed_write('I', .6)
    delayed_write(' block', .4)
    delayed_write('\n  and', 1)
    delayed_write(' the', .4)
    delayed_write(' deferred', .6)
    delayed_write('\n  blocks', 1.5)
    delayed_write(' with', .2)
    delayed_write(' me', .2)
    delayed_write('\nas does', 1)
    delayed_write('\n the reactor', .6)
    delayed_write('\nkeep that', 1)
    delayed_write('\n factor', .6)
    delayed_write('\nin', 1)
    delayed_write(' mind', .4)
    delayed_write('\n\n', 2)

def end_chain(_):
    print "The end of the callback chain."
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallback(start_chain)
d.addCallback(blocking_poem)
d.addCallback(end_chain)

def fire():
    print 'Firing deferred.'
    d.callback(True)
    print 'Firing finished.'

from twisted.internet import reactor

reactor.callWhenRunning(fire)

print 'Starting reactor.'
reactor.run()
print 'Done.'
