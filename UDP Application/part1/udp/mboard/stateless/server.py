#!/usr/bin/python
#
# Implements message board UDP server
# -----------------------------------------------------------------------------
#
# Server is using static message board implementation and state-less
# implementation of message board protocol
# -----------------------------------------------------------------------------
#
# State-less protocol
#
# Server is using state-less protocol, assuming client can only send one UDP
# packet per transaction (2 packets received from the same origin are processed
# in separate transactions. The server does not assure if the packets arriving
# in sequence from the same origin (each new arrived packet is considered as a
# new client). Having a protocol like this it is impossible to sent messages
# in multiple UDP packets from the same client; as the server may receive
# packets from different clients interleaved and does not organize packets
# into client sessions.
#
# Having client sessions would require to store additional information
# about a client on serve side (client sate). For example, in order to allow
# sending messages in multiple UDP packets, the partially received messages
# have to be temporally stored by server (till server receives all the UDP
# packets belonging to this message. Keeping the information about client
# state on server side is the key idea of state-full protocols
# (see: state-full MBoard protocol implementation)
# -----------------------------------------------------------------------------
'''
Message board server
Created on Aug 19, 2016

@author: devel
'''
# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
from udp.mboard.stateless import board, protocol
from socket import socket, AF_INET, SOCK_DGRAM
from argparse import ArgumentParser # Parsing command line arguments
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Server'
___VER = '0.0.0.1'
___DESC = 'Simple Message Board Server'
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
    parser.add_argument('-l','--listenaddr', \
                        help='Bind server socket to INET address, '\
                        'defaults to %s' % __DEFAULT_SERVER_INET_ADDR, \
                        default=__DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p','--listenport', \
                        help='Bind server socket to UDP port, '\
                        'defaults to %d' % __DEFAULT_SERVER_PORT, \
                        default=__DEFAULT_SERVER_PORT)
    args = parser.parse_args()
    # Starting server
    LOG.info('%s version %s started ...' % (___NAME, ___VER))
    LOG.info('Using %s version %s' % ( protocol.___NAME, protocol.___VER))
    LOG.info('Using %s version %s' % ( board.___NAME, board.___VER))
    # Declare UDP Socket
    __server_socket = socket(AF_INET,SOCK_DGRAM)
    LOG.debug('Server socket created, descriptor %d' % __server_socket.fileno())
    # Bind UDP Socket
    __server_socket.bind((args.listenaddr,args.listenport))
    LOG.debug('Server socket bound on %s:%d' % __server_socket.getsockname())
    LOG.info('Accepting requests on UDP %s:%d' % __server_socket.getsockname())

    # Serve forever
    while 1:
        try:
            LOG.debug('Awaiting requests ...')
            m,source = __server_socket.recvfrom(protocol.MAX_DATAUNIT_SIZE)
            LOG.debug('Received message from %s:%d' % source)
            r = protocol.server_process(board, m, source)
            LOG.debug('Processed request, response size [%d] bytes ' % len(r))
            __server_socket.sendto(r,source)
            LOG.debug('Response sent to %s:%d' % source)
        except KeyboardInterrupt as e:
            LOG.debug('Crtrl+C issued ...')
            LOG.info('Terminating server ...')
            break

    # Close server socket
    __server_socket.close()
    LOG.debug('Server socket closed')