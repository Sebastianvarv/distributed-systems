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
Created on Aug 23, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
# Needed imports ------------------ -------------------------------------------
from udp.mboard.sessions.client.protocol import publish, last, get, get_data_from
from socket import socket, AF_INET, SOCK_DGRAM
from time import localtime, asctime
from argparse import ArgumentParser # Parsing command line arguments
from sys import stdin
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Client'
___VER = '0.0.1.2'
___DESC = 'Simple Message Board Client'
___BUILT = '2016-08-19'
___VENDOR = 'Copyright (c) 2016 DSLab'
# -----------------------------------------------------------------------------
__DEFAULT_SERVER_PORT = 7777
__DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
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
                        help='Get iDs of last N messages,'\
                        'defaults to "all"',\
                        default=0)
    parser.add_argument('-d', '--data', action='store_true',\
                        help='Fetch all unread messages')
    args = parser.parse_args()
    # Declare client socket
    sock = socket(AF_INET, SOCK_DGRAM)
    srv = (args.host, int(args.port))  # Server's socket address

    m = args.message # Message to publish
    if m == '-':
        # Read m from STDIN (with protocol 0.0.1.x we can read bigger input)
        #  m is stored in virtual memory, therefore optimal input should\
        #  not be bigger the RAM, otherwise swapping will reduce
        #  performance
        # @TODO: Rewrite STDIN processing, do reading by blocks adjust to
        #         the amount of RAM
        #
        m = stdin.read()

    # Parse integer
    n = int(args.last)  # Last n messages to fetch

    ids = []
    msgs = []


    if len(m) > 0:
        if publish(sock, srv, m):
            print 'Message published'

    # Query messages
    if n >= 0 and not args.data:
        ids += last(sock, srv, n)

    if len(ids) > 0:
        msgs += map(lambda x: get(sock, srv, x), ids)
        msgs = filter(lambda x: x != None, msgs)
    if len(msgs) > 0:
        t_form = lambda x: asctime(localtime(float(x)))
        m_form = lambda x: '%s [%s:%s] -> '\
                            '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
        print 'Board published messages:'
        print '\n'.join(map(lambda x: m_form(x),msgs))

    if args.data:
        msg_data = get_data_from(sock, srv)
        print 'Message list %s' % str(msg_data  )

    print 'Terminating ...'
    sock.close()
