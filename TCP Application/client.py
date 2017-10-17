from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM,  socket

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
    destination = ('127.0.0.1', 7777)
    s.connect(destination)

    print 'Connected to the server %s:%d' % s.getpeername()
    print 'Local end-point bound on %s:%d' % s.getsockname()


    # Client opens file for reading

    msg = ""
    with open(filepath, 'r') as f:
        for line in f:
            msg += line

    s.sendall(msg)

    print 'Sent message to %s:%d' % destination


    raw_input('Press Enter to terminate ...')

    print 'Closing the TCP socket ...'
    s.close()
    print 'Terminating ...'
