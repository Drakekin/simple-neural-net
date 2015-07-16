from random import Random

from battleship.network import Network


def test_crossing_networks():
    network_params = (10, 7, 4)
    net1 = Network(*network_params)
    net2 = Network(*network_params)

    rng = Random("tests")
    net1.initialise(rng)
    net2.initialise(rng)

    net3 = Network(*network_params)
    net3.cross(rng, net1, net2)


if __name__ == "__main__":
    test_crossing_networks()
