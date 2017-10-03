# Here we just keep the common session constants used by server and client
#
'''
Created on Aug 23, 2016

@author: devel
'''
# Sessions protocol constants -------------------------------------------------
__SESS_REQ_NEW = 'a'
__SESS_REQ_SEND_BLOCK = 'b'
__SESS_REQ_CLOSE = 'c'

__SESS_RSP_OK = '0'
__SESS_RSP_RETRANS = 'y'
__SESS_RSP_BADFORMAT = 'z'

__SESS_FIELD_SEP = '?'

__SESS_MAX_PDU = 2**16-32 # Maximal UDP packet size without UDP header

__SESS_ERR_MSG = {  __SESS_RSP_OK:"No Error",\
                    __SESS_RSP_RETRANS:"Retransmit the last block",\
                    __SESS_RSP_BADFORMAT:"Corrupt block header"
                  }

# MBoard protocol constants ---------------------------------------------------
# Protocol Data Unit Size
MAX_PDU_SIZE_OLD_PROTO = 2**16-32 # Maximal UDP packet size without UDP header
# @TODO: Control how much to store in memory
# Currently not controlled - big input may affect performance (swapping issue)
MAX_PDU_SIZE = 200*1024*1024 # Reasonable amount of data to store in RAM
# Requests --------------------------------------------------------------------
__REQ_PUBLISH = '1'
__REQ_LAST = '2'
__REQ_GET = '3'
__REQ_GET_DATA = '4'
__CTR_MSGS = { __REQ_GET:'Get message by id',
               __REQ_LAST:'Get iDs of last N messages',
               __REQ_PUBLISH:'Publish new message',
               __REQ_GET_DATA:'Get all unread messages'
              }
# Responses--------------------------------------------------------------------
__RSP_OK = '0'
__RSP_BADFORMAT = '1'
__RSP_MSGNOTFOUND = '2'
__RSP_UNKNCONTROL = '3'
__RSP_ERRTRANSM = '4'
__ERR_MSGS = { __RSP_OK:'No Error',
               __RSP_BADFORMAT:'Malformed message',
               __RSP_MSGNOTFOUND:'Message not found by iD',
               __RSP_UNKNCONTROL:'Unknown control code',
               __RSP_ERRTRANSM:'Transmission Error'
               }
# Field separator for sending multiple values ---------------------------------
__MSG_FIELD_SEP = ':'