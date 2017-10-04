'''
Created on Aug 23, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
# Imports ---------------------------------------------------------------------
from sys import exit, stderr
from udp.mboard.sessions.common import __SESS_REQ_NEW, __SESS_FIELD_SEP, \
    __SESS_RSP_OK, __SESS_MAX_PDU, __SESS_ERR_MSG, __SESS_REQ_SEND_BLOCK, \
    __SESS_RSP_RETRANS, __SESS_REQ_CLOSE, __MSG_FIELD_SEP, __REQ_GET_BLOCK, __REQ_DOWNLOAD_FINISHED

# Constants -------------------------------------------------------------------
___NAME = 'Sessions Protocol'
___VER = '0.0.0.1'
___DESC = 'Simple Sessions protocol (client-side)'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'


# Client-side functions -------------------------------------------------------
# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)


def __err(m):
    stderr.write("Error: %s\n")


def __request(s, srv, r_type, args):
    '''Send request to server, receive response
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param r_type: string, request type
    @param args: list, request parameters/data
    '''
    # Envelope request (prepare data unit)
    m = __SESS_FIELD_SEP.join([r_type] + map(str, args))
    # Send
    s.sendto(m, srv)
    source = None
    while source != srv:
        try:
            # Try receive a response
            r, source = s.recvfrom(__SESS_MAX_PDU)
        except KeyboardInterrupt:
            LOG.info('Ctrl+C issued, terminating ...')
            s.close()
            exit(0)
        # In case unexpected message was received
        if source != srv:
            LOG.debug('Unknown message origin %s:%d' % source)
            LOG.debug('Expected %s:%d' % srv)
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


def __opensession(sock, srv):
    '''Ask server to open new session, retrieve session iD
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @returns: int, the new session iD given by a server
    '''
    err, args = __request(sock, srv, __SESS_REQ_NEW, [0])
    if err != __SESS_RSP_OK or len(args) < 1:
        LOG.error('No arguments in server\'s response, session iD ' \
                  'expected')
        return None
    # Parse integer
    try:
        sess_id = int(args[0])
    except ValueError:
        LOG.error('Can\'t parse session iD from a server response: '
                  '%s' % args[0])
        return None
    return sess_id


def __sendblock(sock, srv, head, block):
    '''Send block to the server
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @param: head: tuple ( int:sess_id, int:i, int:count, int:l ), block header
    @param: block: str, block data
    @returns: Number of successfully transmitted blocks in sequence
    '''
    err = __SESS_RSP_RETRANS
    while err == __SESS_RSP_RETRANS:
        err, args = __request(sock, srv, __SESS_REQ_SEND_BLOCK, \
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


def __closesession(sock, srv, sess_id):
    '''Send block to the server
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @param: sess_id: int, session iD to close
    @returns int, number of full messages delivered
    '''
    err, args = __request(sock, srv, __SESS_REQ_CLOSE, [sess_id])
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


def send_data(sock, srv, data):
    '''Send data to the server (using session)
    @param: sock: UDP socket
    @param: srv: tuple ( ip, port ), server socket address to refer to
    @param: m: bytes, data to send to server
    @returns: int, number of delivered messages
    '''
    LOG.debug('Sending data, size [%d] bytes to %s:%d' % ((len(data),) + srv))
    # Get session iD
    sess_id = __opensession(sock, srv)
    if sess_id == None:
        LOG.error('Can not open new session for sending')
        return 0
    LOG.debug('Session [%d] opened for sending' % sess_id)
    m_size = len(data)
    b_count, b_size = __calculate_blocksize(sess_id, m_size)
    LOG.debug('Will send %d blocks, maximal size [%d] bytes' \
              '' % (b_count, b_size))

    for i in range(b_count):
        l = (m_size - b_size * i) if i == b_count - 1 else b_size
        h = (sess_id, i, b_count, l)
        b = data[i * b_size:i * b_size + l]
        LOG.debug('Sending block header %s, block size %d bytes ' \
                  '' % (str(h), len(b)))
        c_sent = -1
        while c_sent <= 0:
            c_sent = __sendblock(sock, srv, h, b)

    # Close session, ensure message was received
    n = __closesession(sock, srv, sess_id)
    if n <= 0:
        LOG.error('Error closing session %d' % sess_id)
    return n


def receive_data(sock, srv):
    LOG.debug("Client sessions receive_data socket: %s" % str(sock))
    LOG.debug("Client sessions receive_data server: %s" % str(srv))
    source = None
    while source != srv:
        try:
            # Try receive a response
            r, source = sock.recvfrom(__SESS_MAX_PDU)
            LOG.debug("Client sessions received block: %s" % str(r))
        except KeyboardInterrupt:
            __err('Ctrl+C issued, terminating ...')
            sock.close()
            exit(0)
        # In case unexpected message was received
        if source != srv:
            print 'Unknown message origin %s:%d' % source
            print 'Expected %s:%d' % srv

    # Check error code
    r_data = r.split(__MSG_FIELD_SEP)
    LOG.debug('r_data is %s' % r_data)
    err, r_args = r_data[0], r_data[1:] if len(r_data) > 1 else []
    LOG.debug('Contents of err are %s' % err)
    if err != __SESS_RSP_OK:
        if err in __SESS_ERR_MSG.keys():
            __err('Error: server response code [%s]' % err)
            __err(__SESS_ERR_MSG[err])
        else:
            __err('Malformed server response [%s]' % err)
    return err, r_args

def send_close_session(sock, srv, s_id):
    err, resp = __request(sock, srv, __REQ_DOWNLOAD_FINISHED, [s_id])
    if err == __SESS_RSP_OK:
        return 1
    else:
        return None

def download_blocks(sock, srv, s_id, block_n):
    data = ""

    for i in range(int(block_n)):
        err, resp = __request(sock, srv, __REQ_GET_BLOCK, [int(s_id), i])
        resp_string = ''.join(resp)
        data += resp_string

    data = data.split(__SESS_RSP_OK + __MSG_FIELD_SEP)[1].split(":")
    send_close_session(sock, srv, s_id)
    return data