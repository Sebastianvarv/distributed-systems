'''
Created on Oct 27, 2016

@author: devel
'''
import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_MULTICAST_LOOP, SOL_SOCKET, \
    SO_REUSEADDR, IP_DEFAULT_MULTICAST_TTL

import Pyro4


@Pyro4.expose
class User(object):
    '''User class extending PyRO object.
    instances of this one can be exposed over network
    '''

    def __init__(self, name, chat):
        self.name = name
        self.private_msgs = []  # for receiving private messages
        self.last_common = 0  # for knowing last viewed public message
        self.chat = chat  # parent chat

    def post(self, msg):
        '''Public post'''
        self.chat.post(msg, self.name)

    def post_private(self, msg, to):
        '''Private post'''
        self.chat.post_private(msg, to, self.name)

    def get(self):
        '''Get all public posts for me, not viewed'''
        msgs = self.chat.get(self.last_common)
        self.last_common += len(msgs)
        return msgs

    def get_private(self):
        '''Get all private posts for me, not viewed'''
        msgs = [m for m in self.private_msgs]
        self.private_msgs = []
        return msgs

    def whoami(self):
        return self.name


@Pyro4.expose
class Chat(object):
    '''Chat class extending PyRO object.
    instances of this one can be exposed over network
    '''

    def __init__(self):
        self.users = {}
        self.msgs = []

    def register(self, me):
        print "Register", me
        '''Register user by name, return PyRO objects URI'''
        user = User(me, self)
        self.users[me] = user
        u_uri = daemon.register(user)
        return str(u_uri)

    def post(self, msg, name='Unknown'):
        '''Post public message'''
        self.msgs.append('From %s : %s' % (name, msg))

    def post_private(self, msg, to, name='Unknown'):
        '''Post private message'''
        if to not in self.users.keys():
            return
        self.users[to].private_msgs.append('From %s : %s' % (name, msg))

    def get(self, idx=0):
        '''Get all public messages starting from idx'''
        return self.msgs[idx:]

    def get_users(self):
        '''Get all users online'''
        return self.users.keys()

    def remove_user(self, name):
        del self.users[name]
        self.msgs.append("User " + name + " leaved the chat room")


def send_multicast(msg):
    __mcast_addr = '239.1.1.1'
    __mcast_port = 53124
    __mcast_ttl = 4
    __s = socket(AF_INET, SOCK_DGRAM)
    __s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    __s.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
    __s.setsockopt(IPPROTO_IP, IP_DEFAULT_MULTICAST_TTL, __mcast_ttl)

    thread = threading.Thread(target=poll_multicast, args=(__mcast_addr, __mcast_port, __s, msg))
    thread.setDaemon(True)
    thread.start()


def poll_multicast(__mcast_addr, __mcast_port, __s, msg):
    while True:
        __s.sendto(msg, (__mcast_addr, __mcast_port))
        time.sleep(1)


if __name__ == '__main__':
    # make a Pyro daemon
    daemon = Pyro4.Daemon(host='127.0.0.1', port=7777)
    # Create chat, expose to network using PyRO
    chat = Chat()
    uri = daemon.register(chat)

    print "The chat URI is:", uri
    send_multicast(str(uri))

    daemon.requestLoop()
