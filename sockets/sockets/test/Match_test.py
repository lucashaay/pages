import pytest, logging
from src import Match, Player

#logging.basicConfig(level=logging.DEBUG, 
#                    format='%(asctime)s %(name)s %(levelname)s:: %(message)s',
#                    filename='./test.log')

def test_password():
    m = Match(1, password='123')
    m.password = '321'
    assert m.password == '123'


def test_join(caplog):
    m = Match(1, password='123')
    
    r1 = m.join(2, '124') # senha incorreta
    r2 = m.join(2, '123') # senha correta
    r3 = m.join(3, '123') # Um player a mais
    r4 = m.join(1, '123') # O mesmo player

    assert r1 == False
    assert r2 == True
    assert r3 == False
    assert r4 == False


def test_move():
#    caplog.set_level(logging.DEBUG)
    p1 = Player()
    p2 = Player()
    m = Match(p1, password='123')
    m.join(p2, '123')

    assert m.move(p2, (0, 0)) == False  # mover fora do turno
    assert m.move(p1, (0, 0)) == True
    assert m.turn == Match.P2_MARK  # troca de turno

    assert m.move(p1, (1, 1)) == False # mover fora do turno
    assert m.move(p2, (1, 1)) == True
    assert m.move(p1, (1, 1)) == False # posição repetida
    assert m.turn == Match.P1_MARK


def test_disconnect():
    p1 = Player()
    p2 = Player()
    m = Match(p1, password='123')
    m.join(p2, '123')
    m.end()

    assert len(m.players) == 0