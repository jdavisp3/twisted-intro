import sys

from twisted.python import log
from twisted.internet import defer

"""This example illustrates some Twisted logging basics."""

log.msg('This will not be logged, we have not installed a logger.')

log.startLogging(sys.stdout)

log.msg('This will be logged.')
log.err('This will be logged as an error.')

def bad_callback(result):
    xxx

try:
    bad_callback()
except:
    log.err('The next function call will log the traceback as an error.')
    log.err()

d = defer.Deferred()

def on_error(failure):
    log.err('The next function call will log the failure as an error.')
    log.err(failure)

d.addCallback(bad_callback)
d.addErrback(on_error)

d.callback(True)

log.msg('End of example.')
