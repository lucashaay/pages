from Match import Match
from Player import Player
from uuid import uuid4
import logging

__all__ = ['match_manager', 'MatchManager']

class MatchManager(object):
    def __init__(self):
        self._match_list = {}
        self._log = logging.getLogger(__name__)

    def match_exists(self, _id):
        return _id in self._match_list

    def get_match(self, _id):
        if not self.match_exists(_id): return None
        return self._match_list[_id]
    
    def create(self, player, _id, password):
        """Cria uma partida privada

        Recebe o player, o id da partida e a senha
        """
        if _id in self._match_list:
            self._log.debug(f'Id da partida ({_id}) já existe.')
            return False
        self._match_list[_id] = Match(player, 
                                        password=password)
        player.match_id = _id
        self._log.debug(f'Player ({player}) criou partida ({_id})')
        return True

    def join(self, player, _id, password):
        """Entra em uma partida privada

        Recebe o player, o id da partida e a senha
        """
        if not self.match_exists(_id):
            return False
        done = self.get_match(_id).join(player, password)
        if done:
            player.match_id = _id
        return done

    def end_match(self, _id):
        if self.match_exists(_id):
           m = self._match_list[_id]
           m.end()
           del self._match_list[_id]
           return True
        else:
            return False


match_manager = MatchManager()