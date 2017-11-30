import glob
import os
import threading
import logging
import xmlrpclib

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn

from argparse import ArgumentParser

# Please use LOGGING
FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class FileServerRequestHandler(ThreadingMixIn, SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class Server:
    def __init__(self, args):
        LOG.info("Server Started.")
        self.server_sock = (args.laddr, int(args.port))
        self.dump_dir = args.dump
        self.max_size = args.max_filesize

        # Initilize RPC service on specific port

        # Register server-side functions into RPC middleware
        self.server = SimpleXMLRPCServer(self.server_sock, requestHandler=FileServerRequestHandler)
        self.server.register_introspection_functions()
        self.server.register_instance(self)

        # Start the main thread now
        self.start_main()

    def list_files(self):
        return os.listdir(self.dump_dir)

    def download_file(self, filename):
        with open(self.dump_dir + "/" + filename, "rb") as f:
            return xmlrpclib.Binary(f.read())

    def upload_file(self, filename, filedata):
        with open(self.dump_dir + "/" + filename, "wb") as f:
            f.write(filedata)
        return True

    def delete_file(self, filename):
        try:
            os.remove(self.dump_dir + "/" + filename)
        except:
            return False
        return True

    def rename_file(self, old_filename, new_filename):
        old_file = self.dump_dir + "/" + old_filename
        new_file = self.dump_dir + "/" + new_filename
        try:
            os.rename(old_file, new_file)
        except:
            return False
        return True

    def start_main(self):
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print 'Ctrl+C issued, terminating ...'
        finally:
            self.server.shutdown()  # Stop the serve-forever loop
            self.server.server_close()  # Close the sockets
        print 'Terminating ...'


# start the RPC server


# NB! READ ARGPARSER DESCRIPTION IN CLIENT, if confused by argparsers
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--laddr', help="Listen address. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-d', '--dump', help="Folder as dump dir.", default="dump")
    parser.add_argument('-m', '--max-filesize', help="Max filesize for server", default=10 * 1024 * 1024, type=int)
    args = parser.parse_args()

    s = Server(args)
