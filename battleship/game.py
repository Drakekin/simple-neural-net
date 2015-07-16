from collections import defaultdict
from random import randint, choice
import math


def in_board((x, y)):
    return 0 <= x < 10 and 0 <= y < 10


class BattleshipBoard(object):
    LETTERS = list("ABCDEFGHIL")

    def __init__(self):
        board = defaultdict(lambda: None)
        ships_sizes = [5, 4, 3, 3, 2]
        ships = []
        for ship_size in ships_sizes:
            ship = []
            while not ship or not (all([in_board(p) for p in ship]) and all([board[p] is None for p in ship])):
                startx = randint(0, 9)
                starty = randint(0, 9)

                if choice((True, False)):
                    ship = [(startx, starty + n) for n in range(ship_size)]
                else:
                    ship = [(startx + n, starty) for n in range(ship_size)]

            ship = {p: True for p in ship}
            for point in ship:
                board[point] = ship
            ships.append(ship)

        self.board = board
        self.misses = set()
        self.ships = ships

    def hit_coord(self, location):
        x, y = location
        y = int(y) - 1
        x = self.LETTERS.index(x.upper())
        return self.hit((x, y))

    def hit_n(self, n):
        y = int(math.floor(n / 10))
        x = n % 10
        return self.hit((x, y))

    def hit(self, location):
        assert in_board(location)
        if self.board[location] is not None:
            self.board[location][location] = False
            if all([not p for p in self.board[location].itervalues()]):
                return len(self.board[location])
            return "h"
        self.misses.add(location)
        return "m"

    def board_list(self):
        return list(self.board_generator())

    def board_generator(self):
        for y in range(10):
            for x in range(10):
                yield self.board[x, y]

    def won(self):
        return all([all([not p for p in ship.itervalues()]) for ship in self.ships])

    def ships_sunk(self):
        return [1.0 if all([not p for p in ship.itervalues()]) else 0.0 for ship in self.ships]

    def __str__(self):
        board = ["   A B C D E F G H I L"]
        for y in range(10):
            line = str(y + 1) + (" " if y != 9 else "")
            for x in range(10):
                marker = "." if (x, y) in self.misses else " "
                if self.board[x, y]:
                    if self.board[x, y][x, y]:
                        marker = str(len(self.board[x, y]))
                    else:
                        marker = "X"
                line += " " + marker
            board.append(line)
        return "\n".join(board)


if __name__ == "__main__":
    board = BattleshipBoard()
    print board.ships
    while not board.won():
        print board
        coords = raw_input("> ")
        try:
            print board.hit_coord(coords)
        except:
            print "Must be in form A6"

