# Implements message board protocol on TCP (server-side)
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
MBoard Protocol Server-Side (TCP)
Created on Aug 19, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from exceptions import ValueError # for handling number format exceptions
from tcp.mboard.sessions.common import __RSP_BADFORMAT,\
     __REQ_PUBLISH, __MSG_FIELD_SEP, __RSP_OK, __REQ_LAST,\
     __REQ_GET, __RSP_MSGNOTFOUND, __RSP_UNKNCONTROL, __REQ_GET_N_LAST
from socket import error as soc_err
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Protocol'
___VER = '0.1.0.0'
___DESC = 'State-less Message Board Protocol Server-Side (TCP version)'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Static functions ------------------------------------------------------------
def __disconnect_client(sock):
    '''Disconnect the client, close the corresponding TCP socket
    @param sock: TCP socket to close (client socket)
    '''

    # Check if the socket is closed disconnected already ( in case there can
    # be no I/O descriptor
    try:
        sock.fileno()
    except soc_err:
        LOG.debug('Socket closed already ...')
        return

    # Closing RX/TX pipes
    LOG.debug('Closing client socket')
    # Close socket, remove I/O descriptor
    sock.close()
    LOG.info('Disconnected client')

def server_process(board,message,source,oldprotocol=False):
    '''Process the client's message, modify the board if needed
        @param board: active message board (static lib.)
        @param message: string, protocol data unit received from client
        @param source: tuple ( ip, port ), client's socket address
        @param oldprotocol: backward compatibility flag (for 0.0.0.x clients)
        @returns string, response to send to client
    '''
    LOG.debug('Received request [%d bytes] in total' % len(message))
    if len(message) < 2:
        LOG.degug('Not enough data received from %s ' % message)
        return __RSP_BADFORMAT
    LOG.debug('Request control code (%s)' % message[0])
    if message.startswith(__REQ_PUBLISH + __MSG_FIELD_SEP):
        msg = message[2:]
        LOG.debug('Client %s:%d will publish: '\
            '%s' % (source+((msg[:60]+'...' if len(msg) > 60 else msg),)))
        m_id = board.publish(msg,source)
        LOG.info('Published new message, uuid: %d' % m_id)
        return __RSP_OK
    elif message.startswith(__REQ_LAST + __MSG_FIELD_SEP):
        s = message[2:]
        try:
            n = int(s)
            LOG.debug('New message listing request from %s:%d, '\
                      'messages %d' % (source+(n,)))
        except ValueError:
            LOG.debug('Integer required, %s received' % s)
            return __RSP_BADFORMAT
        ids = board.last(n)
        LOG.debug('Last %d ids: %s ' % (n,','.join(map(str,ids))))
        return __MSG_FIELD_SEP.join((__RSP_OK,)+tuple(map(str,ids)))
    elif message.startswith(__REQ_GET + __MSG_FIELD_SEP):
        s = message[2:]
        try:
            m_id = int(s)
            LOG.debug('New message request by id from %s:%d, '\
                      'id %d' % (source+(m_id,)))
        except ValueError:
            LOG.debug('Integer required, %s received' % s)
            return __RSP_BADFORMAT
        m = board.get(m_id)
        if m == None:
            LOG.debug('No messages by iD: %d' % m_id)
            return __RSP_MSGNOTFOUND
        m = map(str,m)
        return __MSG_FIELD_SEP.join((__RSP_OK,)+tuple(m))
    elif message.startswith(__REQ_GET_N_LAST + __MSG_FIELD_SEP):
        s = message[2:]
        try:
            n = int(s)
            LOG.debug('Client %s:%d requests %s last'\
                      'messages' % (source+('all' if n <= 0 else '%d' % n,)))
        except ValueError:
            LOG.debug('Integer required, %s received' % s)
            return __RSP_BADFORMAT
        # Get last N ids
        ids = board.last(n)
        # Get messages by ids
        msgs = map(board.get,ids)
        # Turn everything to string, use space to separate message meta-info
        #  [ "<timestamp> <ip> <port> <message>", ... ]
        msgs = map(lambda x: ' '.join(map(str,x)),msgs)
        return __MSG_FIELD_SEP.join((__RSP_OK,)+tuple(msgs))
    else:
        LOG.debug('Unknown control message received: %s ' % message)
        return __RSP_UNKNCONTROL
