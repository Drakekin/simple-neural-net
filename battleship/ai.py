# coding=utf-8
from __future__ import division

import math

from battleship.trainer import Trainer
from battleship.game import BattleshipBoard


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
        chances = network.output()
        options = filter(lambda (n, c): n not in hit, enumerate(chances))
        target, chance = max(options, key=lambda (n, c): c)

        result = board.hit_n(target)

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
    return turns

def battleship_trainer(network):
    games = 5

    print "Playing", network.name, "for", games, "rounds"
    score = sum(map(play_battleships, [network] * games)) / games
    print network.name, "scored an average of", score
    return score


if __name__ == "__main__":
    parameters = (105, 110, 100)
    print "Creating trainer"
    trainer = Trainer(lambda n: -n, 20, parameters, 3)
    print "Creating training function"
    print "Starting training"
    trainer.train(battleship_trainer, 5)

    best, score = trainer.best
    print "Winning network won in an average of", score, "turns"
