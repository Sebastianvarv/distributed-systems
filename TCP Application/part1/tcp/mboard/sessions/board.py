#
# Implements simple message board API
#
# API has only 3 functions:
#     1.) Publish new message on the board
#     2.) Get the iDs of N last messages of the board
#     3.) Request the messages by iD
#
# All the messages are public (everything posted is also shown to everyone)
# Users are anonymous, IP and port stored for information
#
# Static implementation (no instances possible)
#
# API is using default Python dictionary for storing the received messages
# Messages in dictionary are stored by uuid (incrementally)
# Messages storage is not preserved (only exists during application's runtime)
# -----------------------------------------------------------------------------
'''
Simple message board
Created on Aug 19, 2016

@author: devel
'''
# Imports ---------------------------------------------------------------------
from time import time #  For storing and message arrival
# Constants -------------------------------------------------------------------
___NAME = 'MBoard API'
___VER = '0.0.0.1'
___DESC = 'Simple Message Board API'
___BUILT = '2016-08-19'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Private vars. - -------------------------------------------------------------
__m_board = {} # For storing published messages
__m_uuid = 0 # For generating unique iDs
# Private functions -----------------------------------------------------------
def __get_uuid():
    '''Generated unique iD using incremental counter
    @returns int, new uuid
    '''
    global __m_uuid
    uuid = __m_uuid
    __m_uuid += 1
    return uuid
# Public functions ------------------------------------------------------------
def publish(msg,source):
    '''Put the received message into message board list, set received timestamp
        @param msg: string, received message (assuming UTF-8)
        @param source: tuple (ip,port), sender's socket address
    '''
    global __m_board
    ip,port = source
    t = time()
    uuid = __get_uuid()
    __m_board[uuid] = (uuid, t, ip, port, msg)
    return uuid

def last(n=0):
    '''Return IDs of last n messages appended
    @param n: number of last messages fetch, fetch all by default
    @returns: list [ int, int ... int ], IDs of last published messages
    '''
    global __m_board
    ids = map(lambda x: x[:2], __m_board.values())
    ids.sort(key=lambda x: x[1])
    return map(lambda x: x[0],ids[n*-1:])

def get(m_id):
    '''Return n last messages appended
        @param n: number of last messages fetch, fetch all by default
        @returns tuple ( float, str, int, msg ):
             1.) arrival time in seconds since UNIX epoch
             (floating point fractions denotes milliseconds if present)
             2.) IP address of the sender's socket
             3.) UDP port of the sender's socket
             4.) Message published by sender in UTF-8
    '''
    global __m_board
    return __m_board[m_id][1:]
