import os, sys
import _thread
from socket import *
import argparse

connection_pool = []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()

    for i in range(args.backlog):
        connection_pool.append(None)

    try:
        serverSock = socket(AF_INET, SOCK_STREAM) # TCP
        serverSock.bind(('', args.port)) # localhost
        serverSock.listen(args.backlog)
    except OSError as e:
        if serverSock:
            serverSock.close()
        if(args.debug):
            print(e)
        sys.exit(1)
    
    if(args.debug):
        print('..listening..')
    
    while 1:
        connectionSock, client_addr = serverSock.accept()
        if(connectionSock):
            print("accepted")
            _thread.start_new_thread(connection_thread, (connectionSock, client_addr, args))

    serverSock.close()

def connection_thread(_connectionSock, _client_addr, args):
    user = None
    while 1:
        request = _connectionSock.recv(args.max_data_recv).decode('utf-8')
        if(args.debug):
            print(request)
        if(request == 'exit'):
            _connectionSock.close()
            connection_pool[int(request.split(':')[1])] = None
            print('connection closed')
            break
        if(request.split(':')[0] == 'user_id'): # first meet
            if connection_pool[int(request.split(':')[1])] == None:
                user = int(request.split(':')[1])
                connection_pool[user] = _connectionSock
                # _connectionSock.send(('connected user ' + request.split(':')[1]).encode('utf-8'))
            else:
                _connectionSock.send('[error] invalid access detected'.encode('utf-8'))
                _connectionSock.close()
                connection_pool[int(request.split(':')[1])] = None
                print('connection closed')
                break
        else:
            if(connection_pool[int(request.split('#', 1)[0])] == None):
                _connectionSock.send(('[error] user' + (request.split('#', 1)[0]) + ' not connected').encode('utf-8'))
                _connectionSock.close()
                connection_pool[user] = None
                print('connection closed')
                break
            else:
                connection_pool[int(request.split('#', 1)[0])].send(("\n[user" + str(user) + "]: " + request.split('#')[1]+"\n>>>").encode('utf-8'))
    

if __name__ == "__main__":
    main()