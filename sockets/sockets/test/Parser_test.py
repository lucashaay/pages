import pytest, logging
from src import Parser, Player


def test_parse_create(caplog):
    caplog.set_level(logging.DEBUG)
    parser = Parser()
    message = 'CREATE player_id=# match_id=nova password=123'

    r1 = parser.parse(message)  # OK player_id=something
    r1pid = r1.split('=')
    r2 = parser.parse(message)
    r3 = parser.parse('CREATE')
    r4 = parser.parse('CREATE player_id=# ')
    r5 = parser.parse('CREATE player_id=# match_id=nova')

    assert r1.startswith('OK')
    assert 'player_id=' in r1
    assert '' != r1pid != '#'
    assert r2 == 'NAME_IN_USE'
    assert r3.startswith('ERROR')
    assert r4.startswith('ERROR')
    assert r5.startswith('ERROR')


def test_parse_join():
    parser = Parser()
    message = 'CREATE player_id=# match_id=nova password=123'
    parser.parse(message)

    message = 'JOIN player_id=# match_id=nova password=123'
    r1 = parser.parse(message)
    r1pid = r1.split('=')
    r2 = parser.parse(message)

    assert r1.startswith('OK')
    assert 'player_id=' in r1
    assert '' != r1pid != '#'
    assert r2 == 'FAILED'


def test_parse_move(caplog):
#    caplog.set_level(logging.DEBUG)
    Player.clear_players()
    parser = Parser()
    message = 'CREATE player_id=# match_id=outra password=123'
    pid1 = parser.parse(message).split(' ')[1].split('=')[1]
    message = 'JOIN player_id=# match_id=outra password=123'
    pid2 = parser.parse(message).split(' ')[1].split('=')[1]

    message = 'MOVE player_id={} pos=({},{})'
    r1 = parser.parse(message.format(pid2, 1, 2))  #jogador errado
    r2 = parser.parse(message.format(pid1, 1, 3))  #posição invalida
    r3 = parser.parse(message.format(pid1, 0, 0))
    r4 = parser.parse(message.format(pid2, 0, 0))  #jogada repetida
    r5 = parser.parse(message.format(pid2, 1, 1))

    assert r1 == 'INVALID_MOVE'
    assert r2.startswith('ERROR')
    assert r3 == 'OK'
    assert r4 == 'INVALID_MOVE'
    assert r5 == 'OK'


def test_parse_disconnect():
    parser = Parser()
    message = 'CREATE player_id=# match_id=discon password=123'
    pid = parser.parse(message).split(' ')[1].split('=')[1]

    message = f'DISCONNECT player_id={pid}'
    r = parser.parse(message)

    assert r == 'OK'

