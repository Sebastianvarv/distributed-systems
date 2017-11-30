# Requests --------------------------------------------------------------------
REQ_UPLOAD = '1'
REQ_SEND_FILENAME_AND_SIZE = '2'
REQ_LISTFILES = '3'
REQ_DOWNLOAD = '4'
REQ_RENAME = '5'
REQ_DELETE = '6'
CTR_MSGS = {REQ_UPLOAD: 'Upload file',
            REQ_SEND_FILENAME_AND_SIZE: 'Send filename',
            REQ_DOWNLOAD: 'Download file'
            }
# Responses--------------------------------------------------------------------
RSP_OK = '0'
RSP_FILEEXISTS = '1'
RSP_DISKSPACE_ERR = '3'
RSP_NO_SUCH_FILE = '4'
RSP_ERRTRANSM = '5'
ERR_MSGS = {RSP_OK: 'No Error',
            RSP_FILEEXISTS: 'Malformed message',
            RSP_ERRTRANSM: 'Transmission Error',
            RSP_DISKSPACE_ERR: 'Not enough disk space',
            RSP_NO_SUCH_FILE: 'Such file does not exist'
            }
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
MSG_END = 'END'
