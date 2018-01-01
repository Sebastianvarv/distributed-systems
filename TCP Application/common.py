# Requests --------------------------------------------------------------------
__REQ_UPLOAD = '1'
__REQ_SEND_FILENAME_AND_SIZE = '2'
__REQ_LISTFILES = '3'
__REQ_DOWNLOAD = '4'
__CTR_MSGS = {__REQ_UPLOAD: 'Upload file',
              __REQ_SEND_FILENAME_AND_SIZE: 'Send filename',
              __REQ_DOWNLOAD: 'Download file'
              }
# Responses--------------------------------------------------------------------
__RSP_OK = '0'
__RSP_FILEEXISTS = '1'
__RSP_DISKSPACE_ERR = '3'
__RSP_NO_SUCH_FILE = '4'
__RSP_ERRTRANSM = '5'
__ERR_MSGS = {__RSP_OK: 'No Error',
              __RSP_FILEEXISTS: 'Malformed message',
              __RSP_ERRTRANSM: 'Transmission Error',
              __RSP_DISKSPACE_ERR: 'Not enough disk space',
              __RSP_NO_SUCH_FILE: 'Such file does not exist'
              }
# Field separator for sending multiple values ---------------------------------
__MSG_FIELD_SEP = ':'
__MSG_END = '__END'
