Files rpc_file_client.py and rpc_file_server.py contain client
and server side of RPC file server which is capable of listing,
uploading, downloading, renaming and removing files.

I did add threading explicitly since SimpleXMLRPCServer is
implemented as single-threaded application. This can be verified by uploading and
downloading files simultaneously without using threads. I did use
SocketServer ThreadingMixIn to enable multi threading.
