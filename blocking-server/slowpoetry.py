# This is the blocking version of the Slow Poetry Server.

import optparse, os, socket, time


def parse_args():
    usage = "usage: %prog [options] poetry-file"

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    option = parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    option = parser.add_option('--iface', help=help, default='')

    help = "The number of seconds between sending bytes."
    option = parser.add_option('--delay', type='float', help=help,
                               default=1)

    help = "The number of bytes to send at a time."
    option = parser.add_option('--num-bytes', type='int', help=help,
                               default=10)

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one poetry file.')

    poetry_file = args[0]

    if not os.path.exists(args[0]):
        parser.error('No such file: %s' % poetry_file)

    return options, poetry_file


def send_poetry(sock, poetry_file, num_bytes, delay):
    """Send some poetry slowly down the socket."""

    inputf = open(poetry_file)

    while True:
        bytes = inputf.read(num_bytes)

        if not bytes: # no more poetry :(
            sock.close()
            inputf.close()
            return

        try:
            sock.sendall(bytes)
        except socket.error:
            sock.close()
            inputf.close()
            return

        time.sleep(delay)


def serve(listen_socket, poetry_file, num_bytes, delay):
    while True:
        sock, addr = listen_socket.accept()

        print 'Somebody at %s wants poetry!' % (addr,)

        send_poetry(sock, poetry_file, num_bytes, delay)

        
def main():
    options, poetry_file= parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((options.iface, options.port or 0))

    sock.listen(5)

    print 'Serving %s on %s.' % (poetry_file, sock.getsockname())

    serve(sock, poetry_file, options.num_bytes, options.delay)


if __name__ == '__main__':
    main()
