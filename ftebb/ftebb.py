""" fivethirtyeight baseball puzzle

This code computes exact runs-scored probabilities, using the 
negative binomial distribution and convolutions of the runs-scored
distributions
"""
import argparse
import numpy as np
import pandas as pd
from collections import defaultdict
from scipy.stats import distributions
from functools import partial
import copy
import sys


class ProbDist:
    def __init__(self, success_prob, offset, max_value=20):
        self.success_prob = success_prob
        self.failure_prob = 1 - success_prob
        self.offset = offset
        self.max_value = max_value
        self._prob = None
        self.non_out_pa_prob = partial(
            distributions.nbinom.pmf, n=3, p=self.failure_prob
        )

    @staticmethod
    def prob_stats(prob_dict):
        _mean = sum([k * v for k, v in prob_dict.items()])
        _mean2 = sum([k * k * v for k, v in prob_dict.items()])
        _norm = sum(prob_dict.values())
        return {
            "mean": _mean,
            "std": np.sqrt(_mean2 - _mean * _mean),
            "prob_norm": _norm,
        }

    def _make_prob(self):
        _prob = defaultdict(float)
        for non_out_pa in range(self.max_value):
            run_value = max(0, non_out_pa - self.offset)
            _prob[run_value] += self.non_out_pa_prob(non_out_pa)
        return _prob

    @property
    def prob(self):
        if not self._prob:
            self._prob = self._make_prob()
        return self._prob

    def multi_prob(self, n, wrk=None, max_value=100):
        if n == 0:
            return wrk
        elif n == 1 and wrk:
            return wrk
        elif n == 1 and not wrk:
            return self.prob

        if wrk is None:
            _prob = copy.deepcopy(self.prob)
        else:
            _prob = copy.deepcopy(wrk)

        return self.multi_prob(
            n - 1,
            self.convolve_probs(self.prob, _prob, max_value=max_value),
            max_value=max_value,
        )

    @staticmethod
    def convolve_probs(prob_dict1, prob_dict2, max_value=100):
        _prob = defaultdict(float)
        for runs1, prob1 in prob_dict1.items():
            for runs2, prob2 in prob_dict2.items():
                if runs1 + runs2 <= max_value:
                    _prob[runs1 + runs2] += prob1 * prob2
        return _prob

    @staticmethod
    def generate_rvs(prob_dict, rng=None):
        if rng is None:
            rng = np.random
        return rng.choice(list(prob_dict.keys()), p=list(prob_dict.values()))

    @staticmethod
    def compute_win_prob(prob_dict1, prob_dict2):
        _prob = defaultdict(float)
        for runs1, prob1 in prob_dict1.items():
            for runs2, prob2 in prob_dict2.items():
                if runs1 > runs2:
                    res = 1
                elif runs1 < runs2:
                    res = -1
                else:
                    res = 0
                _prob[res] += prob1 * prob2
        return _prob


def overall_win_pct(team1, team2, max_value=30, baseline_innings=9):
    epsilon = 1e-6
    d1 = team1.multi_prob(baseline_innings, max_value=max_value)
    d2 = team2.multi_prob(baseline_innings, max_value=max_value)
    win_pct = ProbDist.compute_win_prob(d1, d2)
    tie_prob = win_pct[0]
    extra_inning_count = 0
    result = [
        {
            "innings": baseline_innings + extra_inning_count,
            "tie_prob": tie_prob,
            "win_prob": win_pct[1],
            "loss_prob": win_pct[-1],
        }
    ]

    while tie_prob > epsilon:
        extra_inning_count += 1
        d1 = team1.multi_prob(extra_inning_count, max_value=30)
        d2 = team2.multi_prob(extra_inning_count, max_value=30)
        w = ProbDist.compute_win_prob(d1, d2)
        win_pct[1] += w[1] * tie_prob
        win_pct[-1] += w[-1] * tie_prob
        tie_prob *= w[0]
        result.append(
            {
                "innings": baseline_innings + extra_inning_count,
                "tie_prob": tie_prob,
                "win_prob": win_pct[1],
                "loss_prob": win_pct[-1],
            }
        )

    return pd.DataFrame(result).assign(relative_prob = lambda x: x.win_prob/(x.win_prob+x.loss_prob))


def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--success-prob", required=True, nargs=2, type=float)
    parser.add_argument("--offset", required=True, nargs=2, type=float)
    parser.add_argument("--baseline-innings", default=9, type=int)
    parser.add_argument("--max-value", default=30, type=int)
    args = parser.parse_args(args)
    return args



def main():
    args = _parse_args(sys.argv[1:])
    team1 = ProbDist(args.success_prob[0], args.offset[0])
    team2 = ProbDist(args.success_prob[1], args.offset[1])
    return overall_win_pct(
        team1, team2, max_value=args.max_value, baseline_innings=args.baseline_innings
    )


if __name__ == "__main__":
    res = main()
    print(res)
