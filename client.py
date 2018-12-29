import socket

from time import time
class ClientError(BaseException):

    '''Класс обработки исключений'''

    pass

class Client:

    '''Класс Клиент'''

    def __init__(self, conn, addr, timeout=None):
        self.conn = conn
        self.addr = addr
        self.timeout = timeout or 0
        
        self.sock = socket.create_connection((self.conn, self.addr), timeout = timeout)

    def put(self, key, value, timestamp=None):

        '''Функция "Пут", отправляющая метрики на сервер'''
        try:
            timestamp = timestamp
            if timestamp == None:
                timestamp = str(int(time()))
            message = 'put' + ' ' + key + ' ' + str(value) + ' ' + str(timestamp) + '\n'
            self.sock.sendall(message.encode('utf8'))
            data = self.sock.recv(1024).decode('utf8')
            if data == 'error\nwrong command\n\n':
                raise ClientError
        except socket.error:
            raise ClientError
        
    def get(self, key):
        
        '''Функция "Гет", принимающая метрики с сервера'''
        try:
            message = 'get'+ ' ' + key + '\n'
            self.sock.sendall(message.encode('utf8'))
            data = self.sock.recv(1024).decode('utf8')
            metrics = {}
            if data == 'ok\n\n':
                return {}
            elif data == 'error\nwrong command\n\n':
                raise ClientError        
            elif key == '*':
                rec1 = data.split('\n')
                for i in rec1[1:-2]:
                    if i.split(' ')[0] not in metrics: 
                        metrics[i.split(' ')[0]] = [(int(i.split(' ')[2]), float(i.split(' ')[1]))] 
                    else:
                        metrics[i.split(' ')[0]].append((int(i.split(' ')[2]), float(i.split(' ')[1])))
                for i in metrics:
                    metrics[i] = sorted(metrics[i], key=lambda x: x[0])
            else:
                rec2 = data.split('\n')
                for i in rec2[1:-2]:
                    if i.split(' ')[0] == key:
                        if i.split(' ')[0] not in metrics: 
                            metrics[i.split(' ')[0]] = [(int(i.split(' ')[2]), float(i.split(' ')[1]))] 
                        else:
                            metrics[i.split(' ')[0]].append((int(i.split(' ')[2]), float(i.split(' ')[1])))
                for i in metrics:
                    metrics[i] = sorted(metrics[i], key=lambda x: x[0])

            return metrics
        except socket.error:
            raise ClientError
