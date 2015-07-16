# coding=utf-8
from __future__ import division

import math
import multiprocessing

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

def battleship_trainer(games=5):
    def train(network):
        print "Playing", network.name, "for", games, "rounds"
        pool = multiprocessing.Pool(games)
        results = pool.map(play_battleships, [network] * games)
        score = sum(results) / games
        print network.name, "scored an average of", score
        return score
    return train


if __name__ == "__main__":
    parameters = (105, 110, 100)
    print "Creating trainer"
    trainer = Trainer(lambda n: -n, 20, parameters, 3)
    print "Creating training function"
    training_function = battleship_trainer(games=3)
    print "Starting training"
    trainer.train(training_function, 5)

    best, score = trainer.best
    print "Winning network won in an average of", score, "turns"
