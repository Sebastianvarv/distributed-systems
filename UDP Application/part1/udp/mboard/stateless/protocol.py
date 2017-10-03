# Implements state-less message board protocol
# in this protocol we assume the client never sends the
# message in multiple UDP packets, long text is sent
# in separate lines -> separate messages,
# one client's message -> one UDP packet.
#
# When sending the board contents back to client however, the
# ID of the corresponding message are sent first, then the client
# asks messages one by one using IDs.
#
# Client(c) <-----------> Server requests
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
State-less message board protocol
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
import time
import datetime

# Constants -------------------------------------------------------------------
___NAME = 'MBoard Protocol'
___VER = '0.0.0.3'
___DESC = 'State-less Message Board Protocol'
___BUILT = '2016-08-19'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Protocol Data Unit Size -----------------------------------------------------
MAX_DATAUNIT_SIZE = 2 ** 16 - 32  # Maximal UDP packet size without UDP header
# Requests --------------------------------------------------------------------
__REQ_PUBLISH = '1'
__REQ_LAST = '2'
__REQ_GET = '3'
__REQ_TIME = '4'
__REQ_REQUESTTIME = '5'

__CTR_MSGS = {__REQ_GET: 'Get message by id',
              __REQ_LAST: 'Get iDs of last N messages',
              __REQ_PUBLISH: 'Publish new message',
              __REQ_TIME: 'Get current timestamp',
              __REQ_REQUESTTIME: 'Get message delivery time'
              }
# Responses--------------------------------------------------------------------
__RSP_OK = '0'
__RSP_BADFORMAT = '1'
__RSP_MSGNOTFOUND = '2'
__RSP_UNKNCONTROL = '3'
__ERR_MSGS = {__RSP_OK: 'No Error',
              __RSP_BADFORMAT: 'Malformed message',
              __RSP_MSGNOTFOUND: 'Message not found by iD',
              __RSP_UNKNCONTROL: 'Unknown control code'
              }
# Field separator for sending multiple values ---------------------------------
__MSG_FIELD_SEP = ':'


# Static functions ------------------------------------------------------------
def server_process(board, message, source):
    '''Process the client's message, modify the board if needed
        @param board: active message board (static lib.)
        @param message: string, protocol data unit received from client
        @param source: tuple ( ip, port ), client's socket address
        @returns string, response to send to client
    '''
    shortmsgs = [__REQ_TIME, __REQ_REQUESTTIME]
    LOG.debug('Received message length %d' % len(message))

    if len(message) < 2 and message not in shortmsgs:
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
        # too bad here will lose some of the message trail in
        # respect of the header, but this only affects long messages
        # client should be aware of it and not let publishing messages
        # which are close to maximal PDU size
        m = map(str, m)
        msg_info_size = sum(map(len, m[:3])) + len(m[:3])
        # +2 For control code
        if (len(m[3]) + msg_info_size + 2) > MAX_DATAUNIT_SIZE:
            offset = msg_info_size + 2
            m = m[:3] + [m[3][:-offset]]
            LOG.info('Big message was cut, %d trailing bytes removed' % offset)
            LOG.error('Adjust the client\'s code not to let send messages of ' \
                      'size close to maximal PDU')
        LOG.debug('Message id %d, msg size: [%d]' % (m_id, len(' '.join(m))))
        if m == None:
            LOG.debug('No messages by iD: %d' % m_id)
            return __RSP_MSGNOTFOUND
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(m))

    elif message.startswith(__REQ_TIME):
        # Get time
        timestamp = time.time()
        ts = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(ts))

    elif message.startswith(__REQ_REQUESTTIME):
        # Get timetaken
        timestamp = time.time()
        return_time = board.publish(None, source)
        ts = return_time - timestamp
        print timestamp
        print return_time
        print ts
        return __MSG_FIELD_SEP.join((__RSP_OK,) + tuple(ts))

    else:
        LOG.debug('Unknown control message received: %s ' % message)
        return __RSP_UNKNCONTROL
