#!/usr/bin/python3
import hashlib
import uuid
import random


class User(object):
    def __init__(self, host, port, name='random', password='password'):
        if name == 'random':
            name = str(random.randint(0, 1000))
        self._name, self._password = '', b''
        self.name, self.password = name, password
        self.host, self.port = host, port

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('Incorrect type of name')
        self._name = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if not isinstance(value, str):
            raise ValueError('Incorrect type of password')
        salt = uuid.uuid4().hex
        self._password = hashlib.sha512(value.encode('utf-8') + salt.encode('utf-8')).hexdigest()

    def __str__(self):
        return '{' + self.name + ' at ' + str(self.host) + ':' + str(self.port) + '}'

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               self.host == other.host and \
               self.port == other.port and \
               self.name == other.name
