# This is the blocking Get Poetry Now! client.

import datetime, optparse, socket


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, blocking edition.
Run it like this:

  python get-poetry.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python blocking-client/get-poetry.py 1001 1002 1003

to grab poetry from servers on ports 1001, 1002, and 1003.

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


def get_poetry(address):
    pass


def main():
    addresses = parse_args()

    elapsed = datetime.timedelta()

    for address in addresses:
        print 'Getting poetry from: %s' % (address,)
        start = datetime.datetime.now()
        poem = get_poetry(address)
        time = datetime.datetime.now() - start
        print 'Got a poem from %s in %s' % (address, time)
        elapsed += time

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    main()
