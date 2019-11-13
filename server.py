import os, sys
import _thread
from socket import *
import argparse

class ChatServer():
    connection_pool = []
    addr_list = []
    user_list = []
    _render_msg = "init"

    def __init__(self, parent, args):
        self.main(parent, args)

    def main(self, parent, args):
        for i in range(args.backlog):
            self.connection_pool.append(None)
            self.addr_list.append(None)
            self.user_list.append(None)

        try:
            serverSock = socket(AF_INET, SOCK_STREAM) # TCP
            serverSock.bind(('', args.port)) # localhost
            serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            udpSock = socket(AF_INET, SOCK_DGRAM) # UDP

            serverSock.listen(args.backlog)
        except OSError as e:
            if serverSock:
                serverSock.close()
            print(e)
            sys.exit(1)

        print('..listening..')

        while 1:
            connectionSock, client_addr = serverSock.accept()
            if(connectionSock):
                print("accepted")
                _thread.start_new_thread(self.connection_thread, (parent, udpSock, connectionSock, client_addr, args))

        serverSock.close()
        udpSock.close()

    def connection_thread(self, parent, _udpSock, _connectionSock, _client_addr, args):
        user = None
        username = ""
        while 1:
            request = _connectionSock.recv(args.max_data_recv).decode('utf-8')
            print(request)
            if(request == 'exit'):
                _connectionSock.send(('[exit]').encode('utf-8'))
                _connectionSock.close()
                print('connection closed')
                break
            if(request == ''):
                _connectionSock.send(('[exit]').encode('utf-8'))
                _connectionSock.close()
                print('connection closed')
                break
            if(request == ''):
                _connectionSock.send(('[exit]').encode('utf-8'))
                _connectionSock.close()
                print('connection closed')
                break
            if(request.split(':')[0] == 'user_id'): # first meet
                if self.connection_pool[int(request.split(':')[1])] == None:
                    user = int(request.split(':')[1])
                    username = request.split(':')[2]
                    self.connection_pool[user] = _connectionSock
                    self.addr_list[user] = (_client_addr[0], args.port + user)
                    self.user_list[user] = username
                    _connectionSock.send(("user[" + username + "] is connected").encode('utf-8'))
                    self.show_list(_udpSock, args) # show all list of user
                    # _connectionSock.send(('connected user ' + request.split(':')[1]).encode('utf-8'))
                else:
                    _connectionSock.send('[error] invalid access detected'.encode('utf-8'))
                    _connectionSock.close()
                    self.connection_pool[int(request.split(':')[1])] = None
                    print('connection closed')
                    break
            else:
                if(self.connection_pool[int(request.split('#', 1)[0])] == None):
                    _connectionSock.send(('[error] user' + (request.split('#', 1)[0]) + ' not connected').encode('utf-8'))
                    _connectionSock.close()
                    self.connection_pool[user] = None
                    print('connection closed')
                    break
                else:
                    self.connection_pool[int(request.split('#', 1)[0])].send(("\n[user" + str(user) + "]: " + request.split('#')[1]).encode('utf-8'))

    def render_msg(self):
        return self._render_msg

    def show_list(self, _udpSock, args):
        on_list = '----------- user list -----------\n'
        for i in range(args.backlog):
            if(self.connection_pool[i]!=None):
                on_list += str(i) + " : " +self.user_list[i] + '\n'

        on_list += '---------------------------------\n'

        for i in range(args.backlog):
            try:
                # Send data
                #print('sending')
                if(self.addr_list[i] != None):
                    _udpSock.sendto(on_list.encode('utf-8'), self.addr_list[i])

                # Receive response
                #print('waiting to receive')
                #data, server = udpSock.recvfrom(4096)
                #print('received {!r}'.format(data))

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
