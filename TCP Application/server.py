import ctypes
import os
import os.path
import platform
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR

from common import __REQ_SEND_FILENAME_AND_SIZE, __MSG_FIELD_SEP, __RSP_FILEEXISTS, __RSP_OK, __RSP_DISKSPACE_ERR


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


def get_free_space_byte(dirname):
    """Return folder/drive free space (in megabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize


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
        try:
            print 'Server is listening new connections on %s:%d' % s.getsockname()

            # Wait for a client to connect
            client_socket, client_addr = s.accept()
            print 'Client connected from :', client_addr

            received_msg = client_socket.recv(1024)
            header, msg = received_msg.split(__MSG_FIELD_SEP, 1)

            # Parse headers
            if header == __REQ_SEND_FILENAME_AND_SIZE:
                filename, filesize = msg.split(__MSG_FIELD_SEP, 1)
                if file_exists(filename, dumpdir):
                    client_socket.send(__RSP_FILEEXISTS)
                else:
                    if get_free_space_byte(dumpdir) < int(filesize):
                        print "Not enough space on disk"
                        client_socket.send(__RSP_DISKSPACE_ERR)
                    else:
                        client_socket.send(__RSP_OK)
                        download_file(dumpdir, filename, client_socket)
                        print "Downloaded file: ", filename
        except KeyboardInterrupt:
            # Close the sesion
            # client_socket.close()
            print 'Closed client socket...'
            s.shutdown(SHUT_WR)
            s.close()
            print 'Closed the listener socket ...'
            print 'Terminating ...'
            break
