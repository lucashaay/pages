import socket, threading, logging, traceback
from time import sleep
from Parser import Parser
from Player import Player

HOST, PORT = 'localhost', 1597

class Server(object):

    def __init__(self, host, port):
        self._host = host,
        self._port = port
        self._parser = Parser()
        self._socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self._socket.bind((host, port))
        self._log = logging.getLogger('SERVER')

    def _run(self):
        self._socket.listen()
        self._log.info(f'Escutando em {self._host[0]}:{self._port}.')
        while True:
            conn, address = self._socket.accept()
            self._log.info(f'Aceitando conexão de {address}')
            t = threading.Thread(
                    target=self._handle_connection,
                    args=(conn, address),
                    daemon=True)
            t.start()

    def _handle_connection(self, conn, address):
        try:
            while True:
                data = (conn.recv(1024).decode())
                if len(data) == 0:
                    break
                else:
                    self._log.debug(f'RECEBIDO: {data} de {address} ')
                    response = self._parser.parse(data)
                    self._log.debug(f'ENVIADO: {response} para {address}')
                    conn.send(response.encode())
                    if data.startswith(Parser.DISCONNECT):
                        break
        except Exception:
            self._log.debug(traceback.format_exc())
        finally:
            self._log.info(f'DESCONEXÃO: {address}.')
            conn.close()

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            pass
        except Exception:
            self._log.debug(traceback.format_exc())
        finally:
            self._socket.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)-8s]:%(name)s::%(message)s'
        )
    s = Server(HOST, PORT)
    s.run()
