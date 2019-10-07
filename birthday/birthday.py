import argparse
import numpy as np
import pandas as pd
import copy
from scipy.special import gamma, gammaln
from functools import reduce
from collections import defaultdict
from scipy.special import binom
import sys

class HashableDict(defaultdict):
    def __hash__(self):
        return hash(tuple(sorted(list(self.items()))))


class BirthdayCounter:
    def __init__(self, slots):
        self.slots = slots
        self.counter = HashableDict(int)
        self.counter[0] += slots

    @staticmethod
    def next_set(current_set):
        ans = []
        for shared_birthday_count, instance_count in current_set.items():
            tmp = copy.deepcopy(current_set)
            if instance_count > 0:
                tmp[shared_birthday_count] -= 1
                tmp[shared_birthday_count + 1] += 1
                yield tmp

    def get_next_solution_set(self, solution_set):
        next_solution_set = set()
        for old_set in solution_set:
            for new_set in self.next_set(old_set):
                next_solution_set.add(new_set)
        return next_solution_set

    @staticmethod
    def generate_next_state(state):
        for state_idx in range(len(state)):
            if state[state_idx] >= 1:
                tmp = list(copy.deepcopy(state))
                tmp[state_idx] -= 1
                tmp[min(len(state) - 1, state_idx + 1)] += 1
                yield {"state": tuple(tmp), "prob": state[state_idx] / sum(state)}

    def get_next_prob(self, state_probs):
        next_solution_prob = defaultdict(float)
        for old_state, old_state_prob in state_probs.items():
            for new_state in self.generate_next_state(old_state):
                next_solution_prob[new_state["state"]] += (
                    old_state_prob * new_state["prob"]
                )
        return next_solution_prob

    def analyze_set(self, counter_set):
        tmp = (
            pd.DataFrame(
                [self.analyze_counter(counter) for counter in list(counter_set)]
            )
            .rename(
                columns={
                    0: "total_people",
                    1: "max_birthday_counter",
                    2: "multiplicity",
                    3: "arrangements",
                }
            )
            .assign(total_instances=lambda row: row.multiplicity * row.arrangements)
        )
        return tmp.assign(p=tmp.total_instances / tmp.total_instances.sum())

    def analyze_counter(self, counter):
        total_people = sum(k * v for k, v in counter.items())
        set_multiplicity = multinomial(list(counter.values()))
        arr = [k for k, v in counter.items() for _ in range(v)]
        arrangement_multiplicity = int(
            np.exp(
                gammaln(total_people + 1)
                - reduce(float.__add__, map(lambda x: gammaln(x + 1), arr))
            )
        )
        max_birthday_count = max(
            [
                birthday_counter
                for birthday_counter, instance_count in list(counter.items())
                if instance_count > 0
            ]
        )

        return (
            total_people,
            max_birthday_count,
            set_multiplicity,
            arrangement_multiplicity,
        )


#        pd.DataFrame([bc.analyze_counter(j) for j in list(x)]).rename(columns={0: "total_people", 1: "max_birthday_counter", 2: "multiplicity"})

#  Counter({(3,): 3, (2, 1): 12, (1, 2): 6, (1, 1, 1): 6})
# 3, 18, 6

# https://stackoverflow.com/questions/46374185/does-python-have-a-function-which-computes-multinomial-coefficients
def multinomial(params):
    if len(params) == 1:
        return 1
    return binom(sum(params), params[-1]) * multinomial(params[:-1])


def multiplicity(arr):
    numer = gammaln(np.sum(arr) + 1)
    denom = reduce(float.__add__, map(lambda x: gammaln(x + 1), arr))
    return int(np.exp(numer - denom))


def update_prob(d):
    ans = defaultdict(float)
    for k, v in d.items():
        pass


def next_viable(last_viable):
    new = set()
    old = copy.deepcopy(last_viable)
    for arr in last_viable:
        for i in range(len(arr)):
            tmp = list(copy.deepcopy(arr))
            tmp[i] += 1
            new.add(tuple(tmp))
    return new


def all_viable(target, num_slots):
    s = ([0] * num_slots,)
    ans = {0: copy.deepcopy(s)}
    for i in range(10):
        s = next_viable(s)
        ans[(i + 1)] = copy.deepcopy(s)
    return ans


def main1():
    target = 3
    num_slots = 365
    bc = BirthdayCounter(num_slots)
    x = set((bc.counter,))
    for _ in range(300):
        df = bc.analyze_set(x)
        print(
            df.total_people.iloc[0],
            df.query(f"max_birthday_counter >= {target}").sum().p,
        )
        x = bc.get_next_solution_set(x)

    return df


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
    bc = BirthdayCounter(args.slots)
    d = defaultdict(float)
    initial_state = tuple([args.slots] + [0]*args.target)
    d[initial_state] = 1
    p = 0.0
    i = 0
    while p < args.probability_threshold:
        i += 1
        p = 0.0
        d = bc.get_next_prob(d)
        for state, prob in d.items():
            if state[-1] > 0:
                p += prob
        print(i, p)


if __name__ == "__main__":
    main()