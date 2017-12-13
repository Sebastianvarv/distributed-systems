#!/usr/bin/env python
import uuid
from argparse import ArgumentParser

import pika

from common import RSP_OK, REQ_USERNAME, MSG_FIELD_SEP, REQ_LEAVE, REQ_LIST_USERS, REQ_LIST_ROOMS, REQ_CREATE_ROOM, \
    REQ_CREATE_PRIVATE_ROOM, REQ_LEAVE_ROOM, REQ_JOIN_ROOM, REQ_SEND_MSG, REQ_GET_MSG

QUEUE_NAME = "msg_queue"
CURRENT_ROOM = ""


class ChatClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=QUEUE_NAME,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return str(self.response)


def request_username(chat_rpc, username):
    response = chat_rpc.call(REQ_USERNAME + MSG_FIELD_SEP + username)
    if response.startswith(RSP_OK):
        return True
    return False


def send_leave_request(chat_rpc, username):
    chat_rpc.call(REQ_LEAVE + MSG_FIELD_SEP + username)


def list_users(chat_rpc):
    response = chat_rpc.call(REQ_LIST_USERS + MSG_FIELD_SEP)
    header, msg = response.split(MSG_FIELD_SEP, 1)
    if header == RSP_OK:
        return "--- All users: " + msg
    else:
        return "--- Something went wrong with listing users, rsp:" + response


def list_chatrooms(chat_rpc, username):
    response = chat_rpc.call(REQ_LIST_ROOMS + MSG_FIELD_SEP + username)
    header, msg = response.split(MSG_FIELD_SEP, 1)
    if header == RSP_OK:
        return "--- All chat rooms: " + msg
    else:
        return "--- Something went wrong with listing chat rooms, rsp:" + response


def create_chat_room(chat_rpc, username, user_input):
    global CURRENT_ROOM
    _, room_name = user_input.strip().split(" ", 1)
    response = chat_rpc.call(REQ_CREATE_ROOM + MSG_FIELD_SEP + username
                             + MSG_FIELD_SEP + room_name)
    if response.startswith(RSP_OK):
        CURRENT_ROOM = room_name
        return "--- You were added to chat room: " + room_name + "\n--- For exiting room type exit()"
    else:
        return "--- Chat room name already taken"


def create_private_chat_room(chat_rpc, username, user_input):
    global CURRENT_ROOM
    _, room_name, invite_list = user_input.strip().split(" ", 2)
    response = chat_rpc.call(REQ_CREATE_PRIVATE_ROOM + MSG_FIELD_SEP + username
                             + MSG_FIELD_SEP + room_name + MSG_FIELD_SEP + invite_list)
    if response.startswith(RSP_OK):
        CURRENT_ROOM = room_name
        return "--- You were added to chat room: " + room_name + "\n--- For exiting room type exit()"
    else:
        return "--- Chat room name already taken"


def exit_chatroom(chat_rpc, username):
    global CURRENT_ROOM
    response = chat_rpc.call(REQ_LEAVE_ROOM + MSG_FIELD_SEP + username)
    if response.startswith(RSP_OK):
        CURRENT_ROOM = ""
        return "--- You entered lobby"
    else:
        return "--- Something went wrong with exiting the room"


def join_room(chat_rpc, username, user_input):
    global CURRENT_ROOM
    _, room_name = user_input.split(" ", 1)
    response = chat_rpc.call(REQ_JOIN_ROOM + MSG_FIELD_SEP + room_name + MSG_FIELD_SEP + username)
    if response.startswith(RSP_OK):
        CURRENT_ROOM = room_name
        return "--- You were added to chat room: " + room_name + "\n--- For exiting room type exit()"
    else:
        return "--- No such room found"


def send_msg(chat_rpc, username, user_input):
    response = chat_rpc.call(REQ_SEND_MSG + MSG_FIELD_SEP + username + MSG_FIELD_SEP + CURRENT_ROOM + MSG_FIELD_SEP +
                             user_input)
    if response.startswith(RSP_OK):
        return response.split(MSG_FIELD_SEP, 1)[1]
    else:
        return "--- Message sending failed"


def refresh_msg(chat_rpc):
    response = chat_rpc.call(REQ_GET_MSG + MSG_FIELD_SEP + CURRENT_ROOM)
    if response.startswith(RSP_OK):
        return response.split(MSG_FIELD_SEP, 1)[1]
    else:
        return "Fetching new messages failed"


def parse_user_input(chat_rpc, user_input, username):
    try:
        if user_input == "-l":
            return list_users(chat_rpc)
        elif user_input == "-r":
            return list_chatrooms(chat_rpc, username)
        elif user_input.startswith("-c "):
            return create_chat_room(chat_rpc, username, user_input)
        elif user_input.startswith("-p "):
            return create_private_chat_room(chat_rpc, username, user_input)
        elif user_input.startswith("exit()"):
            return exit_chatroom(chat_rpc, username)
        elif user_input.startswith("-j "):
            return join_room(chat_rpc, username, user_input)
        elif CURRENT_ROOM:
            if user_input and user_input != "":
                return send_msg(chat_rpc, username, user_input)
            else:
                return refresh_msg(chat_rpc)
    except:
        return "--- Incorrect input!"


def main(args):
    username = args.username

    chat_rpc = ChatClient()
    if request_username(chat_rpc, username):
        try:
            while True:
                if not CURRENT_ROOM:
                    print "For seeing registred users write -l\n" \
                          "For seeing all public chatrooms write -r\n" \
                          "Creating public chatroom -c [ROOM NAME]\n" \
                          "Creating private chatroom -p [ROOM NAME] [COMMA SEP INVITED MEMBERS eg. user1, user2, ..., userN]\n" \
                          "Joining existing room -j [ROOM NAME]"
                response = raw_input()
                request_response = parse_user_input(chat_rpc, response, username)
                if request_response:
                    print request_response
                else:
                    print "Invalid request, choose one from below:"


        except KeyboardInterrupt:
            send_leave_request(chat_rpc, username)
            print("Shutting down")
            return
    else:
        print("Username already taken, choose new username and try again")
        return


if __name__ == "__main__":
    parser = ArgumentParser(description="Client for uploading/listing files.")

    parser.add_argument('-a', '--server-addr', help="Address of the host. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-l', '--list', help="List all the files in the server.", action='store_true')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-u", "--username", help="Username in chat client", required=True)
    args = parser.parse_args()
    main(args)
