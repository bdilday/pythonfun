import argparse
import copy
from collections import defaultdict
import sys


class BirthdayCounter:
    @staticmethod
    def generate_next_state(state):
        for state_idx in range(len(state)):
            if state[state_idx] >= 1:
                tmp = list(copy.deepcopy(state))
                tmp[state_idx] -= 1
                tmp[min(len(state) - 1, state_idx + 1)] += 1
                yield {"state": tuple(tmp), "prob": state[state_idx] / sum(state)}

    @staticmethod
    def get_next_prob(state_probs):
        next_solution_prob = defaultdict(float)
        for old_state, old_state_prob in state_probs.items():
            for new_state in BirthdayCounter.generate_next_state(old_state):
                next_solution_prob[new_state["state"]] += (
                    old_state_prob * new_state["prob"]
                )
        return next_solution_prob


def _parse_args(args):
    parser = argparse.ArgumentParser(
        "Probability to have at least 1 shared birthday by N people"
    )
    parser.add_argument(
        "--slots",
        "-s",
        help="number of slots (i.e. days in a year)",
        required=False,
        default=365,
        type=int,
    )
    parser.add_argument(
        "--target",
        "-t",
        help="number of shared birthdays to track",
        required=False,
        default=2,
        type=int,
    )
    parser.add_argument(
        "--probability-threshold",
        "-p",
        help="probability thtreshold at which to stop",
        required=False,
        default=0.5,
        type=float,
    )
    return parser.parse_args()


def main():
    args = _parse_args(sys.argv[1:])
    bc = BirthdayCounter()
    d = defaultdict(float)
    initial_state = tuple([args.slots] + [0] * args.target)
    d[initial_state] = 1
    solution_prob = 0.0
    total_persons = 0
    while solution_prob < args.probability_threshold:
        total_persons += 1
        solution_prob = 0.0
        d = bc.get_next_prob(d)
        for state, prob in d.items():
            if state[-1] > 0:
                solution_prob += prob
        print(total_persons, solution_prob)


if __name__ == "__main__":
    main()
