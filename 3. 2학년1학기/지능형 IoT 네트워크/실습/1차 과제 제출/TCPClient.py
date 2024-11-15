# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 12:45:17 2024

@author: kyj23
"""

from socket import *

serverName = '127.0.0.1'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))

sentence = input('Input lowercase sentence:')

clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024)
print('From Server:', modifiedSentence.decode())

clientSocket.close()