from twisted.internet.defer import Deferred

print """\
This example illustrates how deferreds can
be fired before they are returned. First we
make a new deferred, fire it, then add some
callbacks.
"""

# three simple callbacks

def callback_1(res):
    print 'callback_1 got', res
    return 1

def callback_2(res):
    print 'callback_2 got', res
    return 2

def callback_3(res):
    print 'callback_3 got', res
    return 3

# We create a deferred and fire it immediately:
d = Deferred()

print 'Firing empty deferred.'
d.callback(0)

# Now we add the callbacks to the deferred.
# Notice how each callback fires immediately.

print 'Adding first callback.'
d.addCallback(callback_1)

print 'Adding second callback.'
d.addCallback(callback_2)

print 'Adding third callback.'
d.addCallback(callback_3)

print"""
Because the deferred was already fired, it
invoked each callback as soon as it was added.

Now we create a deferred and fire it, but
pause it first with the pause() method.
"""

# We do the same thing, but pause the deferred:

d = Deferred()
print 'Pausing, then firing deferred.'
d.pause()
d.callback(0)

print 'Adding callbacks.'
d.addCallback(callback_1)
d.addCallback(callback_2)
d.addCallback(callback_3)

print 'Unpausing the deferred.'
d.unpause()
