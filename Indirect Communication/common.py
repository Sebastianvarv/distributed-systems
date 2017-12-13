# Requests --------------------------------------------------------------------
REQ_USERNAME = '1'
REQ_LEAVE = '2'
REQ_LIST_USERS = '3'
REQ_LIST_ROOMS = '4'
REQ_CREATE_ROOM = '5'
REQ_CREATE_PRIVATE_ROOM = '6'
REQ_LEAVE_ROOM = '7'
REQ_JOIN_ROOM = '8'
REQ_SEND_MSG = '9'
REQ_GET_MSG = '10'
CTR_MSGS = {REQ_USERNAME: 'Register username',
            REQ_LEAVE: 'Exit from application',
            REQ_LIST_USERS: 'List all users',
            REQ_LIST_ROOMS: 'List all rooms',
            REQ_CREATE_ROOM: 'Create new public chat room',
            REQ_CREATE_PRIVATE_ROOM: 'Create new private chat room',
            REQ_LEAVE_ROOM: 'Leave current chat room',
            REQ_JOIN_ROOM: "Join a new room",
            REQ_SEND_MSG: 'Send new message',
            REQ_GET_MSG: 'Fetch messages'
            }

# Responses--------------------------------------------------------------------
RSP_OK = '0'
RSP_USERNAMETAKEN = '1'
RSP_ROOMNAME_TAKEN = '3'
RSP_NOT_FOUND = '4'
RSP_ERRTRANSM = '5'
ERR_MSGS = {RSP_OK: 'No Error',
            RSP_USERNAMETAKEN: 'Username is taken',
            RSP_ERRTRANSM: 'Transmission Error',
            RSP_ROOMNAME_TAKEN: 'Room name is taken',
            RSP_NOT_FOUND: 'Such room or user does not exist'
            }
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
MSG_END = 'END'
