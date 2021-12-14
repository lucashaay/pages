import logging
from Player import Player


__all__ = ['Match']

class Match(object):
    EMPTY = '#'
    P1_MARK = 'X'
    P2_MARK = 'O'
    WIN_CONDITIONS = [[0,1,2], [3,4,5], [6,7,8],
                      [0,3,6], [1,4,7], [2,5,8],
                      [0,4,8], [2,5,6]]

    def __init__(self, player, player2=None, password=None):
        self.__psswd_lock = False
        self._turn = Match.P1_MARK
        self.players = [player, player2] if player2 else [player]
        self.winner = None
        self.password = password
        e = Match.EMPTY
        self._board = [e, e, e,
                       e, e, e,
                       e, e, e]
        self._log = logging.getLogger(__name__)

    @property
    def turn(self):
        return self._turn

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, p):
        if p == '' and self.__psswd_lock:
            raise Exception('Password cannot be empty.')
        if not self.__psswd_lock:
            self.__password = p
            self.__psswd_lock = True

    @property
    def board(self):
        b = self._board
        tmp = f"['{b[0]}','{b[1]}','{b[2]}','{b[3]}','{b[4]}',"
        tmp += f"'{b[5]}','{b[6]}','{b[7]}','{b[8]}']"
        return tmp

    def __switch_turn(self):
        x, o = Match.P1_MARK, Match.P2_MARK
        self._turn = x if self._turn == o else o

    def __is_move_valid(self, pos):
        """Retorna True se a posição está vazia
        """
        return self._board[pos] == Match.EMPTY

    def started(self):
        return len(self.players) == 2

    def is_players_turn(self, player):
        p1_turn = (self.turn == Match.P1_MARK and 
                    player == self.players[0])
        p2_turn = (self.turn == Match.P2_MARK and 
                    player == self.players[1])
        return p1_turn or p2_turn

    def join(self, player, password):
        """ Retorna True se o player2 conseguir entrar na partida
        """
        if len(self.players) == 2: 
            self._log.debug(
                f'A partida já tem dois players {self.players}. \
                  Player {player} negado.')  
            return False
        elif player == self.players[0]:
            self._log.debug(
                f'O criador ({player}) tentou se juntar a partida.')
            return False
        if password == self.password:
            self.players.append(player)
            self._log.debug(
                f'Players: {self.players[0]}, {self.players[1]}')
            return True
        else:
            self._log.debug(f'Errou a senha. Player: {player} '+
                f'tentada: {password} correta: {self.password}')
            return False

    def move(self, player, pos):
        pos = self.__convert_pos(pos) 
        if self.is_players_turn(player) and \
        self.__is_move_valid(pos):
            self._board[pos] = self.turn
            self._check_win()
            self.__switch_turn()
            return True
        self._log.debug(
            f'Movimento falhou player:{player}, vez:{self.turn}, '+
            f'movimento:({pos}), tabuleiro:{self._board}')
        return False

    def __convert_pos(self, pos):
        x, y = pos
        return x*3+y

    def _check_win(self):
        bd = self._board
        for a, b, c in Match.WIN_CONDITIONS:
            if bd[a] == bd[b] == bd[c] == Match.P1_MARK:
                self.winner = self.players[0]
            elif bd[a] == bd[b] == bd[c] == Match.P2_MARK:
                self.winner = self.players[1]

    def end(self):
        """Finaliza a partida e desconecta os players
        """
        self._log.debug('Partida finalizada.')
        for p in self.players: p.disconnect()
        self.players = []