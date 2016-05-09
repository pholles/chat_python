#!/usr/bin/python3
from socket import *
from threading import Thread
from chat import User
from datetime import datetime


class ChatServer(Thread):
    def __init__(self, port, host=gethostname()):
        Thread.__init__(self)
        self.port, self.host = port, host
        self.s = socket(AF_INET, SOCK_STREAM)
        self.users = []

        self.s.bind((self.host, self.port))
        self.s.listen()

        self.users.append(User(self.host, self.port, 'server', 'no'))
        print('Server is online on port: ', self.port)

        # test
        self.connections = []

    def exit(self):
        self.s.close()

    def get_users(self):
        list_users = 'Users: ['
        for i in self.users:
            list_users += i.__str__() + '\n'
        list_users += ']'
        return list_users

    def run_thread(self, conn, address):
        user = self.add_user(conn, address)
        print('User :', user, datetime.strftime(datetime.now(), '%H:%M:%S'))
        while True:
            data = conn.recv(4096).decode('utf-8')
            print(data)
            if data == '-get_users':
                conn.sendall(self.get_users().encode())
            msg = user.name + datetime.strftime(datetime.now(), '%H:%M: ') + data
            self.send_to_other_clients(msg, conn)
            conn.sendall(msg.encode())
        conn.close()

    def send_to_other_clients(self, msg, conn):
        for c in self.connections:
            if c != conn:
                c.sendall(msg.encode())
                print('Sent for', str(c))

    def add_user(self, conn, address):
        conn.send(b'user:')
        name = conn.recv(1024).decode('utf-8')
        conn.send(b'password:')
        password = conn.recv(1024).decode('utf-8')

        user = User(address[0], address[1], name, password)
        self.users.append(user)

        print(self.get_users())

        return user

    def run(self):
        print('Waiting for connections...')
        while True:
            conn, address = self.s.accept()
            print('Connected to login with: ', address[0], ':', address[1])
            self.connections.append(conn)
            Thread(target=self.run_thread, args=(conn, address)).start()


def main():
    server = ChatServer(8080)
    server.run()


if __name__ == '__main__':
    main()
