import os
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR, error
from common import __REQ_SEND_FILENAME_AND_SIZE, __REQ_UPLOAD, __MSG_FIELD_SEP, __RSP_FILEEXISTS, __RSP_OK, \
    __REQ_LISTFILES, __RSP_DISKSPACE_ERR, __REQ_DOWNLOAD, __RSP_NO_SUCH_FILE
import ntpath


def download_file(filename, server, data):
    path = os.getcwd() + "/" + filename
    f = open(path, 'wb')
    f.write(data)
    len_buffer = 1024
    part = server.recv(len_buffer)
    while part:
        f.write(part)
        print "Received filepart"
        part = server.recv(len_buffer)

    f.close()


def serve_file(filepath, client):
    f = open(filepath, 'rb')
    part = f.read(1024)
    while part:
        try:
            client.send(part)
            part = f.read(1024)
        except socket.error, e:
            print "Connection terminated (Broken pipe)"
            client.shutdown(SHUT_WR)
            client.close()
    client.shutdown(SHUT_WR)
    client.close()


if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 2 Client program started")

    parser.add_argument('-f', '--filepath', help='File path to upload', required=False)
    parser.add_argument('-l', '--listfiles', help='List files uploaded to server', required=False,
                        action='store_true')
    parser.add_argument('-d', '--download', help='Download file', required=False)

    args = parser.parse_args()
    filepath = args.filepath
    listfiles = args.listfiles
    download = args.download

    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('127.0.0.1', 7778))

    print 'Application started'
    try:
        # Client connects to server

        print 'Connected to the server %s:%d' % s.getpeername()
        print 'Local end-point bound on %s:%d' % s.getsockname()

        if listfiles:
            s.send(__REQ_LISTFILES + __MSG_FIELD_SEP)
            files = s.recv(1024)
            print "Files in server", files
            s.shutdown(SHUT_WR)

        elif download:
            s.send(__REQ_DOWNLOAD + __MSG_FIELD_SEP + download)
            response = s.recv(1024)
            response, data = response.split(__MSG_FIELD_SEP, 1)
            if response == __RSP_NO_SUCH_FILE:
                print "There is no such file in server, run client.py -l to list files"
            elif response == __RSP_OK:
                download_file(download, s, data)
                print "Downloaded file:", download

        elif filepath:
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
                serve_file(filepath, s)
                print "Uploaded file", filename

        raw_input('Press Enter to terminate ...')

        print 'Closing the TCP socket ...'
        s.close()
        print 'Terminating ...'

    except KeyboardInterrupt:
        print 'Closing the TCP socket ...'
        s.close()
        print 'Terminating ...'
