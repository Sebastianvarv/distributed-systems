from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR, error

if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 2 Client program started")

    parser.add_argument('-f', '--filepath', \
                        help='File path to upload', \
                        required=False)

    args = parser.parse_args()
    filepath = args.filepath


    print 'Application started'

    # Client connects to server
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('127.0.0.1', 7777))

    print 'Connected to the server %s:%d' % s.getpeername()
    print 'Local end-point bound on %s:%d' % s.getsockname()


    # Client opens file for reading

    f = open(filepath, 'rb')
    part = f.read(1024)
    while part:
        try:
            s.send(part)
            part = f.read(1024)
        except socket.error, e:
            print "Connection terminated (Broken pipe)"
            s.shutdown(SHUT_WR)
            s.close()
    s.shutdown(SHUT_WR)
    f.close()


    raw_input('Press Enter to terminate ...')

    print 'Closing the TCP socket ...'
    s.close()
    print 'Terminating ...'
