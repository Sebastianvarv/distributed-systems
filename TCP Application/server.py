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
    print 'Socket is bounded and listening on %s:%d' % s.getsockname()

    # Wait for a client to connect
    client_socket, client_addr = s.accept()
    print 'Client connected from %s:%d' % client_addr

    # Receiving the message,
    # here we need to the socket API what is the size of the block
    # that we are ready to receive at once
    recv_buffer_length = 1024

    print 'Waiting for message ...'
    # Append message block by block till terminator is found
    dumpdir = args.dumpdir
    filepath = dumpdir + "/" + str(uuid.uuid4()) + ".txt"
    print "Filepath:", filepath

    with open(filepath, 'w+') as f:
        while True:
            print "1"
            m = client_socket.recv(recv_buffer_length)
            print "received text block :", m
            if len(m) > 0:
                f.write(m)
                print "Wrote text block to file :", filepath
            else:
                break

    # print 'Total length %d bytes: [%s]' % (len(message), message)

    raw_input('Press Enter to terminate ...')

    client_socket.close()
    print 'Closed client socket...'
    s.close()
    print 'Closed the listener socket ...'
    print 'Terminating ...'
