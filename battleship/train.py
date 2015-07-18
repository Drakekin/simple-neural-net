from argparse import ArgumentParser
from random import Random
import os

from battleship.ai import battleship_trainer, battleship_fitness
from snn.trainer import Trainer
from snn.network import Network


def main(args):
    rng = Random(args.seed)
    network_parameters = (105, 103, 100)
    trainer = Trainer(
        battleship_fitness,
        args.class_size,
        network_parameters,
        args.cream,
        rng,
        args.threads
    )

    if args.class_location:
        _, _, files = next(os.walk(args.class_location))
        networks = [os.path.join(args.class_location, f)
                    for f in files if f.endswith(".network")]
        trainer.stable = [Network.load_from_file(f) for f in networks]
    else:
        trainer.spawn_class()

    for n in range(args.rounds):
        print "Beginning round", n
        trainer.run_round(battleship_trainer)
        if args.output_location:
            generation_dir = os.path.join(
                args.output_location,
                "gen_{}".format(max(n.generation for n in trainer.stable))
            )
            os.makedirs(generation_dir)
            for network in trainer.stable:
                network.save_to_file(path=generation_dir)
            network, score = trainer.best
            network.save_to_file(filename="best_gen{}_{}.network".format(
                network.generation, score), path=args.output_location)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--class-size", type=int, default=20,
                        help=("The number of networks to create for each "
                              "generation in the evolutionary simulation."))
    parser.add_argument("--cream", type=int, default=3,
                        help=("The number of networks to select at the end "
                              "of each round to cross to create the next "
                              "class of networks."))
    parser.add_argument("--rounds", type=int, default=5,
                        help=("The number of rounds of evolutionary training "
                              "to run."))
    parser.add_argument("--threads", type=int, default=5,
                        help=("The number of threads in the training thread "
                              "pool."))
    parser.add_argument("--class-location",
                        help=("A path to a directory containing one or more "
                              ".network files to seed the initial class with."))
    parser.add_argument("--output-location",
                        help=("A path to a directory where .network files of "
                              "each class will be saved."))
    parser.add_argument("--seed",
                        help="The seed for the random number generator.")

    main(parser.parse_args())
