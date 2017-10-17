'''
Created on Apr 21, 2016

@author: Developer
'''

# From socket module we import the required structures and constants.
import uuid
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket

if __name__ == '__main__':

    print 'Application started'

    parser = ArgumentParser(description="Homework 2 Server program started")

    parser.add_argument('-d', '--dumpdir', \
                        help='Directory to dump files', \
                        required=False,
                        default="server_dump")

    args = parser.parse_args()

    # Creating a TCP/IP socket
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('127.0.0.1', 7777))
    s.listen(0)

    while True:
        print 'Server is listening new connections on %s:%d' % s.getsockname()

        dumpdir = args.dumpdir

        # Wait for a client to connect
        client_socket, client_addr = s.accept()
        print 'Client connected from :', client_addr

        filepath = dumpdir + "/" + str(uuid.uuid4()) + ".txt"
        print "Filepath:", filepath
        f = open(filepath, 'wb')

        len_buffer = 1024
        part = client_socket.recv(len_buffer)
        while part:
            f.write(part)
            print "Received filepart and wrote to output"
            part = client_socket.recv(len_buffer)
        f.close()

    # print 'Total length %d bytes: [%s]' % (len(message), message)

    raw_input('Press Enter to terminate ...')

    client_socket.close()
    print 'Closed client socket...'
    s.close()
    print 'Closed the listener socket ...'
    print 'Terminating ...'
