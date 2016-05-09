from socket import *


class ChatClient(object):
    def __init__(self, name, password, host, port=8080):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((host, port))

        # Sending user
        r_user = self.s.recv(1024).decode('utf-8')
        if 'user'.find(r_user):
            self.s.send(name.encode())
            print('Username has been sent as: ', name)

        # Sending password
        r_thepass = self.s.recv(1024).decode('utf-8')
        if 'password'.find(r_thepass):
            self.s.send(password.encode())
            print('Password has been sent')

        # Getting users
        self.s.send('-get_users'.encode())
        print(self.s.recv(2048).decode('utf-8'))

    def send(self, msg):
        if not isinstance(msg, str):
            raise AttributeError('Message must be an str')
        return self.s.send(msg.encode())

    def rec(self):
        return self.s.recv(2048).decode('utf-8')


def main():
    a = ChatClient(input('Name: '), input('Password: '), gethostname())
    while True:
        a.send(input())
        print(a.rec())

if __name__ == '__main__':
    main()
