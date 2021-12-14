import pytest
from src import Player
from src.MatchManager import MatchManager 


def test_create_private():
    manager = MatchManager()
    
    p1 = Player()

    r1 = manager.create(p1, 'foo', '123')
    r2 = manager.create(p1, 'foo', '123')

    assert r1 == True
    assert r2 == False


def test_enter_private():
    manager = MatchManager()
    
    p1 = Player()
    p2 = Player()

    manager.create(p1, 'foo', '123')
    r1 = manager.join(p2, 'fo', '123')
    r2 = manager.join(p2, 'foo', '123')

    assert r1 == False
    assert r2 == True
