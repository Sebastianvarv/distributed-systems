# Implements simple sessions between client and server on top of UDP
#
# Supplementary to MBoard protocol versions 0.0.1.x
#
# In MBoard versions O.0.0.x we had PDUs (messages) never
# longer than then UDP packet's maximal length. Now we eliminate this
# disadvantage: the MBoards PDU can easily exceed the 2^16 bytes and
# therefore should be split and sent in multiple UDP packets. On server-side
# the message must then be first assembled from the packets before processing.
# We also need to ensure all packets have arrived and that the order is also
# correct. Introducing session will add another control layer in addition
# request/response control codes. Here however the message delivery is
# controlled and nothing else (the MBoard functions are still in separate
# control layer - protocol.py).
#
#             Client(c) <-----------> Server session
#
#                 opensess() ------------> | sess_id = new uuid()
#                        | <---sess_id ----| S[sess_id] = []
#
#                 sendblock(D,sess_id)     |
#                        |                 |
# blocks = D.split(size) |                 |
# count = len(blocks)`   |                 |
# for i in range(count): |                 |
#     b = blocks[i]      |                 |
#     l = len(b)         |                 |
#                  --------(for loop)-------------------
#                        | -- [ sess_id, ->|
#                        | i,count, l, b ] |
#                        |                 | if len(b) == l:
#                        |                 |   S[sess_id].put((i,count),(l,b))
#       send next block  | < ---- OK ------|
#                        |                 | else
# re-send current block  | < ----NOK ------|
#                  --------(end for loop)---------------
#        close session   | ---[ sess_id ]->| M.append(getM(S[sess_id])
#                        |                 | S.remove(sess_id)
#                        | <------OK-------|
#
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
from udp.mboard.sessions.common import __SESS_REQ_NEW, __SESS_REQ_SEND_BLOCK, \
    __SESS_REQ_CLOSE, __SESS_RSP_OK, __SESS_RSP_RETRANS, __SESS_RSP_BADFORMAT, \
    __SESS_FIELD_SEP, __SESS_MAX_PDU, __SESS_ERR_MSG, __MSG_FIELD_SEP, __RSP_OK

# Constants -------------------------------------------------------------------
___NAME = 'Sessions Protocol'
___VER = '0.0.0.1'
___DESC = 'Simple Sessions protocol (server-side)'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Private variables -----------------------------------------------------------
__M = []  # Received messages (array of tuples like ( ( ip, port), data)
__S = {}  # Sessions
__sess_id_counter = 0


# Private functions -----------------------------------------------------------
def __request(s, client, r_type, args):
    '''Send request to server, receive response
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param r_type: string, request type
    @param args: list, request parameters/data
    '''
    # Envelope request (prepare data unit)
    m = __SESS_FIELD_SEP.join([r_type] + map(str, args))
    # Send
    s.sendto(m, client)
    source = None
    while source != client:
        try:
            # Try receive a response
            r, source = s.recvfrom(__SESS_MAX_PDU)
        except KeyboardInterrupt:
            LOG.info('Ctrl+C issued, terminating ...')
            s.close()
            exit(0)
        # In case unexpected message was received
        if source != client:
            LOG.debug('Unknown message origin %s:%d' % source)
            LOG.debug('Expected %s:%d' % client)
    # Check error code
    r_data = r.split(__SESS_FIELD_SEP)
    err, r_args = r_data[0], r_data[1:] if len(r_data) > 1 else []
    if err != __SESS_RSP_OK:
        if err in __SESS_ERR_MSG.keys():
            LOG.error('Error: server response code [%s]' % err)
            LOG.error(__SESS_ERR_MSG[err])
        else:
            LOG.error('Malformed server response [%s]' % err)
    return err, r_args

def __new_session(source):
    '''Create new session, give it unique iD
    @param source: tuple ( ip, port ), socket address of the session originator
    @returns int, new session iD
    '''
    global __sess_id_counter
    global __S
    uuid = __sess_id_counter
    __sess_id_counter += 1
    __S[source + (uuid,)] = {}
    return uuid


def __store_session_block(head, block, source):
    '''Store received block
    @param head: tuple ( int:sess_id, int:i, int:count, int:l ), block header
    @param block: str, block data
    @param source: tuple ( ip, port ), socket address of the session originator
    @returns int, number of blocks currently received in session
    '''
    global __S
    sess_id, i, count, _ = head
    __S[source + (sess_id,)][(i, count)] = block
    return len(__S[source + (sess_id,)].keys())


def __retrieve_message(sess_id, source):
    '''Get the full message delivered in the scope of a session
    @param sess_id: int, iD of a session transmitting a message
    @param source: tuple ( ip, port ), socket address of the session originator
    @returns str, full message
    '''
    global __S
    # Get all the blocks ordered
    sess = __S.pop(source + (sess_id,))
    blocks = map(lambda x: x[0] + (x[1],), sess.items())
    del sess
    blocks.sort(key=lambda x: x[0])
    # Check count
    if len(blocks) != blocks[0][1]:
        # If this happens - client probably wants to interrupt incomplete
        # session
        LOG.debug('Interrupting incomplete session, %d blocks complete, ' \
                  '%d expected' % (len(blocks), blocks[0][1]))
        return None
    return ''.join(map(lambda x: x[-1], blocks))


# Public functions ------------------------------------------------------------
def process_session(block, source):
    '''Process the session block, assemble the message
    @param block: string, a piece of bigger message
    @param source: tuple ( ip, port ), client's socket address
    @returns string, response to send to client
    '''
    global __M
    LOG.debug('Received block length %d' % len(block))
    if len(block) < 2:
        LOG.debug('Not enough data received from %s ' % source)
        return __SESS_RSP_BADFORMAT
    # Declare new session
    if block.startswith(__SESS_REQ_NEW + __SESS_FIELD_SEP):
        sess_id = __new_session(source)
        LOG.debug('New session [%d] initiated with ' \
                  ' %s:%d' % ((sess_id,) + source))
        return __SESS_FIELD_SEP.join(map(str, [__SESS_RSP_OK, sess_id]))
    # Receive a new block
    if block.startswith(__SESS_REQ_SEND_BLOCK + __SESS_FIELD_SEP):
        parts = block.split(__SESS_FIELD_SEP)
        if len(parts) < 6:
            LOG.degug('Malformed received from %s ' % source)
            return __SESS_RSP_BADFORMAT
        head, data = parts[1:5], __SESS_FIELD_SEP.join(parts[5:])
        LOG.debug('New block [head:%s] received ' \
                  'from %s:%d' % ((str(head),) + source))
        # Parse header
        try:
            head = map(int, head)
            sess_id, i, count, l = head
        except ValueError:
            LOG.debug('No numeric data in block header [%s]' % (str(head)))
            return __SESS_RSP_BADFORMAT
        LOG.info('Session %d: Received block %d/%d ' \
                 'size %d' % (sess_id, i, count, l))
        # Check block
        if len(data) != l:
            # Incomplete block
            LOG.info('Session %d: block %d/%d incomplete size ' \
                     '%d of %d' % (sess_id, i, count, len(data), l))
            return __SESS_RSP_RETRANS
        # Store block
        n = __store_session_block(head, data, source)
        LOG.info('Session %d: %d/%d blocks received successfully' \
                 '' % (sess_id, n, count))
        return __SESS_FIELD_SEP.join(map(str, [__SESS_RSP_OK, n]))
    # Close session
    if block.startswith(__SESS_REQ_CLOSE + __SESS_FIELD_SEP):
        parts = block.split(__SESS_FIELD_SEP)
        if len(parts) < 2:
            LOG.degug('Malformed received from %s ' % source)
            return __SESS_RSP_BADFORMAT
        try:
            sess_id = int(parts[1])
        except ValueError:
            LOG.debug('No numeric data in control code [%s]' % parts[1])
            return __SESS_RSP_BADFORMAT
        # Retrieve full message, store it, clean session
        message = __retrieve_message(sess_id, source)
        if message == None:
            LOG.info('Session %d: interrupted by client %s:%d' \
                     '' % ((sess_id,) + source))
            return __SESS_FIELD_SEP.join(map(str, [__SESS_RSP_OK, 0]))
        LOG.debug('Received new message, size %d from %s:%d' \
                  '' % ((len(message),) + source))
        __M.append((source, message))
        return __SESS_FIELD_SEP.join(map(str, [__SESS_RSP_OK, 1]))


def checkincoming():
    '''Check if any message was delivered into M
    @returns: int, number messages in M
    '''
    global __M
    return len(__M)


def getincoming():
    '''Get the first message added to M
    @returns: tuple ( ( str:ip, int:port ), msg ) first message added to M
    '''
    global __M
    source, m = __M.pop(0)
    return m, source

def __calculate_blocksize(sess_id, msg_len, max_pdu=__SESS_MAX_PDU):
    '''Calculate the block size for splitting message into blocks, try to
    achieve block size close to maximal PDU of the session protocol
    @param: sess_id: int, session iD
    @param: msg_len: int, length of the message
    @returns: tuple ( int:b_count, int:b_length )
    '''
    b_count = 0
    b_size = max_pdu
    delta = b_size
    while delta > 0:
        b_count = msg_len / b_size
        b_count = b_count + 1 if (msg_len - b_count * b_size) > 0 else b_count
        # Total count of space to reserve block header
        # Space for session id +
        # Space for blocks counting +
        # Space for block size
        # Space for separators

        digits = \
            len(str(sess_id)) + \
            (len(str(b_count)) + 1) * 2 + \
            len(str(b_size)) + \
            4
        # Adjust the block size using block header length +2 for control code
        delta = (b_size + digits + 2) - max_pdu
        b_size = b_size - delta
    return (b_count, b_size)

def split_data_to_blocks(data, max_pdu=__SESS_MAX_PDU):
    input_data = data.encode()
    blocks = []
    while len(input_data) > 0:
        if len(input_data) > max_pdu:
            blocks.append(input_data[:max_pdu])
            input_data = input_data[max_pdu:]
        else:
            blocks.append(input_data)
            input_data = []

    return blocks



def __sendblock(sock, client, head, block):
    '''Send block to the client
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @param: head: tuple ( int:sess_id, int:i, int:count, int:l ), block header
    @param: block: str, block data
    @returns: Number of successfully transmitted blocks in sequence
    '''
    err = __SESS_RSP_RETRANS
    while err == __SESS_RSP_RETRANS:
        err, args = __request(sock, client, __SESS_REQ_SEND_BLOCK, \
                              list(head) + [block])
    if err != __SESS_RSP_OK or len(args) < 1:
        LOG.error('No arguments in server\'s response, integer ' \
                  'expected')
        return -1
    # Parse integer
    try:
        n = int(args[0])
    except ValueError:
        LOG.error('Can\'t parse integer from a server response: '
                  '%s' % args[0])
        return -1
    return n

def __closesession(sock, client, sess_id):
    '''Send block to the server
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @param: sess_id: int, session iD to close
    @returns int, number of full messages delivered
    '''
    err, args = __request(sock, client, __SESS_REQ_CLOSE, [sess_id])
    if err != __SESS_RSP_OK or len(args) < 1:
        LOG.error('No arguments in server\'s response, integer ' \
                  'expected')
        return -1
    # Parse integer
    try:
        n = int(args[0])
    except ValueError:
        LOG.error('Can\'t parse integer from a server response: '
                  '%s' % args[0])
        return -1
    return n

def send_session_and_block_len(client, data):
    # init session
    global __S
    s_id = __new_session(client)

    if s_id == None:
        LOG.error('Can not open new session for sending')
        return 0

    count, size = __calculate_blocksize(s_id, len(data.encode()))
    blocks = split_data_to_blocks(data)
    LOG.debug("splitted data %s" % str(blocks))

    LOG.debug("Block count: %d" % count)
    LOG.debug("Block count splited: %d" % len(blocks))
    assert count == len(blocks)

    __S[s_id] = blocks

    LOG.debug("Send session and block session id %s" % s_id)
    LOG.debug("Send session and block session count %s" % count)

    response_data = [__RSP_OK, str(s_id), str(count)]
    r = __MSG_FIELD_SEP.join(response_data)
    return r


def get_block(s_id, block_n):
    global __S
    return __S[s_id][block_n]

def finish_download(s_id):
    global __S
    __S.pop(s_id, None)