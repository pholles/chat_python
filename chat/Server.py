#!/usr/bin/python3
from socket import *
from threading import Thread
from chat import User
from datetime import datetime

log_file = 'Log_Server.log'


class ChatServer(Thread):
    #  inicializa as variaveis
    def __init__(self, port, host=gethostname()):
        Thread.__init__(self)
        self.port, self.host = port, host
        self.s = socket(AF_INET, SOCK_STREAM)
        self.users = []
        try:
            self.s.bind((self.host, self.port))
        except OSError:
            print('Nao foi possivel realizar bind no socket!\nTente outra porta')
            input('Digite para sair')
            exit()
        self.s.listen()

        self.users.append(User(self.host, self.port, 'server', 'no'))
        print('Server is online on port: ', self.port)

        #  test
        #  abriga as conexoes ativas para poder enviar
        self.connections = []
        self.log_message = 'On Server:' + self.host + ':' + str(self.port) + '\n'
        # self.log_file = log_file

    def exit(self):
        self.s.close()

    def get_users(self):
        self.log_generator('get-users-perform')
        list_users = 'Users: \n['
        for i in self.users:
            list_users += i.__str__() + '\n'
        list_users += ']'
        return list_users

    def run_thread(self, conn, address):
        #  add new user
        user = self.add_user(conn, address)

        #  add event on log
        self.log_generator('New user:' + str(user))
        i = 0

        while True:
            try:
                #  Rec an information
                data = conn.recv(4096).decode('utf-8')
                s = '<<Server Incoming>> ' + str(user) + ':\n[' + data + ']'
                self.log_generator(s)

                #  identify command
                if data == '-get_users':  # requisicao de lista de usuarios
                    conn.sendall(self.get_users().encode())
                    continue
                elif data == '-exit':  # sair
                    s = 'Exit user: ' + user.name
                    self.log_generator(s)
                    self.send_to_other_clients(user.name + ': get out', conn)
                    break

                #  format the string and send it for others
                msg = user.name + datetime.strftime(datetime.now(), '%H.%M : ') + data
                self.send_to_other_clients(msg, conn)
                # conn.sendall(msg.encode()) #  if method isn't working use this
            except ConnectionError:
                self.log_generator('Connection Error: ' + str(user))
                break
            finally:
                print('While on ' + str(i))
                i += 1
                if i > 5:
                    self.log_file_saver()

        #  When the while stops: remove the user and close connection
        self.users.remove(user)
        try:
            conn.close()
        except AssertionError:
            self.log_generator('Erro ao fechar conexao')
        self.log_file_saver()

    def send_to_other_clients(self, msg, conn) -> object:
        for c in self.connections:
            if c != conn:
                try:
                    c.sendall(msg.encode())
                    print('Sent for', str(c))
                except(ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
                    print('Message not sent to conn: ')

    #  Rec and add an user to the list
    def add_user(self, conn, address) -> User:
        name, password = 'no_identify_Thread_' + str(self.ident), 'a'
        try:
            conn.send(b'user:')
            name = conn.recv(1024).decode('utf-8')
            conn.send(b'password:')
            password = conn.recv(1024).decode('utf-8')
        except(ConnectionAbortedError, ConnectionError):
            s = 'Falha ao autenticar'
            self.log_generator(s)

        #  Create user object and add to the list
        user = User(address[0], address[1], name, password)
        self.users.append(user)

        print(self.get_users())

        return user

    def run(self):
        print('Waiting for connections...')
        while True:
            try:
                #  aceita conexao e salva informacaoes nas variaves conn e address
                conn, address = self.s.accept()
                self.log_generator('Connected with: ' + str(address[0]) + ':' + str(address[1]))
                try:
                    #  adiciona conexao e lanca thread para permancer conectado
                    self.connections.append(conn)
                    Thread(target=self.run_thread, args=(conn, address)).start()
                except (ConnectionAbortedError, ConnectionError, Exception):
                    self.log_generator('Erro ao criar Thread ou incluir nova conexao')
            except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
                print('Connection error')

    def log_generator(self, msg: str) -> str:
        thread = 'Thread: ' + str(self.ident)
        time = datetime.strftime(datetime.now(), ' %H:%M:%S ')
        s = thread + time + msg + '\n____\n'
        self.log_message += s
        print(s)
        return s

    def log_file_saver(self, file_place: str = log_file):
        try:
            file = open(file_place, mode='a', encoding='utf-8')
            try:
                file.write(self.log_message)
                self.log_message = 'Last log saved at :{0}'.format(datetime.strftime(datetime.now(), ' %H:%M:%S\n'))
            except (SO_ERROR, IOError):
                print('Can not save the log')
            finally:
                file.close()
        except (IOError, AttributeError, SO_ERROR):
            print('Nao foi possivel abrir o arquivo')


def main():
    server = ChatServer(8040)
    server.run()


if __name__ == '__main__':
    main()
