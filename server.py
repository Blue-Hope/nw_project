import os, sys
import _thread
from socket import *
import argparse

class ChatServer():
    connection_pool = {}
    _render_msg = "init"

    def __init__(self, parent, args):
        self.main(parent, args)

    def main(self, parent, args):
        try:
            serverSock = socket(AF_INET, SOCK_STREAM) # TCP
            serverSock.bind(('', args.port)) # localhost
            serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            serverSock.listen(args.backlog)
            udpSock = socket(AF_INET, SOCK_DGRAM) # UDP
            udpSock.bind(('', args.port + 1))
            

        except OSError as e:
            if serverSock:
                serverSock.close()
            print(e)
            sys.exit()

        print('..listening..')

        _thread.start_new_thread(self.udp_thread, (udpSock, args))
        while 1:
            connectionSock, client_addr = serverSock.accept()
            if(connectionSock):
                _thread.start_new_thread(self.connection_thread, (parent, connectionSock, client_addr, args))                

        serverSock.close()
        udpSock.close()

    def connection_thread(self, parent, _connectionSock, _client_addr, args):
        username = ""
        while True:
            request = _connectionSock.recv(args.max_data_recv).decode('utf-8')

            if(request != ''):
                print(username, request)

            if(request == '###EXIT###'): # client exit handling
                _connectionSock.close()
                self.connection_pool.pop(username)
                print('connection closed')
                break
            if(request.find('###STARTCONNECT###') != -1): # first meet
                request = request.split('###STARTCONNECT###')[1]
                if request not in self.connection_pool:
                    username = request
                    self.connection_pool[username] = _connectionSock
                    _connectionSock.send(('###CONNECTSUCCESS###').encode('utf-8'))
                else:
                    _connectionSock.send('###ERROR###the username already used by someone'.encode('utf-8'))
                    print('connection closed')
                    break
            elif(request.find('###DATA###') != -1): # else meet
                request = request.split('###DATA###')[1]
                if(request.split('#', 1)[0] not in self.connection_pool):
                    _connectionSock.send(('###WARNING###' + (request.split('#', 1)[0]) + ' not connected').encode('utf-8'))
                elif request.split('#', 1)[0] == username:
                    _connectionSock.send(('###WARNING###' + (request.split('#', 1)[0]) + ' is you').encode('utf-8'))
                else:
                    self.connection_pool[request.split('#', 1)[0]].send(("[" + username + "]: " + request.split('#')[1]).encode('utf-8'))

    def render_msg(self):
        return self._render_msg
    
    def udp_thread(self, _udpSock, args):
        while True:
            data, address = _udpSock.recvfrom(args.max_data_recv)
            # self.printmsg(parent, data.decode())
            if(data.decode() == "###LIST###"):
                try:
                    on_list = '------------ user in ------------\n'
                    for _user_name in self.connection_pool:
                        on_list += '[' + _user_name + '] logged in\n'
                        on_list += '---------------------------------\n'
                        _udpSock.sendto(on_list.encode('utf-8'), address)
                except OSError as e:
                    if _udpSock:
                        _udpSock.close()
                    print(e)
                    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatServer = ChatServer(None, args)
