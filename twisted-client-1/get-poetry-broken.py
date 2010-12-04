# This is the *Broken* Twisted Get Poetry Now! client, version 1.0.

# NOTE: This should not be used as the basis for production code.
# It uses low-level Twisted APIs as a learning exercise.

# Also, it's totally broken. See the explanation in Part 4
# to understand why.

import datetime, optparse, socket

from twisted.internet import main


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the *Broken* Get Poetry Now! client, Twisted version 1.0.
Run it like this:

  python get-poetry-broken.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-client-1/get-poetry-broken.py 10001 10002 10003

to grab poetry from servers on ports 10001, 10002, and 10003.

Of course, there need to be servers listening on those ports
for that to work.
"""

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print parser.format_help()
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


class PoetrySocket(object):

    poem = ''

    def __init__(self, task_num, address):
        self.task_num = task_num
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        #self.sock.setblocking(0) we don't set non-blocking -- broken!

        # tell the Twisted reactor to monitor this socket for reading
        from twisted.internet import reactor
        reactor.addReader(self)

    def fileno(self):
        try:
            return self.sock.fileno()
        except socket.error:
            return -1

    def connectionLost(self, reason):
        self.sock.close()

        # stop monitoring this socket
        from twisted.internet import reactor
        reactor.removeReader(self)

        # see if there are any poetry sockets left
        for reader in reactor.getReaders():
            if isinstance(reader, PoetrySocket):
                return

        reactor.stop() # no more poetry

    def doRead(self):
        poem = ''

        while True: # we're just reading everything (blocking) -- broken!
            bytes = self.sock.recv(1024)
            if not bytes:
                break
            poem += bytes

        msg = 'Task %d: got %d bytes of poetry from %s'
        print  msg % (self.task_num, len(poem), self.format_addr())

        self.poem = poem

        return main.CONNECTION_DONE

    def logPrefix(self):
        return 'poetry'

    def format_addr(self):
        host, port = self.address
        return '%s:%s' % (host or '127.0.0.1', port)


def poetry_main():
    addresses = parse_args()

    start = datetime.datetime.now()

    sockets = [PoetrySocket(i + 1, addr) for i, addr in enumerate(addresses)]

    from twisted.internet import reactor
    reactor.run()

    elapsed = datetime.datetime.now() - start

    for i, sock in enumerate(sockets):
        print 'Task %d: %d bytes of poetry' % (i + 1, len(sock.poem))

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    poetry_main()
