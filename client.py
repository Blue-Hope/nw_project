import os, sys
import _thread
import time
from socket import *
import argparse

class ChatClient():
    closed = False

    def __init__(self, parent, args):
        super().__init__()
        self.main(parent, args)

    def main(self, parent, args):
        if(args.username == ''):
            print("invalid username, assign --username [username]. (user_id cannot be blanked)")

        try:
            if args.cli == 1:
                destinationAddr = '127.0.0.1'
            else:
                destinationAddr = '13.125.249.160'

            clientSock = socket(AF_INET, SOCK_STREAM) # TCP
            clientSock.connect((destinationAddr, args.port)) # localhost
            clientSock.send(('###STARTCONNECT###' + args.username).encode('utf-8'))

            udpSock = socket(AF_INET, SOCK_DGRAM)
            udpSock.bind(('', args.port + args.user))

            _thread.start_new_thread(self.send_thread, (parent, clientSock, args))
            _thread.start_new_thread(self.recv_thread, (parent, clientSock, args))
            _thread.start_new_thread(self.udp_thread, (parent, udpSock, args))

            if args.cli == 1:
                try:
                    while True:
                        time.sleep(1)
                        if self.closed:
                            break
                        pass
                except KeyboardInterrupt:
                    clientSock.send('###EXIT###'.encode('utf-8'))
                    self.printmsg(parent, '[SYSTEM] connection closed')
                    clientSock.close()
                    sys.exit()


        except OSError as e:
            if(str(e).find("[Errno 61]") != -1):
                data = "[SYSTEM] check if server is turned on"
                self.printmsg(parent, data)


    def send_thread(self, parent, _clientSock, args):
        while True:
            if(parent):
                if not parent.messageQueue.qsize():
                    input_str = parent.messageQueue.get()
                    if input_str == 'exit':
                        _clientSock.send('###EXIT###'.encode('utf-8'))
                        break
                    elif input_str.find("###") != -1:
                        self.printmsg(parent, "you can't use ### in your input")
                    else:
                        try:
                            _clientSock.send(("###DATA###" + input_str.split(' ')[0] + "#" + input_str.split(' ', 1)[1]).encode('utf-8'))
                            self.printmsg(parent, "[you] " + input_str.split(' ', 1)[1])
                        except:
                            self.printmsg(parent, "[SYSTEM] please enter (username + one blank + message)")
            else:
                input_str = input("")
                if input_str == 'exit':
                    _clientSock.send('###EXIT###'.encode('utf-8'))
                    break
                elif input_str.find("###") != -1:
                    print("you can't use ### in your input")
                else:
                    _clientSock.send(('###DATA###' + input_str.split(' ')[0] + "#" + input_str.split(' ', 1)[1]).encode('utf-8'))

        _clientSock.close()
        self.closed = True
        sys.exit()

    def recv_thread(self, parent, _clientSock, args):
        while True:
            try:
                data = _clientSock.recv(args.max_data_recv).decode('utf-8')
            except OSError as e:
                break
            if(data.find('###ERROR###') != -1):
                self.printmsg(parent, '[SYSTEM] ' + (data.split('###ERROR###')[1]))
                break
            elif(data.find('###WARNING###') != -1):
                self.printmsg(parent, '[SYSTEM] ' + (data.split('###WARNING###')[1]))
            elif(len(data) == 0):
                break
            else:
                if data.find('###CONNECTSUCCESS###') != -1:
                    self.printmsg(parent, ('[SYSTEM] ' + args.username + ' is successfully connected'))
                    parent.pushButton.setText(args.username)
                    parent.pushButton.setEnabled(False)
                else:
                    self.printmsg(parent, data)

        self.printmsg(parent, '[SYSTEM] connection closed')
        _clientSock.close()
        self.closed = True
        sys.exit()


    def printmsg(self, parent, msg):
        print(msg)
        if(parent):
            parent.textBrowser.append(msg)
            parent.textBrowser.verticalScrollBar().setValue(10000) #try input different high value

    def udp_thread(self, parent, _udpSock, args):
        while True:
            data, address = _udpSock.recvfrom(args.max_data_recv)
            if(parent):
                parent.textBrowser.append(data.decode('utf-8'))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', type=int, default=0)
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--username', type=str, default='')
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatClient = ChatClient(None, args)
