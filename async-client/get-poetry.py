# This is the asynchronous Get Poetry Now! client.

import datetime, errno, optparse, select, socket


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, asynchronous edition.
Run it like this:

  python get-poetry.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python async-client/get-poetry.py 10001 10002 10003

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
            host = ''
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


def get_poetry(sockets):
    """Download poety from all the given sockets."""

    poems = dict.fromkeys(sockets, '') # socket -> accumulated poem

    # socket -> task numbers
    sock2task = dict([(s, i + 1) for i, s in enumerate(sockets)])

    while sockets:
        rlist, _, _ = select.select(sockets, [], [])

        # rlist is the list of sockets with data ready to read

        for sock in rlist:
            bytes = ''

            while True:
                try:
                    bytes += sock.recv(1024)
                    if not bytes:
                        break
                except socket.error, e:
                    if e.args[0] == errno.EAGAIN:
                        break # we would have blocked
                    raise

            task_num = sock2task[sock]
            addr_fmt = format_address(sock.getsockname())

            if not bytes:
                sockets.remove(sock)
                sock.close()
                print 'Task %d finished' % task_num
            else:
                msg = 'Task %d: got %d bytes of poetry from %s'
                print  msg % (task_num, len(bytes), addr_fmt)

            poems[sock] += bytes

    return poems


def connect(address):
    """Connect to the given server and return a non-blocking socket."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.setblocking(0)
    return sock


def format_address(address):
    host, port = address
    return '%s:%s' % (host or 'localhost', port)


def main():
    addresses = parse_args()

    start = datetime.datetime.now()

    sockets = map(connect, addresses)

    poems = get_poetry(sockets)

    elapsed = datetime.datetime.now() - start

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    main()
