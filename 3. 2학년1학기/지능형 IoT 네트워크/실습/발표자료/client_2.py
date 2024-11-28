import socket
import datetime
import time

# IN : NCD.io 수신기 ip주소 및 port번호
HOST_IN = "172.30.1.80"
PORT_IN = 2101
# OUT : server 와 통신하기 위한 server의 ip주소 및 port번호
HOST_OUT = "172.30.1.48" # 현재 주소 : ryong miniPC
PORT_OUT = 12301
# 소켓 객체 생성(TCP 방식)
client_socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try :
    client_socket_in.connect((HOST_IN, PORT_IN))
    print('Connect1 OK!')
    client_socket_out.connect((HOST_OUT, PORT_OUT))
    print('Connect2 OK!')
except :
    print('Connect Fail')


while True :
    now = datetime.datetime.now()
    data = client_socket_in.recv(1024) # 수신기로부터 진동데이터 받고
    client_socket_out.send(data) # 받은 데이터 server로 전송
    print("%4d-%02d-%02d %02d:%02d:%02d  %d byte 수신" % (now.year,now.month,now.day,now.hour,now.minute,now.second, len(data)))
    for x in data :
        print("%02x " % x, end='')
    print("\n")
    
    
client_socket_in.close()
client_socket_out.close()