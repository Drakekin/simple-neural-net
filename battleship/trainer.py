import random
from multiprocessing import Pool

from battleship.network import Network


class Trainer(object):
    def __init__(self, fitness_function, class_size, network_parameters,
                 cream, rng=random, threads=5):
        self.network_parameters = network_parameters
        self.class_size = class_size
        self.fitness_function = fitness_function
        self.cream = cream
        self.best = None
        self.rng = rng
        self.pool = Pool(threads)

        self.stable = []
        for _ in range(self.class_size):
            print "Seeding network", _, "of", self.class_size
            network = Network(*self.network_parameters)
            network.initialise(self.rng)
            self.stable.append(network)

    def run_round(self, task):
        results = zip(self.stable, self.pool.map(task, self.stable))
        if self.best:
            results.append(self.best)

        print "Ranking winners"

        ranked_results = sorted(
            results,
            key=lambda (n, r): self.fitness_function(r),
            reverse=True
        )
        best_result = ranked_results[0]
        self.best = best_result
        bn, best = best_result
        wn, worst = ranked_results[-1]

        print "Best score was", best, bn.name
        print "Worst score was", worst, wn.name

        cream = ranked_results[:self.cream]
        cream = [n for n, s in cream]
        print "Selected", len(cream), "best networks"

        new_class = []
        for _ in range(self.cream):
            new_blood = Network(*self.network_parameters)
            new_blood.initialise(self.rng)
            new_class.append(new_blood)
        while len(new_class) < self.class_size:
            new_network = Network(*self.network_parameters)
            new_network.cross(self.rng, *cream)
            new_class.append(new_network)
        self.stable = new_class
        print "Produced", len(self.stable), "new networks"

    def train(self, task, rounds):
        """
        This function takes a function that takes a network and returns an
        object that can be passed to the fitness function to sort networks in
        order of fitness.

        It will pass the network to the task function, a number of times
        equal to the number of rounds. After each round, the top networks
        are selected, paired off to produce a new set of networks and
        rerun.
        """
        for _ in range(rounds):
            print "Starting round", _
            self.run_round(task)
            print
