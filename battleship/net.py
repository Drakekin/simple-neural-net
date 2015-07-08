from __future__ import division

import random
import math
from itertools import combinations


def clamp(n, min_value, max_value):
    return max(min(n, max_value), min_value)


def shuffle(rng, list_):
    return sorted(list_, key=rng.random())


def log_sigmoid(n):
    return 1.0 / (1 + (math.e ** (-9.21024*n)))


class Neuron(object):
    def __init__(self, activation_function, rng, inputs=None, output=None):
        """

        :param inputs: A list of Neurons or Inputs
        :param activation_function: A function that returns a float
        :param rng: A function that obeys the python random interface
        """
        self.inputs = []
        self.output = output
        self.rng = rng
        self.activation_function = activation_function
        self.value = 0

        inputs = inputs if inputs is not None else []
        for input_ in inputs:
            self.add_input(input_)

    def mutate(self, mutation_rate=0.015):
        def _mutate(input_, weight):
            if self.rng.random() <= mutation_rate:
                return input_, clamp(weight + self.rng.uniform(-1, 1), -1, 1)
            return input_, weight

        self.inputs = [_mutate(i, w) for i, w in self.inputs]

    def add_input(self, input_):
        self.inputs.append((input_, 0))
        if input_.output != self:
            input_.set_output(self)

    def set_output(self, output):
        self.output = output
        if self not in self.output.inputs:
            self.output.add_input(self)

    def input_weights(self):
        return [w for i, w in self.inputs]

    def set_weights(self, weights):
        inputs = [i for i, w in self.inputs]
        self.inputs = zip(inputs, weights)

    def update(self):
        inputs = sum(i.value * w for i, w in self.inputs) / len(self.inputs)
        self.value = self.activation_function(inputs)
        if self.output:
            self.output.update()

class Input(object):
    def __init__(self, output=None):
        self.output = output
        self.value = 0

    def set_output(self, output):
        self.output = output
        if self not in self.output.inputs:
            self.output.add_input(self)

    def update(self, input_):
        self.value = input_
        self.output.update()


class Network(object):
    def __init__(self, inputs, outputs, hidden_layers, activation_function, rng):
        """

        :param inputs: The number of inputs
        :param outputs: The number of outputs
        :param hidden_layers: A list of integers, one for each hidden
                              layer, each representing how many neurons
                              to include for that layer
        """

        self.neurons = []
        self.parameters = (inputs, outputs, hidden_layers,
                           activation_function, rng)
        self.rng = rng
        self.activation_function = activation_function

        self.inputs = [Input() for _ in range(inputs)]
        self.hidden_layers = []
        top_layer = self.inputs

        for neurons in hidden_layers:
            layer = [Neuron(activation_function, rng, inputs=top_layer)
                     for _ in range(neurons)]
            self.neurons += layer
            self.hidden_layers.append(layer)
            top_layer = layer

        self.outputs = [Neuron(activation_function, rng, inputs=top_layer)
                        for _ in range(outputs)]
        self.neurons += self.outputs

    def initialise(self):
        for neuron in self.neurons:
            neuron.mutate(1)  # mutate all inputs

    def output(self):
        return [n.value for n in self.outputs]

    def produce_offspring(self, network):
        if self.parameters != network.parameters:
            raise ValueError("Networks must have the same parameters ")

        new_network = Network(*self.parameters)
        neurons = zip(new_network.neurons, zip(self.neurons, network.neurons))

        for neuron, (a, b) in neurons:
            a_weights = a.input_weights()
            b_weights = b.input_weights()
            weights = [self.rng.choice(w) for w in zip(a_weights, b_weights)]
            neuron.set_weights(weights)
            neuron.mutate()

        return new_network


class Trainer(object):
    def __init__(self, fitness_function, class_size, network_parameters,
                 cream, rng=random):
        if math.factorial(cream) < class_size:
            raise ValueError("cream is too small, !cream must be at least class_size")

        self.network_parameters = network_parameters
        self.class_size = class_size
        self.fitness_function = fitness_function
        self.cream = cream
        self.rng = rng

        self.stable = []
        for _ in self.class_size:
            network = Network(*self.network_parameters)
            network.initialise()
            self.stable.append(network)

    def run_round(self, task):
        results = []
        for network in self.stable:
            results.append((network, task(network)))

        ranked_results = sorted(
            results,
            key=lambda (n, r): self.fitness_function(r),
            reverse=True
        )
        cream = ranked_results[:self.cream]
        potentials = combinations(cream, 2)
        parents = self.rng.sample(potentials, self.class_size)
        self.stable = [a.produce_offspring(b) for ((a, _), (b, _)) in parents]

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
            self.run_round(task)

