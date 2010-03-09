from twisted.internet.defer import Deferred

print """
This example illustrates how callbacks in a deferred
chain can return deferreds themselves.
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


# We add them all to a deferred and fire it:

d = Deferred()

d.addCallback(callback_1)
d.addCallback(callback_2)
d.addCallback(callback_3)

print """
Here we are firing a deferred with three callbacks that just print
their argument and return simple values:
"""

d.callback(0)

# And you get output like this:
# callback_1 got 0
# callback_2 got 1
# callback_3 got 2


# Now we make a callback that returns a deferred:

deferred_2 = None # NOTE: because we aren't using a reactor, we have
                  #       to fire this deferred from the 'outside'.
                  #       We store it in a global variable for this
                  #       purpose. In a normal Twisted program you
                  #       would never store a deferred in a global or
                  #       fire it from the outside. By 'outside' we
                  #       mean the deferred is not being fired by an
                  #       action set in motion by the callback that
                  #       created and returned the deferred, as is
                  #       normally the case.

def callback_2_async(res):
    print 'callback_2 got', res
    global deferred_2 # never do this in a real program
    deferred_2 = Deferred()
    return deferred_2


# We do the same thing, but use the async callback:

d = Deferred()

d.addCallback(callback_1)
d.addCallback(callback_2_async)
d.addCallback(callback_3)

print """
Here we are firing a deferred as above but the middle callback is
returning a deferred:
"""

d.callback(0)

# And you get output like this:
# callback_1 got 0
# callback_2 got 1

print """
Notice the output from the third callback is missing. That's because
the second callback returned a deferred and now the 'outer' deferred
is paused. It's not waiting in a thread or anything like that, it just
stopped invoking the callbacks in the chain. Instead, it registered
some callbacks on the 'inner' deferred which will start the outer
deferred back up when the inner deferred is fired.

We can see this in action by firing the inner deferred:
"""

deferred_2.callback(2)

# And you get output like this:
# callback_3 got 2

print """
Note the argument to the inner deferred's callback() method became
the result passed to the next callback in the outer deferred.
"""
