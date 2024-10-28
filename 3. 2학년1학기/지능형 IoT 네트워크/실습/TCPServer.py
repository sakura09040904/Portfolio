# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 12:45:19 2024

@author: kyj23
"""

from socket import *

serverPort = 12000

serverSoket = socket(AF_INET, SOCK_STREAM)

serverSoket.bind(('127.0.0.1', serverPort))

serverSoket.listen(1)
print('The server is ready to receive')

while True:
    connectionSoket, addr = serverSoket.accept()
    sentence = connectionSoket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionSoket.send(capitalizedSentence.encode())
    
    connectionSoket.close()
    