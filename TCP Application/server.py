import uuid
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket
from common import *
from common import __REQ_SEND_FILENAME, __REQ_UPLOAD, __MSG_FIELD_SEP, __RSP_FILEEXISTS, __RSP_OK, __MSG_END
import os.path


def file_exists(filename, dump_dir):
    return os.path.isfile(dump_dir + "/" + filename)


def download_file(dumpdir, filename, client):
    filepath = dumpdir + "/" + filename
    f = open(filepath, 'wb')
    len_buffer = 1024
    part = client.recv(len_buffer)
    while part:
        f.write(part)
        print "Received filepart and wrote to output"
        part = client.recv(len_buffer)
    f.close()


if __name__ == '__main__':

    print 'Application started'

    parser = ArgumentParser(description="Homework 2 Server program started")

    parser.add_argument('-d', '--dumpdir', \
                        help='Directory to dump files', \
                        required=False,
                        default="server_dump")

    args = parser.parse_args()
    dumpdir = args.dumpdir

    # Creating a TCP/IP socket
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('127.0.0.1', 7777))
    s.listen(0)

    while True:
        print 'Server is listening new connections on %s:%d' % s.getsockname()

        # Wait for a client to connect
        client_socket, client_addr = s.accept()
        print 'Client connected from :', client_addr

        received_msg = client_socket.recv(1024)
        header, msg = received_msg.split(__MSG_FIELD_SEP, 1)

        # Parse headers
        if header == __REQ_SEND_FILENAME:
            filename = msg
            if file_exists(filename, dumpdir):
                client_socket.send(__RSP_FILEEXISTS)
            else:
                client_socket.send(__RSP_OK)
                download_file(dumpdir, filename, client_socket)

        # Close the sesion
        raw_input('Press Enter to terminate ...')
        client_socket.close()
        print 'Closed client socket...'
        s.close()
        print 'Closed the listener socket ...'
        print 'Terminating ...'
        break
