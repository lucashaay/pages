import socket, re, os
from threading import Thread, Lock
from time import sleep
from Game import Game

HOST, PORT = 'localhost', 1597

class Client(object):
    def __init__(self):
        self.sock = None
        self.player_id = '#'
        self.in_match = False
        self.is_winner = None
        self.lock = Lock()
        self.game = Game()
        self._elpsd_time = 0

    def connect(self):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

    def clear_console(self):
        if os.name == 'nt':
            return os.system('cls')
        else:
            return os.system('clear')

    def send(self, msg):
        self.sock.sendall(str.encode(msg))
        return self.sock.recv(1024).decode()

    def check_match_status(self):
        r = self.send(f'MATCH_STATUS player_id={self.player_id}')
        args = self._get_args(r)
        if args['winner'] == self.player_id:
            self.in_match = False
            self.is_winner = True
        elif args['winner'] != 'None':
            self.in_match = False
            self.is_winner = False
        self.game.started = args['started'] == 'True'
        self.game.my_turn = args['my_turn'] == 'True'
        self.game.board = args['board']

    def _get_args(self, response):
        response = response.split(' ')[1:]
        return self._format_args(response)

    def _format_args(self, args_list):
        args = {}
        for a in args_list:
            tmp = a.split('=')
            args[tmp[0]] = tmp[1]
        return args

    def start(self):
        try:
            self.menu()
        except KeyboardInterrupt:
            pass
        finally:
            self.send(f'DISCONNECT player_id={self.player_id}')
            self.sock.close()

    def menu(self):
        r = None
        while r is None:
            r = self.ask('Deseja criar[1], se juntar a uma partida[2], ou sair[3]?',
                r'[123]')
        if r.group(0) == '3':
            return
        if r.group(0) == '2':
            self.join()
        else:
            self.create()
        self.in_match = True
        self.match()

    def ask(self, message, match):
        option = input(f'{message}\n:: ').strip()
        if option == '': return '\n'
        r = re.search(match, option)
        if not r:
            print('Entrada invalida.')
            return None
        return r

    def create(self):
        while True:
            m_id = input('Nome da partida: ')
            p = input('Senha da partida: ')
            self.connect()
            r = self.send(
            f'CREATE player_id={self.player_id} match_id={m_id} password={p}')
            if r == 'NAME_IN_USE':
                n = input('O nome escolhido já está sendo usando. Digite 1 para tentar de novo\n::')
                if n != '1': break
                continue
            args = self._get_args(r)
            self.player_id = args['player_id']
            break

    def join(self):
        while True:
            m_id = input('Nome da partida: ')
            p = input('Senha da partida: ')
            self.connect()
            r = self.send(
            f'JOIN player_id={self.player_id} match_id={m_id} password={p}')
            if r == 'FAILED': 
                n = input('Nome ou senha incorretos. Digite 1 para tentar de novo.\n::')
                if n != '1': break
                continue
            args = self._get_args(r)
            self.player_id = args['player_id']
            break

    def match(self):
        while True:
            if not self.in_match: break
            if not self.game.started:
                self.check_match_status()
                print('Esperando outro jogador...')
                sleep(2)
                continue
            r = self.make_move()
            if r == 'INVALID_MOVE':
                print('Jogada invalida')
            if r == -1:
                break
        if self.is_winner: 
            print('VOCÊ GANHOU.')
        else:
            print('VOCÊ PERDEU.')

    def update_screen(self):
        print('\n' + '='*30)
        self.check_match_status()
#        self.clear_console()
        self.game.print_board()
        if self.game.my_turn: 
            print('Minha vez\n')
        else:
            print('Vez do outro\n')

    def make_move(self):
        self.update_screen()
        move = self.get_move()
        if move == -1:
            return -1
        elif move == -2:
            pass
        elif type(move) == str:
            if self.game.my_turn:
                r = self.send(f'MOVE player_id={self.player_id} pos={move}')
                return r
            else:
                print('Ainda não é sua vez.')


    def get_move(self):
        move = input('Jogada, enter para atualizar, ou s para sair:: ')
        if move == '':
            return -2
        match = r'([0-2]) ([0-2])|(s)'
        move = re.search(match, move)
        if move:
            if move.group(0) == 's':
                return -1
            else:
                return f'({move.group(1)},{move.group(2)})'
        else:
            return None

    


if __name__ == '__main__':
    c = Client()
    c.start()
