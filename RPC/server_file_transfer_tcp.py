import os
import threading
import logging
import json

from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
from common import REQ_SEND_FILENAME_AND_SIZE, REQ_UPLOAD, MSG_FIELD_SEP, RSP_FILEEXISTS, RSP_OK, \
    REQ_LISTFILES, RSP_DISKSPACE_ERR, REQ_DOWNLOAD, RSP_NO_SUCH_FILE, MSG_FIELD_SEP, REQ_RENAME, REQ_DELETE

BUFFER_SIZE = 1024

# Please use LOGGING
FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


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


def serve_file(dumpdir, filename, client):
    f = open((dumpdir + "/" + filename), 'rb')
    part = f.read(1024)
    while part:
        try:
            client.send(part)
            part = f.read(1024)
        except socket.error as e:
            print "Connection terminated (Broken pipe)"
            client.shutdown(SHUT_WR)
            client.close()
    client.shutdown(SHUT_WR)
    client.close()


def rename_file(dumpdir, filename_old, filename_new, client):
    old_file = dumpdir + "/" + filename_old
    new_file = dumpdir + "/" + filename_new
    try:
        os.rename(old_file, new_file)
        client.send(RSP_OK + MSG_FIELD_SEP)
    except:
        client.send(RSP_NO_SUCH_FILE + MSG_FIELD_SEP)

    client.shutdown(SHUT_WR)
    client.close()


def delete_file(dumpdir, filename, client):
    try:
        os.remove(dumpdir + "/" + filename)
        client.send(RSP_OK + MSG_FIELD_SEP)
    except:
        client.send(RSP_NO_SUCH_FILE + MSG_FIELD_SEP)

    client.shutdown(SHUT_WR)
    client.close()


class Server:
    def __init__(self, args):
        LOG.info("Server Started.")
        self.socket = self.__socket_init(args.laddr, args.port)
        self.dump_dir = args.dump
        self.max_filesize = args.max_filesize
        # If there is no dump directory, create it
        if not os.path.exists(self.dump_dir):
            os.mkdir(self.dump_dir)
        # Start the main thread now
        self.start_main()

    @staticmethod
    def __socket_init(server_ip, port):
        # Create socket and return it
        # Please handle errors for socket creation if there appears any
        # Returns None right now because otherwise it would not compile
        sock = None
        try:
            server = (server_ip, port)
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind(server)
            sock.listen(10)
        except:
            LOG.info("Socket initalizing failed")
        return sock

    def start_main(self):
        # THIS IS MAIN THREAD
        # RECEIVE LOOP
        # IF CLIENT CONNECTS, Handle client on different thread
        # LOOP FOREVER
        # Just for information: This method only connects and assigns threads, no recv or send required
        global client_sock
        try:
            while True:
                client_sock = None
                client_sock, client_addr = self.socket.accept()
                client_thread = threading.Thread(self.handle_client(client_sock))
                client_thread.start()
        except KeyboardInterrupt:
            print "Closing server"
        finally:
            if client_sock != None:
                client_sock.close()
            self.socket.close()

        return

    def handle_client(self, client_socket):
        # HANDLE UPLOAD, LISTING, DOWNLOAD
        # Then close thread
        # Recv and send only in this method basically
        try:
            received_msg = client_socket.recv(1024)
            header, msg = received_msg.split(MSG_FIELD_SEP, 1)

            # Parse headers
            if header == REQ_SEND_FILENAME_AND_SIZE:
                LOG.info("Upload chosen")
                filename, filesize = msg.split(MSG_FIELD_SEP, 1)
                if file_exists(filename, self.dump_dir):
                    client_socket.send(RSP_FILEEXISTS)
                else:
                    if self.max_filesize < int(filesize):
                        print "Not enough space on disk"
                        client_socket.send(RSP_DISKSPACE_ERR)
                    else:
                        client_socket.send(RSP_OK)
                        download_file(self.dump_dir, filename, client_socket)
                        print "Downloaded file: ", filename
            elif header == REQ_LISTFILES:
                LOG.info("List files request received")

                files = os.listdir(self.dump_dir)
                LOG.info("Files list" + str(files))
                client_socket.send(str(files))

            elif header == REQ_DOWNLOAD:
                filename = msg
                if os.path.isfile(self.dump_dir + "/" + filename):
                    client_socket.send(RSP_OK + MSG_FIELD_SEP)
                    serve_file(self.dump_dir, filename, client_socket)
                else:
                    client_socket.send(RSP_NO_SUCH_FILE)

            elif header == REQ_RENAME:
                old_file, new_file = msg.split(MSG_FIELD_SEP, 1)
                rename_file(self.dump_dir, old_file, new_file, client_socket)

            elif header == REQ_DELETE:
                filename = msg
                delete_file(self.dump_dir, filename, client_socket)

        except:
            LOG.debug("Something went wrong:" + received_msg)
            pass


# NB! READ ARGPARSER DESCRIPTION IN CLIENT, if confused by argparsers
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--laddr', help="Listen address. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-d', '--dump', help="Folder as dump dir.", default="dump")
    parser.add_argument('-m', '--max-filesize', help="Max filesize for server", default=10 * 1024 * 1024, type=int)
    args = parser.parse_args()
    s = Server(args)
