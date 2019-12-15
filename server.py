import os, sys
import _thread
from socket import *
import argparse

class ChatServer():
    connection_pool = {}
    _render_msg = "init"

    def __init__(self, parent, args):
        self.main(parent, args)

    def __del__(self):
        print("closing")
        for username in self.connection_pool:
            self.connection_pool[username].send('###CLOSE###'.encode('utf-8'))
            self.connection_pool[username].close()

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
            try:
                request = _connectionSock.recv(args.max_data_recv).decode()
            except UnicodeDecodeError as e:
                continue

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
            elif(request.find("###FILE###") != -1):
                request = request.split('###FILE###')[1].rstrip('\0')
                if(request.split('#', 1)[0] not in self.connection_pool):
                    _connectionSock.send(('###WARNING###' + (request.split('#', 1)[0]) + ' not connected').encode('utf-8'))
                #elif request.split('#', 1)[0] == username:
                 #   _connectionSock.send(('###WARNING###' + (request.split('#', 1)[0]) + ' is you').encode('utf-8'))
                else:
                    file_type = request.split('#')[1]
                    diff = args.max_data_recv - len(('###FILE###' + file_type).encode('utf-8'))
                    tmp = ''
                    for i in range(diff): # send the data with fixed size of max_data_recv
                        tmp += '\0'
                    self.connection_pool[request.split('#', 1)[0]].send(('###FILE###' + file_type + tmp).encode('utf-8'))
                    size = _connectionSock.recv(4) # assuming that the size won't be bigger then 1GB.
                    self.connection_pool[request.split('#', 1)[0]].send(size)
                    size = self.bytes_to_number(size)
                    current_size = 0
                    buffer = b""
                    i = 1
                    while(current_size < size):
                        r = _connectionSock.recv(args.max_data_recv)
                        if not r:
                            break
                        if len(r) + current_size > size:
                            r = r[:size-current_size] # trim additional data
                        buffer += r
                        current_size += len(r)
                        self.connection_pool[request.split('#', 1)[0]].send(r)
                    print('done')
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
            print(data.decode())
            # self.printmsg(parent, data.decode())
            if(data.decode() == "###LIST###"):
                try:
                    on_list = ''
                    for _user_name in self.connection_pool:
                        on_list += _user_name + '\n'
                    if on_list == '':
                        on_list = "empty"
                    _udpSock.sendto(on_list.encode('utf-8'), address)
                except OSError as e:
                    if _udpSock:
                        _udpSock.close()
                    print(e)
                    sys.exit(1)

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i*8)
        return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=1024) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatServer = ChatServer(None, args)
