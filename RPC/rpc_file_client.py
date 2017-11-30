import logging
import sys
from argparse import ArgumentParser
import os
from xmlrpclib import ServerProxy

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


def main(args):
    server = (args.server_addr, int(args.port))
    try:
        proxy = ServerProxy("http://%s:%d" % server)
        LOG.info('Connected to Mboard XMLRPC server!')

        methods = filter(lambda x: 'system.' not in x, proxy.system.listMethods())
        LOG.debug('Remote methods are: [%s] ' % (', '.join(methods)))

        if args.upload:
            LOG.debug("Upload chosen")
            handle_upload(proxy, args.upload[0])
        elif args.download:
            LOG.debug("Download chosen")
            handle_download(proxy, args.download[0])
        elif args.move:
            LOG.debug("Rename chosen")
            old_file, new_file = args.move
            handle_move(proxy, old_file, new_file)
        elif args.remove:
            LOG.debug("Remove chosen")
            handle_delete(proxy, args.remove[0])
        else:
            LOG.debug("Listing chosen")
            handle_listing(proxy)

    except KeyboardInterrupt:
        LOG.warn('Ctrl+C issued, terminating')
        exit(0)
    except Exception as e:
        LOG.error('Communication error %s ' % str(e))
        exit(1)


def handle_download(proxy, filename):
    LOG.info("Starting download for file: %s." % filename)
    # Use RPC proxy and initialize download
    try:
        with open(filename, "wb") as f:
            f.write(proxy.download_file(filename).data)
        print "Downloaded", filename
    except:
        print "File", filename, "not found"


def handle_listing(proxy):
    LOG.info("Starting file listing.")
    # Use RPC proxy and get the list of files on server
    files = proxy.list_files()
    print "Files in server: ", files


def handle_upload(proxy, filename):
    LOG.info("Starting upload for file: %s." % filename)
    # Use RPC proxy and initialize the upload
    try:
        with open(filename, "rb") as f:
            proxy.upload_file(filename, f.read())
        print "Uploaded", filename
    except:
        print "File", filename, "not found"


def handle_delete(proxy, filename):
    LOG.info("Deleting file: %s." % filename)
    # Use RPC proxy and delete the file on server
    if proxy.delete_file(filename):
        print "File", filename, "deleted"
    else:
        print "File", filename, "not found"


def handle_move(proxy, oldfile, newfile):
    LOG.info("Move file: %s -> %s." % (oldfile, newfile))
    # Use RPC proxy and move (rename) the file
    if proxy.rename_file(oldfile, newfile):
        print "File", oldfile, "renamed"
    else:
        print "File", oldfile, "not found"


if __name__ == "__main__":
    parser = ArgumentParser(description="Client for uploading/listing files.")
    parser.add_argument('-a', '--server-addr', help="Address of the host. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-u', '--upload', help="File to be uploaded.", nargs=1)
    parser.add_argument('-l', '--list', help="List all the files in the server.", action='store_true')
    parser.add_argument('-d', '--download', help="Download specified file.", nargs=1)
    parser.add_argument('-r', '--remove', help="Remove specified file.", nargs=1)
    parser.add_argument('-m', '--move', help="Move specified file.", nargs=2)
    args = parser.parse_args()
    main(args)
