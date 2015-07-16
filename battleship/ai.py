# coding=utf-8
from __future__ import division

import math

from battleship.trainer import Trainer
from battleship.game import BattleshipBoard
from battleship.util import bar, chunk


def n_to_coord(n):
    y = int(math.floor(n / 10)) + 1
    x = n % 10
    return "{}{}".format(BattleshipBoard.LETTERS[x], y)

def play_battleships(network):
    network.reset()
    board = BattleshipBoard()
    ai_board = network.inputs[:100]
    ai_ships = network.inputs[100:]

    print "Playing", network.name, "at battleships"
    turns = 0
    hit = set()
    while not board.won():
        chances = list(enumerate(network.output()))
        options = filter(lambda (n, c): n not in hit, chances)
        target, chance = max(options, key=lambda (n, c): c)

        outputs = u" ".join(("X" if network.inputs[n].value == 1 else "O") if n in hit else bar(o, 0, 1) for n, o in chances)
        outputs = u"\n".join(chunk(outputs, 20)).encode("utf8")

        result = board.hit_n(target)
        display = str(board)
        yield "Targeted {} ({}% chance)\nOutputs:\n{}\nGot a {}\n{}".format(
            n_to_coord(target), round(chance * 100), outputs, result, display)

        hit.add(target)

        if result == "m":
            ai_board[target].value = -1
        elif result == "h":
            ai_board[target].value = 1
        else:
            ai_board[target].value = 1
            ai_ships[result - 1].value = 1

        turns += 1

    print network.name, "took", turns, "turns"

def battleship_trainer(network):
    games = 5

    print "Training", network.name, "for", games, "rounds"
    score = sum(map(lambda n: len(list(play_battleships(n))), [network] * games)) / games
    print network.name, "scored an average of", score
    return score


if __name__ == "__main__":
    parameters = (105, 103, 100)
    print "Creating trainer"
    trainer = Trainer(lambda n: -n, 20, parameters, 3)
    print "Creating training function"
    print "Starting training"
    trainer.train(battleship_trainer, 5)

    best, score = trainer.best
    print "Winning network won in an average of", score, "turns"
    for move in play_battleships(best):
        print move
        print ""
