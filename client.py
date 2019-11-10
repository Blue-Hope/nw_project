import os, sys
import _thread
import time
from socket import *
import argparse

class ChatClient():
    def __init__(self, parent, args):
        super().__init__()
        self.main(parent, args)

    def main(self, parent, args):
        if(args.user == -1):
            print("invalid user id, assign --user [user_id]. (user_id > 0)")

        try:
            clientSock = socket(AF_INET, SOCK_STREAM) # TCP
            clientSock.connect(('13.125.249.160', args.port)) # localhost
            clientSock.send(('user_id:' + str(args.user) + ':' + args.username).encode('utf-8'))
            # clientSock.recv(args.max_data_recv).decode('utf-8')

            _thread.start_new_thread(self.send_thread, (parent, clientSock, args))
            _thread.start_new_thread(self.recv_thread, (parent, clientSock, args))

            while True:
                time.sleep(1)
                pass
        except OSError as e:
            print(e)


    def send_thread(self, parent, _clientSock, args):
        while True:
            if not parent.messageQueue.qsize():
                input_str = parent.messageQueue.get()
                if input_str == 'exit':
                    _clientSock.send('exit'.encode('utf-8'))
                    break
                else:
                    _clientSock.send((input_str.split(' ')[0] + "#" + input_str.split(' ', 1)[1]).encode('utf-8'))
            else:
                input_str = input(">>> ")
                if input_str == 'exit':
                    _clientSock.send('exit'.encode('utf-8'))
                    break
                else:
                    _clientSock.send((input_str.split(' ')[0] + "#" + input_str.split(' ', 1)[1]).encode('utf-8'))


    def recv_thread(self, parent, _clientSock, args):
        while True:
            data = _clientSock.recv(args.max_data_recv).decode('utf-8')
            if(data.find('[error]') != -1):
                print(data)
                break
            elif(data.find('[exit]') != -1):
                break
            elif(len(data) == 0):
                break
            else:
                print(data, end=' ')
                if(parent):
                    parent.textBrowser.append(data)

        print('connection closed')
        _clientSock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--user', type=int, default=-1)
    parser.add_argument('--username', type=str, default='xxx')
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatClient = ChatClient(None, args)
