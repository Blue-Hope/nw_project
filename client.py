import os, sys
import _thread
import time
from socket import *
import argparse

class ChatClient():
    closed = False
    killself = False

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

            _thread.start_new_thread(self.send_thread, (parent, clientSock, args))
            _thread.start_new_thread(self.recv_thread, (parent, clientSock, args))

            if args.cli == 1:
                try:
                    while True:
                        time.sleep(1)
                        if self.closed:
                            break
                        if killself:
                            del self
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
                    input_data = parent.messageQueue.get()
                    input_dest = input_data[0]
                    input_str = input_data[1]
                    input_type = input_data[2]
                    if input_type == 0: #msg
                        if input_str == 'exit':
                            _clientSock.send('###EXIT###'.encode('utf-8'))
                            break
                        elif input_str.find("###") != -1:
                            self.printmsg(parent, "[SYSTEM] you can't use ### in your input")
                        else:
                            try:
                                _clientSock.send(("###DATA###" +  input_dest + "#" + input_str).encode('utf-8'))
                                self.printmsg(parent, "[you -> " + input_dest + "] " + input_str)
                            except:
                                self.printmsg(parent, "[SYSTEM] error in message transfer")
                    elif input_type == 1: #file
                        try:
                            file_path = input_str
                            file_type = file_path.split('.')[-1]
                            diff = args.max_data_recv - len(("###FILE###" + input_dest + "#" + file_type).encode('utf-8'))
                            tmp = ''
                            for i in range(diff):
                                tmp += '\0'
                            _clientSock.send(("###FILE###" + input_dest + "#" + file_type + tmp).encode('utf-8'))
                            length = os.path.getsize(file_path)
                            _clientSock.send(self.convert_to_bytes(length)) # has to be 4 bytes
                            f = open(file_path, 'rb')
                            f_data = f.read(args.max_data_recv)
                            while(f_data):
                                _clientSock.send(f_data)
                                f_data = f.read(args.max_data_recv)
                            f.close()
                            self.printmsg(parent, "[you -> " + input_dest + "] " + input_str)
                        except:
                            self.printmsg(parent, "[SYSTEM] error in file transfer")

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
                data = _clientSock.recv(args.max_data_recv).decode()
            except OSError as e:
                break
            print(data)
            if(data.find('###ERROR###') != -1):
                self.printmsg(parent, '[SYSTEM] ' + (data.split('###ERROR###')[1]))
                self.killself = True
                # break
            elif(data.find('###WARNING###') != -1):
                self.printmsg(parent, '[SYSTEM] ' + (data.split('###WARNING###')[1]))
            elif(data.find('###FILE###') != -1):
                file_type = data.split("###FILE###")[1].rstrip('\0')
                size = _clientSock.recv(4) # assuming that the size won't be bigger then 1GB. get the size of recv file
                size = self.bytes_to_number(size)
                current_size = 0
                buffer = b""
                f = open('download.' + file_type, 'wb')
                i = 1
                while(current_size < size):
                    data = _clientSock.recv(args.max_data_recv)
                    if not data:
                        break
                    if len(data) + current_size > size:
                        data = data[:size-current_size]
                    current_size += len(data)
                    f.write(data)
                f.close()
                print('did')
            elif(len(data) == 0):
                break
            else:
                if data.find('###CONNECTSUCCESS###') != -1:
                    parent.clientOK = True
                    print("data gotten")
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

    def convert_to_bytes(self, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i*8)
        return res



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', type=int, default=0)
    parser.add_argument('--max_data_recv', type=int, default=1460) # byte
    parser.add_argument('--username', type=str, default='')
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatClient = ChatClient(None, args)
