#!/usr/bin/python
#
# Implements message board TCP client
#
# Switching to TCP protocol allows us to avoid programming of our own sessions
# for big-block delivery. TCP connections are in fact a data delivery sessions.
# Therefore in this implementation we just removed everything
# related to the sessions protocol, that we implemented for UDP.
# When sending a request the client first connects to server,
# then request/response sequence starts.
#
# --------------
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
Message board client (TCP)
Created on Aug 23, 2016

@author: devel
'''
# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Needed imports ------------------ -------------------------------------------
from tcp.mboard.sessions.client import protocol
from protocol import publish, last
from time import localtime, asctime
from sys import stdin
# Constants -------------------------------------------------------------------
___NAME = 'MBoard Client'
___VER = '0.1.0.0'
___DESC = 'Simple Message Board Client (TCP version)'
___BUILT = '2016-09-13'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
# Not a real main method-------------------------------------------------------
def mboard_client_main(args):
    '''Runs the Mboard client
    should be run by the main mehtod of CLI or GUI application
    @param args: ArgParse collected arguments
    '''
    # Starting client
    LOG.info('%s version %s started ...' % (___NAME, ___VER))
    LOG.info('Using %s version %s' % ( protocol.___NAME, protocol.___VER))

    # Processing arguments
    # 1.) If -m was provided
    m = ''
    if len(args.message) > 0:
        m = args.message # Message to publish
        if m == '-':
            LOG.debug('Will read message from standard input ...')
            # Read m from STDIN
            m = stdin.read()
        LOG.debug('User provided message of %d bytes ' % len(m))

    # Processing arguments
    # 2.) If -l was provided
    # Parse integer
    n = int(args.last)  # Last n messages to fetch
    n = n if n > 0 else 0 # no negative values allowed
    LOG.debug('Will request %s published messages'\
              '' % ('all' if n == 0 else ('last %d' % n)))

    # Server's socket address
    server = (args.host,int(args.port))

    msgs = []

    try:
        if len(m) > 0:
            if publish(server, m):
                LOG.info('Message published')
            else:
                exit(3)

        # Query messages
        # With TCP we may get all messages in one request
        msgs += last(server,n)
    except KeyboardInterrupt:
            LOG.debug('Crtrl+C issued ...')
            LOG.info('Terminating ...')
            exit(2)

    # Split messages by space
    #  [ "<timestamp> <ip> <port> <message>", ... ]
    msgs = map(lambda x: x.split(' '),msgs)
    # Consider 1-st 3 elements: timestamp, ip and port,
    # and thr rest is the actual message
    msgs = map(lambda x: tuple(x[:3]+[' '.join(x[3:])]),msgs)

    if len(msgs) > 0:
        t_form = lambda x: asctime(localtime(float(x)))
        m_form = lambda x: '%s [%s:%s] -> '\
                            '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
        print 'Board published messages:'
        print '\n'.join(map(lambda x: m_form(x),msgs))

    print 'Terminating ...'