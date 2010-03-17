# This is the Twisted Poetry Proxy, version 1.0

import optparse

from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory, ServerFactory, Protocol


def parse_args():
    usage = """usage: %prog [options] [hostname]:port

This is the Poetry Proxy, version 1.0.

  python poetry-proxy.py [hostname]:port

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-server-1/poetry-proxy.py 10000

to proxy the poem for the server running on port 10000.
"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('--iface', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one server address.')

    def parse_address(addr):
        if ':' not in addr:
            host = ''
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return options, parse_address(args[0])


class PoetryProxyProtocol(Protocol):

    def connectionMade(self):
        self.transport.write(self.factory.poem)
        self.transport.loseConnection()


class PoetryProxyFactory(ServerFactory):

    protocol = PoetryProxyProtocol

    def __init__(self, service):
        self.service = service


class PoetryClientProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)


class PoetryClientFactory(ClientFactory):

    protocol = PoetryClientProtocol

    def __init__(self):
        self.deferred = Deferred()

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)


def main():
    options, server_addr = parse_args()

    factory = PoetryFactory(poem)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory,
                             interface=options.iface)

    print 'Proxying %s on %s.' % (server_addr, port.getHost())

    reactor.run()


if __name__ == '__main__':
    main()
