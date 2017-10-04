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
Message board protocol with sessions
Created on Aug 19, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from exceptions import ValueError  # for handling number format exceptions
from udp.mboard.sessions.common import __RSP_BADFORMAT, \
    __CTR_MSGS, __REQ_PUBLISH, __MSG_FIELD_SEP, __RSP_OK, __REQ_LAST, \
    __REQ_GET, __RSP_MSGNOTFOUND, __RSP_UNKNCONTROL, \
    MAX_PDU_SIZE_OLD_PROTO, __REQ_HAS_MESSAGES, __REQ_GET_MESSAGES, __REQ_GET_BLOCK, __SESS_FIELD_SEP, __SESS_RSP_OK, __REQ_DOWNLOAD_FINISHED
from sessions import get_block, finish_download

# Constants -------------------------------------------------------------------
___NAME = 'MBoard Protocol'
___VER = '0.0.1.2'
___DESC = 'State-less Message Board Protocol Server-Side'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'


# Static functions ------------------------------------------------------------
def server_process(board, message, source, oldprotocol=False):
    '''Process the client's message, modify the board if needed
        @param board: active message board (static lib.)
        @param message: string, protocol data unit received from client
        @param source: tuple ( ip, port ), client's socket address
        @param oldprotocol: backward compatibility flag (for 0.0.0.x clients)
        @returns string, response to send to client
    '''
    LOG.debug("###### RECEIVED REQUEST ######")
    LOG.debug('Received message length %d' % len(message))
    if len(message) < 2:
        LOG.debug('Not enough data received from %s ' % message)
        return __RSP_BADFORMAT
    LOG.debug('Message control code (%s) ' \
              '%s ' % (message[0], __CTR_MSGS[message[0]]))
    if message.startswith(__REQ_PUBLISH + __MSG_FIELD_SEP):
        msg = message[2:]
        LOG.debug('New message to publish from %s:%d, ' \
                  'msg: %s' % (source + ((msg[:60] + '...' if len(msg) > 60 else msg),)))
        m_id = board.publish(msg, source)
        LOG.info('Published new message, uuid: %d' % m_id)
        return __RSP_OK
    elif message.startswith(__REQ_LAST + __MSG_FIELD_SEP):
        s = message[2:]
        try:
            n = int(s)
            LOG.debug('New message listing request from %s:%d, ' \
                      'messages %d' % (source + (n,)))
        except ValueError:
            LOG.debug('Integer required, %s received' % s)
            return __RSP_BADFORMAT
        ids = board.last(n)
        LOG.debug('Last %d ids: %s ' % (n, ','.join(map(str, ids))))
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(map(str, ids)))
    elif message.startswith(__REQ_GET + __MSG_FIELD_SEP):
        s = message[2:]
        try:
            m_id = int(s)
            LOG.debug('New message request by id from %s:%d, ' \
                      'id %d' % (source + (m_id,)))
        except ValueError:
            LOG.debug('Integer required, %s received' % s)
            return __RSP_BADFORMAT
        m = board.get(m_id)
        m = map(str, m)
        if oldprotocol:
            # too bad here will lose some of the message trail in
            # respect of the header, but this only affects long messages
            # client should be aware of it and not let publishing messages
            # which are close to maximal PDU size

            msg_info_size = sum(map(len, m[:3])) + len(m[:3])
            # +2 For control code
            if (len(m[3]) + msg_info_size + 2) > MAX_PDU_SIZE_OLD_PROTO:
                offset = MAX_PDU_SIZE_OLD_PROTO - (msg_info_size + 2)
                m = m[:3] + [m[3][:offset]]
                LOG.info('Big message was cut, %d trailing bytes removed' % offset)
                LOG.info('Upgrade client code to protocol 0.0.1.x!')
        LOG.debug('Message id %d, msg size: [%d]' % (m_id, len(' '.join(m))))
        if m == None:
            LOG.debug('No messages by iD: %d' % m_id)
            return __RSP_MSGNOTFOUND
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(m))

    elif message.startswith(__REQ_HAS_MESSAGES + __MSG_FIELD_SEP):
        n_msg = board.get_size()
        LOG.debug("Number of messages in server.protocol: %d" % n_msg)
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(map(str, [n_msg])))

    elif message.startswith(__REQ_GET_MESSAGES + __MSG_FIELD_SEP):
        msg_board = board.get_all_unread()
        LOG.debug("All of the messages %s" % msg_board)
        msg_list = []
        for msg in msg_board:
            msg_list.append(msg_board[msg][4])
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(map(str, msg_list)))

    elif message.startswith(__REQ_GET_BLOCK + __SESS_FIELD_SEP):
        LOG.debug("Message in server protocol get_block: %s" % str(message))
        parts = message.split(__SESS_FIELD_SEP)
        s_id = int(parts[1])
        block_n = int(parts[2])

        return_value = get_block(s_id, block_n)
        return __SESS_FIELD_SEP.join((__SESS_RSP_OK,) + tuple(map(str, return_value)))

    elif message.startswith(__REQ_DOWNLOAD_FINISHED + __SESS_FIELD_SEP):
        parts = message.split(__SESS_FIELD_SEP)
        finish_download(int(parts[1]))

        return __SESS_RSP_OK + __SESS_FIELD_SEP

    else:
        LOG.debug('Unknown control message received: %s ' % message)
        return __RSP_UNKNCONTROL
