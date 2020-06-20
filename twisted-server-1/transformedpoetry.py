# This is the Twisted Poetry Transform Server, version 1.0

import sys
import optparse

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log


def parse_args():
    usage = """usage: %prog [options]

This is the Poetry Transform Server.
Run it like this:

  python transformedpoetry.py

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-server-1/transformedpoetry.py --port 11000

to provide poetry transformation on port 11000.
"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('--iface', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 0:
        parser.error('Bad arguments.')

    return options


class TransformService(object):

    def cummingsify(self, poem):
        return poem.lower()


class TransformProtocol(NetstringReceiver):
    '''The goal of separating the protocol and service ideally would put the
    utf8 processing in the service. However python names are now unicode.
    That means we can not use a byte string in the getattr call.
    
    I put the decode into stringReceived and overrode sendString to encode the data.
    
    Ideally we would probably want the decode/encode in the TransformService.
    
    The error handling was modified to provide feedback about what was truly failing.
    The original except returning None was not helpful.
    '''

    def stringReceived(self, request):
        if b'.' not in request: # bad request
            self.transport.loseConnection()
            return

        xform_name, poem = request.decode('utf8').split('.', 1)

        self.xformRequestReceived(xform_name, poem)

    def sendString(self, string):
        # Netstrings are really byte strings
        super().sendString(string.encode('utf8'))

    def xformRequestReceived(self, xform_name, poem):
        new_poem = self.factory.transform(xform_name, poem)

        if new_poem is not None:
            self.sendString(new_poem)

        self.transport.loseConnection()


class TransformFactory(ServerFactory):

    protocol = TransformProtocol

    def __init__(self, service):
        self.service = service

    def transform(self, xform_name, poem):
        thunk = getattr(self, 'xform_%s' % (xform_name,), None)

        if thunk is None: # no such transform
            log.msg("%r no such transform" % xform_name)
            return None

        try:
            return thunk(poem)
        except:
            log.msg(sys.exc_info()[0])
            return None # transform failed

    def xform_cummingsify(self, poem):
        return self.service.cummingsify(poem)


def main():
    options = parse_args()

    service = TransformService()

    factory = TransformFactory(service)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory,
                             interface=options.iface)

    print('Serving transforms on %s.' % (port.getHost(),))

    reactor.run()


if __name__ == '__main__':
    main()
