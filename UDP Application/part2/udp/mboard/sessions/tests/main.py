# Implements tests for MBoard modules:
# 1.) Sessions
'''
Created on Aug 25, 2016

@author: devel
'''
# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Constants -------------------------------------------------------------------
__TEST_SRV_ADDR = ( '127.0.0.1', 7777 )
# Imports ---------------------------------------------------------------------
from udp.mboard.sessions.client.sessions import send_data
from udp.mboard.sessions.common import __SESS_MAX_PDU
from udp.mboard.sessions.server.sessions import process_session, \
        checkincoming, getincoming
from socket import socket,AF_INET,SOCK_DGRAM
from multiprocessing import Process, Queue
from time import sleep
# Sessions tester functions ------------------------------------------------------------
def ___test_custom_data_client(q,size):
    s = socket(AF_INET,SOCK_DGRAM)
    srv = __TEST_SRV_ADDR
    data = q.get(size)
    send_data(s,srv,data)
    s.close()

def ___test_custom_data_server(q):
    s = socket(AF_INET,SOCK_DGRAM)
    srv = __TEST_SRV_ADDR
    s.bind(srv)
    max_pdu = __SESS_MAX_PDU
    while checkincoming() <=0:
        m,source = s.recvfrom(max_pdu)
        r = process_session(m, source)
        s.sendto(r,source)
    data,source = getincoming()
    q.put(data)
    s.close()

def test_session_send_data(data):
    q_in,q_out = Queue(),Queue()
    server_p = Process(name='MBoardTestSessionSendDataServer',\
                       target=___test_custom_data_server,\
                       args=[q_out])
    client_p = Process(name='MBoardTestSessionSendDataClient',\
                       target=___test_custom_data_client,\
                       args=[q_in,len(data)])
    q_in.put(data)
    server_p.start()
    sleep(2)
    client_p.start()
    rcv_data = q_out.get(len(data))
    client_p.join()
    server_p.join()
    assert(len(data) == len(rcv_data))
    assert(data == rcv_data)

if __name__ == '__main__':
    test_session_send_data('aaaaaaaaaaaa'*2**16)

