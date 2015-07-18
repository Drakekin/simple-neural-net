from __future__ import division

import math
import cPickle
import os.path

from faker import Faker

from snn.util import clamp, count

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
            total_inputs = sum(c.value for c in self._inputs)
            self._value = self.activation_function(total_inputs)
            self._inputs_last_changed = inputs_last_changed
            self.last_changed += 1
        return self._value


class LogSigmoidNeuron(Neuron):
    @staticmethod
    def activation_function(n):
        return 1.0 / (1 + (math.e ** (-9.21024*n)))


class Network(object):
    __slots__ = [
        "first_name", "last_names", "generation",
        "layers", "connections"
    ]

    def __init__(self, inputs, *layers, **kwargs):
        neuron_class = kwargs.get("neuron_class", LogSigmoidNeuron)
        identifier = count()

        self.first_name = names.first_name()
        self.last_names = []
        self.generation = 0

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
        self.last_names.append(names.last_name())
        for connection in self.connections.itervalues():
            connection.mutate(rng, mutation_rate=1)

    def cross(self, rng, *parents):
        parent_connections = {k: [p.connections[k] for p in parents]
                              for k in self.connections}
        self.last_names = [rng.choice(p.last_names) for p in parents]
        self.generation = max(p.generation for p in parents) + 1
        for connection, candidates in parent_connections.iteritems():
            self.connections[connection].weight = rng.choice(candidates).weight
            self.connections[connection].mutate(rng)

    @property
    def name(self):
        return "{} {} (Gen. {})".format(
            self.first_name, "-".join(self.last_names), self.generation)

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

    @classmethod
    def load(cls, pickled_string):
        return cPickle.loads(pickled_string)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, "rb") as pickled_network:
            return cls.load(pickled_network.read())

    def save(self):
        return cPickle.dumps(self, protocol=2)
    
    def save_to_file(self, filename=None, path=None):
        if filename is None:
            filename = "{}_{}-{}.network".format(
                self.first_name, "-".join(self.last_names), self.generation)
        if path is not None:
            filename = os.path.join(path, filename)

        with open(filename, "wb") as pickled_network:
            pickled_network.write(self.save())
