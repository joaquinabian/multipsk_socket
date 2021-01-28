# Joaquin Abian diciembre 2017
# Conecta por TCP/IP con MultiPsk leyendo lo que el programa decodifica
# Va salvando el texto en un archivo en paquetes de 5000 chars


import socket
import os
from threading import Thread
from easygui import ynbox, enterbox


def acquire(sock, archive, stop):
    print('acquiring')
    while True:
        amount_received = 0
        amount_expected = 5000

        try:
            chunks = []
            # Look for the response
            while amount_received < amount_expected:
                data = sock.recv(1024)
                n = len(data)    # normally n=
                # each character received by Multipsk and transmitted to the
                # client is preceded by the character CHR(29).
                if data and (data[0] == 29):
                    amount_received += n
                    chunks.append(data)
                else:
                    print('no char: ', repr(data))

        finally:
            sentence = b''.join(chunks)
            sentence = sentence.replace(b'\x1d', b'')

            txt = sentence.decode('utf-8', errors='ignore')
            txt = txt.replace('\r', '')
            with open(archive, 'a') as f:
                print(txt, file=f)
            print('saved txt')

        print('checking stop', stop())
        if stop():
            print('closing socket')
            sock.close()
            break


def connect_tcpip(server_address, archive):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    print('connected')

    stop_t = False
    t = Thread(target=acquire, args=(sock, archive, lambda: stop_t))
    t.start()

    ynbox('push anything to stop')

    print('to stop')
    stop_t = True
    t.join()
    print('end')


if __name__ == '__main__':

    PORT = 3122
    URL = '127.0.0.1'

    DIR = os.path.expanduser('~/Desktop')

    name = enterbox('file name to save messages', default='test')
    if name is not None:
        archive = os.path.join(DIR, '%s.txt' % name)

    connect_tcpip((URL, PORT), archive)
