# Implements message board protocol with sessions
# in this protocol client's can send a big messages (in multiple UDP packets).
# Therefore we need to introduce sessions, please refer to sessions.py
#
# When sending the board contents back to client however, the
# ID of the corresponding message are sent first, then the client
# asks messages one by one using IDs.
#
# Client(c) <-----------> Server requests/responses
#
#   publish(M) --0:M---->|
#      |                 | mboard.put(M,c)
#      | <------OK-------|
#
#   last(N) ---1:N------>|
#      |                 | if int(N):
#      | <----- iDs -----|     iDs = mboard.last(N)
#      | <-----ERR-------| else
#
#    get(id) ---2:id---->|
#      |                 | if int(id):
#      | <----- M -------|     M = mboard.get(id)
#      | <------ ERR ----| else
#
# ------------------------------------------------------------------------------
'''
Created on Aug 23, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from udp.mboard.sessions.common import __REQ_PUBLISH, __MSG_FIELD_SEP, \
    __RSP_OK, __REQ_LAST, __REQ_GET, __RSP_ERRTRANSM, __REQ_GET_DATA
from udp.mboard.sessions.client.sessions import send_data, receive_data

# Constants -------------------------------------------------------------------
___NAME = 'MBoard Protocol'
___VER = '0.0.1.2'
___DESC = 'State-less Message Board Protocol Client-Side'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'


# Static functions ------------------------------------------------------------
def __request(sock, srv, r_type, args):
    '''Send request to server, receive response
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param r_type: string, request type
    @param args: list, request parameters/data
    '''
    # Envelope request (prepare data unit)
    m = __MSG_FIELD_SEP.join([r_type] + map(str, args))
    # Send/Receive using sessions
    n = send_data(sock, srv, m)
    # @TODO: Receive using sessions
    #     source = None
    #     while source != srv:
    #         try:
    #             # Try receive a response
    #             r,source = s.recvfrom(protocol.MAX_DATAUNIT_SIZE)
    #         except KeyboardInterrupt:
    #             __err('Ctrl+C issued, terminating ...')
    #             sock.close()
    #             exit(0)
    #         # In case unexpected message was received
    #         if source != srv:
    #             print 'Unknown message origin %s:%d' % source
    #             print 'Expected %s:%d' % srv
    # Check error code
    # @TODO: When sessions receive is implemented, rewrite this properly
    #     r_data = r.split(protocol.__MSG_FIELD_SEP)
    #     err,r_args = r_data[0],r_data[1:] if len(r_data) > 1 else []
    #     if err != protocol.__RSP_OK:
    #         if err in protocol.__ERR_MSGS.keys():
    #             __err('Error: server response code [%s]' % err)
    #             __err(protocol.__ERR_MSGS[err])
    #         else:
    #             __err('Malformed server response [%s]' % err)

    LOG.debug("Client protocol request, trying to receive data from %s" % str(srv))
    err, r = receive_data(sock, srv)

    # err = __RSP_OK if n > 0 else __RSP_ERRTRANSM
    return err, r


def publish(sock, srv, m):
    '''Publish message
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param m: string, message to publish, maximal length 2^16-32-2 bytes
    @returns True if successfully published, else False
    '''

    LOG.debug("Client published message %s" % m)
    # Try converting to utf-8
    msg = m.encode('utf-8')
    # Sending request
    err, _ = __request(sock, srv, __REQ_PUBLISH, [msg])
    LOG.debug("Response from publish %s" % str(err))
    return err == __RSP_OK


def last(sock, srv, n):
    '''Get iDs of last n messages
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param n: int, last n messages
    @returns list [ int, int .. int ], iDs of last n messages
    '''
    err, ids = __request(sock, srv, __REQ_LAST, [n])
    return ids if err == __RSP_OK else []


def get(sock, srv, m_id):
    '''Get message by iD
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param m_id: int, message unique id
    @returns tuple ( int: time seconds since UNIX epoch,
                     str:IP, int:port, str:message )
    '''
    err, m = __request(sock, srv, __REQ_GET, [m_id])
    m = m[:3] + [__MSG_FIELD_SEP.join(m[3:])]
    return m if err == __RSP_OK else None


def unread_messages(sock, srv):
    err, data = __request(sock, srv, __REQ_GET_DATA)
    return data if err == __RSP_OK else None
