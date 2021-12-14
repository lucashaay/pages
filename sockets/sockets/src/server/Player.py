from uuid import uuid4
import logging

class Player(object):
    __players_list = {} 
    CREATED = 0
    IN_MATCH = 5
    WINNER = 6
    LOSER = 7
    DISCONNECTED = 10

    def __init__(self, conn=None):
        self.id = str(uuid4())
        self._match_id = None 
        self.status = Player.CREATED
        self.conn = conn

        Player.__players_list[str(self.id)] = self
        self._log = logging.getLogger(__name__)
        self._log.debug(f'Player:{self.id} criado.')
    
    @property
    def match_id(self):
        return self._match_id
    
    @match_id.setter
    def match_id(self, m_id):
        self._match_id = m_id
        if m_id:
            self.status = Player.IN_MATCH

    def is_in_match(self):
        return not self.match_id is None

    def disconnect(self):
        """Desconecta da partida o player
        
        Remove o id da partida e o registro do 
        player na classe
        """
        self.match_id = None
        self.status = Player.DISCONNECTED
        del Player.__players_list[self.id]

    def __str__(self):
        return str(self.id)
    
    def __eq__(self, p):
        return self.id == p.id

    @staticmethod
    def get_by_id(_id):
        if _id in Player.__players_list:
            return Player.__players_list[_id]
        else:
            return None
    
    @staticmethod
    def clear_players():
        Player.__players_list = {}