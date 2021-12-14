import re
from MatchManager import match_manager
from Player import Player
import logging


class Parser(object):
    JOIN = 'JOIN'
    CREATE = 'CREATE'
    MOVE = 'MOVE'
    DISCONNECT = 'DISCONNECT'
    MATCH_STATUS = 'MATCH_STATUS'
    COMMANDS = [JOIN, CREATE, MOVE, DISCONNECT,
                MATCH_STATUS]

    SEPARATOR = ' '

    def __init__(self, disconnect_func=None):
        self._handlers = {
            Parser.JOIN: self._handle_join,
            Parser.CREATE: self._handle_create,
            Parser.MOVE: self._handle_move,
            Parser.DISCONNECT: self._handle_disconnect,
            Parser.MATCH_STATUS: self._handle_match_status,
        }
        self._log = logging.getLogger(__name__)
        self.__disconnect = disconnect_func

    def __try_create_match(self, m_id, password):
        if not match_manager.match_exists(m_id):
            p = Player()
            match_manager.create(p, m_id, password)
            return f'OK player_id={p.id}'
        else:
            return 'NAME_IN_USE'

    def __try_join_match(self, m_id, password):
        p = Player() 
        done = match_manager.join(p, m_id, password)
        if done:
            self._log.debug('Handle join: Joined match.')
            return f'OK player_id={p.id}'
        else: 
            return 'FAILED'
        
    def __assert_private_match_args(self, args):
        if not 'match_id' in args: 
            return 'Id da partida faltando.'
        if not 'password' in args: 
            return 'Senha faltando.'
        if not 'player_id' in args:
            return 'Id do player faltando.'
        if args['player_id'] != '#':
            return 'O Player ja esta em uma partida.'
        return 1

    def __assert_move_args(self, args):
        if not 'player_id' in args: 
            return 'Player id missing.'
        if not 'pos' in args: 
            return 'Position id missing.'
        pos = re.search(r'\(([0-2]), ?([0-2])\)', args['pos'])
        if not pos:
            return 'Invalid position format. Expected: (x, y)'
        args['pos'] = (int(pos.group(1)), int(pos.group(2)))
        return 1

    def _format_args(self, args_list):
        self._log.debug(f'Formatando: {args_list}')
        args = {}
        for a in args_list:
            tmp = a.split('=')
            args[tmp[0]] = tmp[1]
        return args

    def _handle_join(self, args):
        tmp = self.__assert_private_match_args(args)
        if tmp != 1:
            self._log.debug(f'Handle join: {tmp}')
            return f'ERROR {tmp}'
        
        return self.__try_join_match(args['match_id'],
                                     args['password'])

    def _handle_create(self, args):
        """Cria uma nova partida
        """
        tmp = self.__assert_private_match_args(args)
        if tmp != 1: 
            self._log.debug(f'Handle create: {tmp}')
            return f'ERROR {tmp}'

        return self.__try_create_match(args['match_id'],
                                        args['password'])

    def _handle_move(self, args):
        tmp = self.__assert_move_args(args) 
        if tmp != 1:
            self._log.debug(f'Handle Move: {tmp}')
            return f'ERROR {tmp}'

        p = Player.get_by_id(args['player_id'])
#        if p.status == Player.LOSER:
#            return 'LOSER'

        m = match_manager.get_match(p.match_id)
        if m.move(p, args['pos']):
#            if p.status == Player.WINNER:
#                return f'WINNER board={m.board}'
#            else:
            return 'OK'
        else:
            return 'INVALID_MOVE'

    def _handle_match_status(self, args):
        if not 'player_id' in args:
            message = 'Id do player faltando.'
            self._log.debug('Handle match: {message}')
            return f'Error {message}'
        p = Player.get_by_id(args['player_id'])
        m = match_manager.get_match(p.match_id)
        return 'STATUS started={} winner={} my_turn={} board={}'.format(
            m.started(), m.winner, m.is_players_turn(p), m.board)

    def _handle_disconnect(self, args):
        if not 'player_id' in args:
            message = 'Id do player faltando.'
            self._log.debug(f'Handle match: {message}')
            return f'Error {message}'
        p = Player.get_by_id(args['player_id'])
        if p is None:
            return 'OK'
        done = match_manager.end_match(p.match_id)
        if done:
            if self.__disconnect: self.__disconnect()
            self._log.debug('Handle Discon: Partida terminada.')
            return 'OK'
        else:
            self._log.debug('Handle Discon: Partida não encontrada.')
            return 'OK'

    def parse(self, stream):
        """Recebe e executa um comando
        """
        data = stream.strip().split(Parser.SEPARATOR)
        command = data[0]

        if not command in Parser.COMMANDS: 
            message = f'Invalid command {command}.'
            self._log.debug(f'Parse: {message}')
            return f'ERROR {message}'

        args = self._format_args(data[1:])
        return self._handlers[command](args)
