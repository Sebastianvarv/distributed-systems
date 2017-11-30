'''
Created on Oct 18, 2016

@author: devel
'''
import logging

FORMAT = '%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err
from base64 import decodestring, encodestring
from time import asctime, localtime

# Requests --------------------------------------------------------------------
REQ_PUBLISH = '1'
REQ_GET = '2'
CTR_MSGS = {REQ_GET: 'Get messages',
            REQ_PUBLISH: 'Publish new message',
            }
# Responses--------------------------------------------------------------------
RSP_OK_PUBLISH = '0'
RSP_OK_GET = '1'
RSP_BADFORMAT = '2'
RSP_UNKNCONTROL = '4'
RSP_NOTIFY = '7'
# Assuming message itself is base64 encoded
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
# Message separator for sending multiple messages------------------------------
MSG_SEP = ';'

DEFAULT_RCV_BUFSIZE = 1024


def handle_user_input(myclient):
    logging.info('Starting input processor')

    while 1:
        logging.info('\nHit Enter to init user-input ...')
        raw_input('')
        logging.info('\nEnter message to send to all or Q to exit: ')
        m = raw_input('')
        if len(m) <= 0:
            continue
        elif m == 'Q':
            myclient.stop()
            return
        else:
            myclient.publish(m)


def serialize(msg):
    return encodestring(msg)


def deserialize(msg):
    return decodestring(msg)


class Client():
    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None
        self.__on_published = None

    def stop(self):
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

    def set_on_recv_callback(self, on_recv_f):
        self.__on_recv = on_recv_f

    def set_on_published_callback(self, on_published_f):
        self.__on_published = on_published_f

    def connect(self, srv_addr):
        self.__s = socket(AF_INET, SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to MessageBoard server at %s:%d' % srv_addr)
            return True
        except soc_err as e:
            logging.error('Can not connect to MessageBoard server at %s:%d' \
                          ' %s ' % (srv_addr + (str(e),)))
        return False

    def __session_rcv(self):
        m, b = '', ''
        try:
            b = self.__s.recv(DEFAULT_RCV_BUFSIZE)
            m += b
            while len(b) > 0 and not (b.endswith(MSG_SEP)):
                b = self.__s.recv(DEFAULT_RCV_BUFSIZE)
                m += b
            if len(b) <= 0:
                logging.debug('Socket receive interrupted')
                self.__s.close()
                m = ''
            m = m[:-1]
        except KeyboardInterrupt:
            self.__s.close()
            logging.info('Ctrl+C issued, terminating ...')
            m = ''
        except soc_err as e:
            if e.errno == 107:
                logging.warn('Server closed connection, terminating ...')
            else:
                logging.error('Connection error: %s' % str(e))
            self.__s.close()
            logging.info('Disconnected')
            m = ''
        return m

    def __session_send(self, msg):
        m = msg + MSG_SEP
        with self.__send_lock:
            r = False
            try:
                self.__s.sendall(m)
                r = True
            except KeyboardInterrupt:
                self.__s.close()
                logging.info('Ctrl+C issued, terminating ...')
            except soc_err as e:
                if e.errno == 107:
                    logging.warn('Server closed connection, terminating ...')
                else:
                    logging.error('Connection error: %s' % str(e))
                self.__s.close()
                logging.info('Disconnected')
            return r

    def publish(self, msg):
        data = serialize(msg)
        req = REQ_PUBLISH + MSG_FIELD_SEP + data
        return self.__session_send(req)

    def __fetch_msgs(self):
        req = REQ_GET + MSG_FIELD_SEP
        return self.__session_send(req)

    def __protocol_rcv(self, message):
        logging.debug('Received [%d bytes] in total' % len(message))
        if len(message) < 2:
            logging.debug('Not enough data received from %s ' % message)
            return
        logging.debug('Response control code (%s)' % message[0])
        if message.startswith(RSP_OK_PUBLISH + MSG_FIELD_SEP):
            logging.debug('Server confirmed message was published')
            self.__on_published()
        elif message.startswith(RSP_NOTIFY + MSG_FIELD_SEP):
            logging.debug('Server notification received, fetching messages')
            self.__fetch_msgs()
        elif message.startswith(RSP_OK_GET + MSG_FIELD_SEP):
            logging.debug('Messages retrieved ...')
            msgs = message[2:].split(MSG_FIELD_SEP)
            msgs = map(deserialize, msgs)
            for m in msgs:
                self.__on_recv(m)
        else:
            logging.debug('Unknown control message received: %s ' % message)
            return RSP_UNKNCONTROL

    def loop(self):
        logging.info('Falling to receiver loop ...')
        self.__fetch_msgs()
        while 1:
            m = self.__session_rcv()
            if len(m) <= 0:
                break
            self.__protocol_rcv(m)


if __name__ == '__main__':
    def on_recv(msg):
        if len(msg) > 0:
            msg = msg.split(' ')
            msg = tuple(msg[:3] + [' '.join(msg[3:])])
            t_form = lambda x: asctime(localtime(float(x)))
            m_form = lambda x: '%s [%s:%s] -> ' \
                               '%s' % (t_form(x[0]), x[1], x[2], x[3].decode('utf-8'))
            m = m_form(msg)
            logging.info('\n%s' % m)


    def on_publish():
        logging.info('\n Message published')


    c = Client()
    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)

    if c.connect(('127.0.0.1', 7777)):
        t = Thread(name='InputProcessor', \
                   target=handle_user_input, args=(c,))
        t.start()

        c.loop()
        t.join()

    logging.info('Terminating')
