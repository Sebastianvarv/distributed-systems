#!/usr/bin/python
#
# Implements message board UDP client
#
# Simple command-line application
# Currently no interactive mode implemented, application does the request
# and dies. User has to provide the IP address of the server at least.
# Default behavior is to fetch all the messages from the Board and show them
# to the user. Refer to --help to get the details about the options.
#
# Current implementation considers all user input is by default in UTF-8, no
# additional encoding.
# -----------------------------------------------------------------------------
'''
Created on Aug 21, 2016

@author: devel
'''
# Needed imports ------------------ -------------------------------------------
from udp.mboard.stateless import protocol
from socket import socket, AF_INET, SOCK_DGRAM
from time import localtime, asctime, time
from argparse import ArgumentParser # Parsing command line arguments
from sys import exit, stderr,stdin
from os import linesep
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Client'
___VER = '0.0.0.2'
___DESC = 'Simple Message Board Client'
___BUILT = '2016-08-19'
___VENDOR = 'Copyright (c) 2016 DSLab'
# -----------------------------------------------------------------------------
__DEFAULT_SERVER_PORT = 7777
__DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
def __err(m):
    stderr.write("Error: %s\n")

def __request(sock,srv,r_type,args):
    '''Send request to server, receive response
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param r_type: string, request type
    @param args: list, request parameters/data
    '''
    # Envelope request (prepare data unit)
    m = protocol.__MSG_FIELD_SEP.join([r_type]+map(str,args))
    # Send
    s.sendto(m,srv)
    source = None
    while source != srv:
        try:
            # Try receive a response
            r,source = s.recvfrom(protocol.MAX_DATAUNIT_SIZE)
        except KeyboardInterrupt:
            __err('Ctrl+C issued, terminating ...')
            sock.close()
            exit(0)
        # In case unexpected message was received
        if source != srv:
            print 'Unknown message origin %s:%d' % source
            print 'Expected %s:%d' % srv
    # Check error code
    r_data = r.split(protocol.__MSG_FIELD_SEP)
    err,r_args = r_data[0],r_data[1:] if len(r_data) > 1 else []
    if err != protocol.__RSP_OK:
        if err in protocol.__ERR_MSGS.keys(err):
            __err('Error: server response code [%s]' % err)
            __err(protocol.__ERR_MSGS[err])
        else:
            __err('Malformed server response [%s]' % err)
    return err,r_args

def publish(sock,srv,m):
    '''Publish message
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param m: string, message to publish, maximal length 2^16-32-2 bytes
    @returns True if successfully published, else False
    '''
    max_size = protocol.MAX_DATAUNIT_SIZE-2 # Leaving spaces for control code
    # Try converting to utf-8
    m = m.encode('utf-8')
    msg = m[:max_size] if len(m) > max_size else m    # Cut off long message
    if msg != m:
        print 'Too big message provided, only first %d bytes will be published' % max_size
    # Sending request
    err,_ = __request(sock, srv, protocol.__REQ_PUBLISH, [msg])
    return err == protocol.__RSP_OK


def noPublish(sock,srv,m):
    # Sending request
    err, resp = __request(sock, srv, protocol.__REQ_REQUESTTIME, m)
    return resp if err == protocol.__RSP_OK else None


def last(sock,srv,n):
    '''Get iDs of last n messages
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param n: int, last n messages
    @returns list [ int, int .. int ], iDs of last n messages
    '''
    err,ids = __request(sock, srv, protocol.__REQ_LAST,[n])
    return ids if err == protocol.__RSP_OK else []

def get(sock,srv,m_id):
    '''Get message by iD
    @param sock: UDP socket, used to send/receive
    @param src: tuple ( IP, port ), server socket address
    @param m_id: int, message unique id
    @returns tuple ( int: time seconds since UNIX epoch,
                     str:IP, int:port, str:message )
    '''
    err,m = __request(sock, srv, protocol.__REQ_GET, [m_id])
    m = m[:3] + [protocol.__MSG_FIELD_SEP.join(m[3:])]
    return m if err == protocol.__RSP_OK else None

def getTime(sock,srv):
    err, time = __request(sock, srv, protocol.__REQ_TIME, '')
    time = ''.join(time[:13]) + ':' + ''.join(time[15:17]) + ':' + ''.join(time[19:])
    return time if err == protocol.__RSP_OK else None

def getRequestTime(sock,srv):
    err, time = __request(sock, srv, protocol.__REQ_REQUESTTIME, '')

    return

# Main method -----------------------------------------------------------------
if __name__ == '__main__':
    # Parsing arguments
    parser = ArgumentParser(description=__info(),
                            version = ___VER)
    parser.add_argument('-H','--host',\
                        help='Server INET address',\
                        required=True
                        )
    parser.add_argument('-p','--port', type=int,\
                        help='Server UDP port, '\
                        'defaults to %d' % __DEFAULT_SERVER_PORT, \
                        default=__DEFAULT_SERVER_PORT)
    parser.add_argument('-m','--message',\
                        help='Message to publish',\
                        default='')
    parser.add_argument('-l','--last', metavar='N', type=int,\
                        help='Get last N messages,'\
                        'defaults to "all"',\
                        default=0)
    parser.add_argument('-t','--time', action='store_true')
    parser.add_argument('-rt', '--requesttime', action='store_true')
    args = parser.parse_args()
    # Declare client socket
    s = socket(AF_INET,SOCK_DGRAM)
    server = (args.host,int(args.port))  # Server's socket address

    m = args.message # Message to publish
    if m == '-':
        # Read m from STDIN
        m = stdin.readline()
        m = m.split(linesep)[0]

    # Parse integer
    n = int(args.last)  # Last n messages to fetch

    ids = []
    msgs = []

    if len(m) > 0:
        if publish(s, server, m):
            print 'Message published'

    # Query messages
    if n > 0:
        ids += last(s,server,n)

    if len(ids) > 0:
        msgs += map(lambda x: get(s,server,x), ids)
        msgs = filter(lambda x: x != None, msgs)
    if len(msgs) > 0:
        t_form = lambda x: asctime(localtime(float(x)))
        m_form = lambda x: '%s [%s:%s] -> '\
                            '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
        print 'Board published messages:'
        print '\n'.join(map(lambda x: m_form(x),msgs))

    if args.time == True:
        print(getTime(s, server))

    if args.requesttime == True:
        curtime = time()
        rqtime_resp = noPublish(s, server, [curtime])
        rqtime = float(''.join(rqtime_resp))
        print 'Time to publish message: %f seconds' % rqtime

    print 'Terminating ...'
    s.close()
