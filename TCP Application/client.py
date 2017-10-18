import os
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR, error
from common import __REQ_SEND_FILENAME_AND_SIZE, __REQ_UPLOAD, __MSG_FIELD_SEP, __RSP_FILEEXISTS, __RSP_OK, \
    __RSP_DISKSPACE_ERR
import ntpath


if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 2 Client program started")

    parser.add_argument('-f', '--filepath', \
                        help='File path to upload', \
                        required=False)

    args = parser.parse_args()
    filepath = args.filepath

    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('127.0.0.1', 7777))

    print 'Application started'
    try:
        # Client connects to server

        print 'Connected to the server %s:%d' % s.getpeername()
        print 'Local end-point bound on %s:%d' % s.getsockname()

        # Client send filename to server
        filename = ntpath.basename(filepath)
        filesize = str(os.path.getsize(filepath))
        s.send(__REQ_SEND_FILENAME_AND_SIZE + __MSG_FIELD_SEP + filename + __MSG_FIELD_SEP + filesize)
        response = s.recv(1024)

        # File with such name already exists in server
        if response.startswith(__RSP_FILEEXISTS):
            print "File with such name already exists"
            s.shutdown(SHUT_WR)
            s.close()

        elif response.startswith(__RSP_DISKSPACE_ERR):
            print "Server does not have enough disk space"
            s.shutdown(SHUT_WR)
            s.close()
        # Upload can begin
        elif response.startswith(__RSP_OK):
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
            print "Uploaded file: ", filename
            s.shutdown(SHUT_WR)
            f.close()
            raw_input('Press Enter to terminate ...')

            print 'Closing the TCP socket ...'
            s.close()
            print 'Terminating ...'

    except KeyboardInterrupt:
        print 'Closing the TCP socket ...'
        s.close()
        print 'Terminating ...'
