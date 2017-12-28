import logging
from _socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_MULTICAST_LOOP, SOL_SOCKET, \
    SO_REUSEADDR, IP_DEFAULT_MULTICAST_TTL, SOL_IP, IP_ADD_MEMBERSHIP, inet_aton
from argparse import ArgumentParser

import Pyro4

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'


def multicast_rcv():
    __mcast_addr = '239.1.1.1'
    __mcast_port = 53124
    __mcast_ttl = 4
    __mcast_buffer = 1024
    __s = socket(AF_INET, SOCK_DGRAM)
    __s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    __s.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
    __s.setsockopt(IPPROTO_IP, IP_DEFAULT_MULTICAST_TTL, __mcast_ttl)
    __s.bind((__mcast_addr, __mcast_port))
    __s.setsockopt(SOL_IP, IP_ADD_MEMBERSHIP, inet_aton(__mcast_addr) + inet_aton('0.0.0.0'))
    msg, _ = __s.recvfrom(__mcast_buffer)
    return msg


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', '--name',
                        help='Username',
                        required=True)

    args = parser.parse_args()

    name = args.name

    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007

    chat_uri = multicast_rcv()
    # print "Received chat uri:", chat_uri

    chat = Pyro4.Proxy(chat_uri)
    # print "Created chat and connected pyro proxy"

    my_uri = chat.register(name)
    # print "Registered username in chat"

    me = Pyro4.Proxy(my_uri)

    print "Press ENTER to refresh the message feed, \n" \
          "Type -l to list all users. \n" \
          "type -p 'to_username' 'msg', to send private message \n" \
          "e.g '-p User1 This is a private message to User1'\n\n"

    while True:
        msg = me.get()
        private_msg = me.get_private()
        try:
            if msg:
                print "\nMy messages:"
                for elem in msg:
                    print elem
            if private_msg:
                print "\nMy private messages:"
                for msg in private_msg:
                    print msg

            input_msg = raw_input('Message to send: ')
            if len(input_msg) > 0:
                if input_msg.startswith("-p "):
                    try:
                        _, to_user, msg = input_msg.split(" ", 2)
                        me.post_private(msg, to_user)
                    except:
                        print "--- use form '-p Username message' ---"
                elif input_msg.startswith("-l"):
                    print chat.get_users()
                else:
                    me.post(input_msg)
        except KeyboardInterrupt:
            chat.remove_user(me.whoami())
            print "\nLeaving chat client"
            print "Terminating session"
            exit()
