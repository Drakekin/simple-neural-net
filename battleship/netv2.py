from __future__ import division

import math
import random
from util import clamp, count
from faker import Faker


names = Faker()


class Connection(object):
    __slots__ = [
        "_source", "_output", "weight"
    ]

    def __init__(self, source, output):
        self._source = source
        self._output = output
        self._output.add_input(self)
        self.weight = 0

    @property
    def identity(self):
        return self._source.identity, self._output.identity

    @property
    def value(self):
        return self._source.value * self.weight

    @property
    def last_changed(self):
        return self._source.last_changed

    def mutate(self, rng, mutation_rate=0.015):
        if rng.random() <= mutation_rate:
            self.weight = clamp(self.weight + rng.uniform(-1, 1), -1, 1)


class Node(object):
    __slots__ = [
        "identity", "_value", "last_changed", "_inputs"
    ]

    def __init__(self, identity):
        self.identity = identity
        self._value = 0
        self.last_changed = 0
        self._inputs = []

    def add_input(self, connection):
        if connection not in self._inputs:
            self._inputs.append(connection)

    @property
    def value(self):
        raise NotImplemented()


class Sensor(Node):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value_):
        self._value = value_
        self.last_changed += 1

    def add_input(self, connection):
        raise NotImplementedError("Sensors do not have inputs")


class Neuron(Node):
    def __init__(self, identity):
        super(Neuron, self).__init__(identity)
        self._inputs_last_changed = []

    @staticmethod
    def activation_function(value):
        raise NotImplementedError()

    @property
    def value(self):
        inputs_last_changed = [i.last_changed for i in self._inputs]
        if not inputs_last_changed == self._inputs_last_changed:
            self._value = self.activation_function(sum(c.value for c in self._inputs))
            self._inputs_last_changed = inputs_last_changed
            self.last_changed += 1
        return self._value


class LogSigmoidNeuron(Neuron):
    @staticmethod
    def activation_function(n):
        return 1.0 / (1 + (math.e ** (-9.21024*n)))


class Network(object):
    def __init__(self, inputs, *layers, **kwargs):
        neuron_class = kwargs.get("neuron_class", LogSigmoidNeuron)
        identifier = count()

        self.name = names.name()

        self.layers = [[Sensor(next(identifier)) for _ in range(inputs)]]
        self.connections = {}

        for layer in layers:
            n_layer = [neuron_class(next(identifier)) for _ in range(layer)]
            for output in n_layer:
                for source in self.layers[-1]:
                    connection = Connection(source, output)
                    self.connections[connection.identity] = connection
            self.layers.append(n_layer)

    def initialise(self, rng):
        for connection in self.connections.itervalues():
            connection.mutate(rng, mutation_rate=1)

    def cross(self, rng, *parents):
        parent_connections = {k: [p.connections[k] for p in parents] for k in self.connections}
        for connection, candidates in parent_connections.iteritems():
            self.connections[connection].weight = rng.choice(candidates).weight
            self.connections[connection].mutate(rng)

    def clone(self):
        new_network = Network(*[len(layer) for layer in self.layers])
        new_network.name = self.name
        for hash_, connection in new_network.connections.iteritems():
            connection.weight = self.connections[hash_].weight
        return new_network

    def reset(self):
        for input_ in self.inputs:
            input_.value = 0

    @property
    def inputs(self):
        return self.layers[0]

    @property
    def outputs(self):
        return self.layers[-1]

    def input(self):
        return [n.value for n in self.inputs]

    def output(self):
        return [n.value for n in self.outputs]


class Trainer(object):
    def __init__(self, fitness_function, class_size, network_parameters,
                 cream, rng=random):
        self.network_parameters = network_parameters
        self.class_size = class_size
        self.fitness_function = fitness_function
        self.cream = cream
        self.best = None
        self.rng = rng

        self.stable = []
        for _ in range(self.class_size):
            print "Seeding network", _, "of", self.class_size
            network = Network(*self.network_parameters)
            network.initialise(self.rng)
            self.stable.append(network)

    def run_round(self, task):
        results = []
        for network in self.stable:
            results.append((network, task(network)))
            network.reset()

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
        for _ in range(self.class_size):
            new_network = Network(*self.network_parameters)
            new_network.cross(*cream)
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



