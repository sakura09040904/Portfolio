# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 12:46:45 2024

@author: kyj23
"""

from socket import *

serverPort = 12000

serverSoket = socket(AF_INET, SOCK_DGRAM)

serverSoket.bind(('127.0.0.1', serverPort))

print("The server is ready to receive")

while True:
    message, clientAddress = serverSoket.recvfrom(2048)
    
    modifiedMessage = message.decode().upper()
    
    serverSoket.sendto(modifiedMessage.encode(), clientAddress)