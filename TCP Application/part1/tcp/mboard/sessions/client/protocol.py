# Implements message board protocol on TCP (client-side)
# in this protocol client's can send a big messages (delivered by TCP)
# Therefore there is no need to additionally implement sessions.
#
# Also as we can now send big messages we do no need to split the
# "get last N messages" routine into 2 sub routines, like we did for UDP.
#
# Client(c) <-----------> Server requests/responses
#
#   publish(M) --0:M---->|
#      |                 | mboard.put(M,c)
#      | <------OK-------|
#
#   last(N) ---1:N------>|
#      |                 | if int(N):
#      |                 |     iDs = mboard.last(N)
#      | <----- iDs -----|     msgs = map(mboard.get, iDs)
#      | <-----ERR-------| else
#
#------------------------------------------------------------------------------
'''
MBoard Protocol Client-Side (TCP)
Created on Aug 23, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from tcp.mboard.sessions.common import  __REQ_PUBLISH,\
     __RSP_OK, __REQ_GET_N_LAST, __RSP_ERRTRANSM, __RSP_CANT_CONNECT,\
     __CTR_MSGS, tcp_send, tcp_receive, MBoardProtocolError, __MSG_FIELD_SEP,\
     __ERR_MSGS
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as soc_err
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Protocol'
___VER = '0.1.0.0'
___DESC = 'State-less Message Board Protocol Client-Side (TCP version)'
___BUILT = '2016-09-13'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Static functions ------------------------------------------------------------
def __disconnect(sock):
    '''Disconnect from the server, close the TCP socket
    @param sock: TCP socket to close
    @param srv: tuple ( string:IP, int:port ), server's address
    '''
    # Usually we do not need separate method for just closing the socket
    # Here we do it because we can close socket in multiple place down in
    # __request method ... and we don not want to copy paste all the LOGs

    # Check if the socket is closed disconnected already ( in case there can
    # be no I/O descriptor
    try:
        sock.fileno()
    except soc_err:
        LOG.debug('Socket closed already ...')
        return

    # Closing RX/TX pipes
    LOG.debug('Closing client socket ...')
    # Close socket, remove I/O descriptor
    sock.close()
    LOG.info('Disconnected from server')

def __request(srv,r_type,args):
    '''Send request to server, receive response
    @param srv: tuple ( IP, port ), server socket address
    @param r_type: string, request type
    @param args: list, request parameters/data
    @returns tuple ( string:err_code, list:response arguments )
    '''

    # Declaring TCP socket
    sock = socket(AF_INET,SOCK_STREAM)
    LOG.debug('Client socket created, descriptor %d' % sock.fileno())

    # Try connect to server
    try:
        sock.connect(srv)
    except soc_err as e:
        # In case we failed to connect to server, we should report error code
        LOG.error('Can\'t connect to %s:%d, error: %s' % (srv+(e,)))
        return __RSP_CANT_CONNECT,[str(e)]
    LOG.info('Client connected to %s:%d' % srv)
    LOG.debug('Local TCP socket is bound on %s:%d' % sock.getsockname())

    # If we are connected
    # Envelope the request
    req = __MSG_FIELD_SEP.join([r_type]+map(str,args))
    LOG.debug('Will send [%s] request, total size [%d]'\
              '' % (__CTR_MSGS[r_type], len(req)))

    # Try to Send request using TCP
    n = 0   # Number of bytes sent
    try:
        n = tcp_send(sock, req)
    except soc_err as e:
        # In case we failed in the middle of transfer we should report error
        LOG.error('Interrupted sending the data to %s:%d, '\
                    'error: %s' % (sock+(e,)))
        # ... and close socket
        __disconnect(sock)
        return __RSP_ERRTRANSM,[str(e)]

    LOG.info('Sent [%s] request, total bytes sent [%d]'\
             '' % (__CTR_MSGS[r_type], n))

    # We assume if we are here we succeeded with sending, and
    # we may start receiving
    rsp = None
    try:
        rsp = tcp_receive(sock)
    except (soc_err, MBoardProtocolError) as e:
        # In case we failed in the middle of transfer we should report error
        LOG.error('Interrupted receiving the data from %s:%d, '\
                  'error: %s' % (srv+(e,)))
        # ... and close socket
        __disconnect(sock)
        return __RSP_ERRTRANSM,[str(e)]

    # We assume if we are here we succeeded with receiving, and
    # we may close the socket and check the response
    LOG.debug('Received response [%d bytes] in total' % len(rsp))
    __disconnect(sock)

    # Check error code
    r_data = rsp.split(__MSG_FIELD_SEP)
    err,r_args = r_data[0],r_data[1:] if len(r_data) > 1 else []
    if err != __RSP_OK:
        if err in __ERR_MSGS.keys():
            LOG.error('Server response code [%s]: %s' % (err,__ERR_MSGS[err]))
        else:
            LOG.error('Malformed server response [%s]' % err)

    return err,r_args

def publish(srv,m):
    '''Publish message
    @param src: tuple ( IP, port ), server socket address
    @param m: string, message to publish, maximal length 2^16-32-2 bytes
    @returns True if successfully published, else False
    '''
    # Try converting to utf-8
    msg = m.encode('utf-8')
    # Sending request
    err,_ = __request(srv, __REQ_PUBLISH, [msg])
    return err == __RSP_OK

def last(srv,n):
    '''Get last n messages
    @param src: tuple ( IP, port ), server socket address
    @param n: int, last n messages
    @returns list [ tuple ( int: time seconds since UNIX epoch,
                     str:IP, int:port, str:message ) ... ]
    '''
    err,msgs = __request(srv, __REQ_GET_N_LAST, [n])
    return msgs if err == __RSP_OK else []
