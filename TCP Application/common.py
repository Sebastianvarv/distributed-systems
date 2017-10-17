# Requests --------------------------------------------------------------------
__REQ_UPLOAD = '1'
__REQ_SEND_FILENAME = '2'

__CTR_MSGS = {__REQ_UPLOAD: 'Upload file',
              __REQ_SEND_FILENAME: 'Send filename'
              }
# Responses--------------------------------------------------------------------
__RSP_OK = '0'
__RSP_FILEEXISTS = '1'

__RSP_ERRTRANSM = '4'
__ERR_MSGS = {__RSP_OK: 'No Error',
              __RSP_FILEEXISTS: 'Malformed message',
              __RSP_ERRTRANSM: 'Transmission Error'
              }
# Field separator for sending multiple values ---------------------------------
__MSG_FIELD_SEP = ':'
__MSG_END = '__END'
