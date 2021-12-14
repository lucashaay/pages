import re

class Game(object):
    def __init__(self):
        self._board = []
        self.started = False
        self.my_turn = None

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, b):
        groups = re.search(r"\['([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])', ?'([#XO])'\]",
                            b)
        board = []
        for i in range(1, 10):
            e = groups.group(i)
            if e == '#': e = ' '
            board.append(e)
        self._board = board

    def print_board(self):
        b = self.board
        for i in range(3):
            print(f'\n\t {b[i*3]} | {b[i*3+1]} | {b[i*3+2]} ')
            if i != 2:
                print('\t'+'-'*11)
    

if __name__ == '__main__':
    g = Game()
    g.board = "['O', 'X', 'O', ' ', 'O', ' ', ' ', 'X', ' ']"
    g.print_board()