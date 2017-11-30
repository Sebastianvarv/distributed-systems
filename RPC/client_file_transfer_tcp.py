import logging
import ntpath
import sys
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
from argparse import ArgumentParser
import os
from common import REQ_SEND_FILENAME_AND_SIZE, REQ_UPLOAD, MSG_FIELD_SEP, RSP_FILEEXISTS, RSP_OK, \
    REQ_LISTFILES, RSP_DISKSPACE_ERR, REQ_DOWNLOAD, RSP_NO_SUCH_FILE, MSG_FIELD_SEP, REQ_RENAME, REQ_DELETE

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

BUFFER_SIZE = 1024


def close_sock(s):
    s.shutdown(SHUT_WR)
    s.close()


def connect_server(server_addr, server_port):
    """
    Connects server port and returns socket
    :param server_port: port to connect
    :return: socket
    """
    server = (server_addr, server_port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(server)
    sock.send("")
    return sock


def handle_download(filename, server_addr, port):
    s = connect_server(server_addr, port)
    s.send(REQ_DOWNLOAD + MSG_FIELD_SEP + filename)
    response = s.recv(BUFFER_SIZE)
    response, data = response.split(MSG_FIELD_SEP, 1)
    if response == RSP_NO_SUCH_FILE:
        print "There is no such file in server, run client.py -l to list files"
    elif response == RSP_OK:
        LOG.info("Starting download for file: %s." % filename)
        path = os.getcwd() + "/" + filename
        f = open(path, 'wb')
        f.write(data)
        len_buffer = BUFFER_SIZE
        part = s.recv(len_buffer)
        while part:
            try:
                f.write(part)
                part = s.recv(len_buffer)
            except socket.error, e:
                print "Connection terminated (Broken pipe)"
                s.shutdown(SHUT_WR)
                s.close()
        f.close()
        s.shutdown(SHUT_WR)
        s.close()
        LOG.info("Received file: " + filename)
        return


def handle_listing(server_addr, port):
    LOG.info("Starting file listing.")
    s = connect_server(server_addr, port)
    s.send(REQ_LISTFILES + MSG_FIELD_SEP)
    files = s.recv(BUFFER_SIZE)
    close_sock(s)
    print "Files in server", files
    return


def handle_upload(filename, server_addr, port):
    LOG.info("Starting upload for file: %s." % filename)
    s = connect_server(server_addr, port)

    # Client send filename to server
    file_size = str(os.path.getsize(filename))

    s.send(REQ_SEND_FILENAME_AND_SIZE + MSG_FIELD_SEP + filename + MSG_FIELD_SEP + file_size)
    response = s.recv(BUFFER_SIZE)

    # File with such name already exists in server
    if response.startswith(RSP_FILEEXISTS):
        print "File with such name already exists"
    elif response.startswith(RSP_DISKSPACE_ERR):
        print "Server does not have enough disk space"
    # Upload can begin
    elif response.startswith(RSP_OK):
        # Client opens file for reading
        filepath = os.getcwd() + "/" + filename
        f = open(filepath, 'rb')
        part = f.read(BUFFER_SIZE)
        while part:
            try:
                s.send(part)
                part = f.read(BUFFER_SIZE)
            except socket.error, e:
                print "Connection terminated (Broken pipe)"
                close_sock(s)
        close_sock(s)
        LOG.debug("Uploaded " + args.upload)
    return


def handle_delete(delete, server_addr, port):
    s = connect_server(server_addr, port)
    s.send(REQ_DELETE + MSG_FIELD_SEP + delete)

    response = s.recv(BUFFER_SIZE)

    if response.startswith(RSP_OK):
        print("File successfully deleted")
    elif response.startswith(RSP_NO_SUCH_FILE):
        print("File not found")
    else:
        print("Something went wrong, rsp:" + response)


def handle_rename(rename, server_addr, port):
    s = connect_server(server_addr, port)
    oldfile, newfile = rename
    s.send(REQ_RENAME + MSG_FIELD_SEP + oldfile + MSG_FIELD_SEP + newfile)
    response = s.recv(BUFFER_SIZE)

    if response.startswith(RSP_OK):
        print("File successfully renamed")
    elif response.startswith(RSP_NO_SUCH_FILE):
        print("File not found")
    else:
        print("Something went wrong, rsp:" + response)


def main(args):
    # In this way ONLY one HANDLE is done, and that is fine, don't handle upload and download with same request.

    # Add server address and port when calling handle functions

    if args.upload:
        LOG.debug("Upload chosen")
        handle_upload(args.upload, args.server_addr, args.port)
    elif args.list:
        LOG.debug("Listing chosen")
        handle_listing(args.server_addr, args.port)

    elif args.download:
        LOG.debug("Download chosen")
        handle_download(args.download, args.server_addr, args.port)

    elif args.rename:
        LOG.debug("Rename chosen")
        handle_rename(args.rename, args.server_addr, args.port)

    elif args.delete:
        LOG.debug("Delete chosen")
        handle_delete(args.delete, args.server_addr, args.port)
    # If something else then log it and exit
    return None


if __name__ == "__main__":
    parser = ArgumentParser(description="Client for uploading/listing files.")
    parser.add_argument('-a', '--server-addr', help="Address of the host. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-u', '--upload', help="File to be uploaded.")
    parser.add_argument('-l', '--list', help="List all the files in the server.", action='store_true')
    parser.add_argument('-d', '--download', help="Download specified file.")
    parser.add_argument('-r', '--rename', help="Rename file", nargs='*')
    parser.add_argument('-e', '--delete', help="Delete file")
    args = parser.parse_args()
    main(args)
