#!/usr/bin/env python
import logging
from argparse import ArgumentParser

import pika
from common import RSP_OK, MSG_FIELD_SEP, REQ_USERNAME, RSP_USERNAMETAKEN, REQ_LEAVE, REQ_LIST_USERS, REQ_LIST_ROOMS, \
    REQ_CREATE_ROOM, RSP_ROOMNAME_TAKEN, REQ_CREATE_PRIVATE_ROOM, REQ_LEAVE_ROOM, REQ_JOIN_ROOM, RSP_NOT_FOUND, \
    REQ_SEND_MSG, REQ_GET_MSG

_USERS = set()
_PUBLIC_ROOMS = dict()  # key: room name value: set of users in this room
_PRIVATE_ROOMS = dict()  # key: room name value: set of users in this room
_PRIVATE_ROOM_INVITES = dict()  # key: room name value: set of invited users
_MESSAGES = dict()  # key:room name value: sender: msg

QUEUE_NAME = "msg_queue"

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)


def notify_all_users(msg):
    message = "User " + msg + " joined the lobby"
    for room_name in _PUBLIC_ROOMS.keys():
        if room_name not in _MESSAGES:
            _MESSAGES[room_name] = ["--- " + message + " ---"]
        else:
            _MESSAGES[room_name].append("--- " + message + " ---")

    for room in _PRIVATE_ROOMS.keys():
        if room_name not in _MESSAGES:
            _MESSAGES[room_name] = ["--- " + message + " ---"]
        else:
            _MESSAGES[room_name].append("--- " + message + " ---")


def create_public_room(user, room_name):
    if room_name not in _PUBLIC_ROOMS.keys():
        _PUBLIC_ROOMS[room_name] = {user}
        return RSP_OK + MSG_FIELD_SEP
    return RSP_ROOMNAME_TAKEN + MSG_FIELD_SEP


def create_private_room(user, room_name, invite_list):
    if room_name not in _PRIVATE_ROOMS.keys():
        _PRIVATE_ROOMS[room_name] = {user}
        _PRIVATE_ROOM_INVITES[room_name] = set(invite_list.split(", "))
        _PRIVATE_ROOM_INVITES[room_name].add(user)
        return RSP_OK + MSG_FIELD_SEP
    return RSP_ROOMNAME_TAKEN + MSG_FIELD_SEP


def list_rooms(username):
    all_rooms = _PUBLIC_ROOMS.keys()
    print(_PRIVATE_ROOM_INVITES.items())
    for room_name, invite_list in _PRIVATE_ROOM_INVITES.items():
        if username in invite_list:
            all_rooms.append(room_name)
    return RSP_OK + MSG_FIELD_SEP + str(all_rooms)


def exit_room(user_name):
    for roomname, users in _PUBLIC_ROOMS.items():
        users.discard(user_name)
        if not users:
            del _PUBLIC_ROOMS[roomname]

    for roomname, users in _PRIVATE_ROOMS.items():
        users.discard(user_name)
        if not users:
            del _PRIVATE_ROOMS[roomname]
            del _PRIVATE_ROOM_INVITES[roomname]

    return RSP_OK + MSG_FIELD_SEP


def add_user_to_room(username, room_name):
    if room_name in _PUBLIC_ROOMS.keys():
        _PUBLIC_ROOMS[room_name].add(username)
        return RSP_OK + MSG_FIELD_SEP
    elif room_name in _PRIVATE_ROOMS.keys():
        _PRIVATE_ROOMS[room_name].add(username)
        return RSP_OK + MSG_FIELD_SEP
    else:
        return RSP_NOT_FOUND + MSG_FIELD_SEP


def get_msgs(room):
    all_msgs_string = ""
    for message in _MESSAGES[room]:
        all_msgs_string += message
    return all_msgs_string


def add_msg(username, room, user_input):
    is_in_public = room in _PUBLIC_ROOMS and username in _PUBLIC_ROOMS[room]
    is_in_private = room in _PRIVATE_ROOMS and username in _PRIVATE_ROOMS[room]
    if is_in_public or is_in_private:
        if room not in _MESSAGES:
            _MESSAGES[room] = [username + " >> " + user_input + "\n"]
        else:
            _MESSAGES[room].append(username + " >> " + user_input + "\n")
        return RSP_OK + MSG_FIELD_SEP + get_msgs(room)
    else:
        return RSP_NOT_FOUND + MSG_FIELD_SEP


def fetch_msg(room_name):
    if room_name in _MESSAGES:
        return RSP_OK + MSG_FIELD_SEP + "".join(_MESSAGES[room_name])
    else:
        return RSP_OK + MSG_FIELD_SEP + "No messages yet ..."


def parse_msg(message):
    global _USERS
    global _PUBLIC_ROOMS

    header, msg = message.split(MSG_FIELD_SEP, 1)
    if header == REQ_USERNAME:
        if msg in _USERS:
            return RSP_USERNAMETAKEN + MSG_FIELD_SEP
        notify_all_users(msg)
        _USERS.add(msg)
        return RSP_OK + MSG_FIELD_SEP
    elif header == REQ_LEAVE:
        if _USERS:
            exit_room(msg)
            _USERS.discard(msg)
        return RSP_OK + MSG_FIELD_SEP
    elif header == REQ_LIST_USERS:
        return RSP_OK + MSG_FIELD_SEP + str(list(_USERS))
    elif header == REQ_LIST_ROOMS:
        return list_rooms(msg)
    elif header == REQ_CREATE_ROOM:
        username, room_name = msg.split(MSG_FIELD_SEP, 1)
        return create_public_room(username, room_name)
    elif header == REQ_CREATE_PRIVATE_ROOM:
        username, room_name, invite_list = msg.split(MSG_FIELD_SEP, 2)
        return create_private_room(username, room_name, invite_list)
    elif header == REQ_LEAVE_ROOM:
        return exit_room(msg)
    elif header == REQ_JOIN_ROOM:
        room_name, username = msg.split(MSG_FIELD_SEP, 1)
        return add_user_to_room(username, room_name)
    elif header == REQ_SEND_MSG:
        username, room, user_input = msg.split(MSG_FIELD_SEP, 2)
        return add_msg(username, room, user_input)
    elif header == REQ_GET_MSG:
        return fetch_msg(msg)


def on_request(channel, method, properties, body):
    response = parse_msg(body)

    channel.basic_publish(exchange='',
                          routing_key=properties.reply_to,
                          properties=pika.BasicProperties(correlation_id= \
                                                              properties.correlation_id),
                          body=str(response))
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main(args):
    try:
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(on_request, queue=QUEUE_NAME)

        print(" [x] Awaiting RPC requests")
        channel.start_consuming()
    except KeyboardInterrupt:
        print "Server terminating ..."


if __name__ == "__main__":
    parser = ArgumentParser(description="Message server")

    parser.add_argument('-a', '--server-addr', help="Address of the host. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    args = parser.parse_args()
    main(args)
