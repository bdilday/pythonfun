""" baseball with negative binomial distribution simulations

This code uses numerical simulations to estimate the winning percentages
for the three teams. The file ftebb.py does exact calculations
"""
import attr
import sys
import pandas as pd
import numpy as np
import requests
import json
import logging
import argparse


MAX_INNING = 99


class Team:
    def __init__(self, success_prob, runs_offset, rng):
        self.success_prob = success_prob
        self.failure_prob = 1 - success_prob
        self.runs_offset = runs_offset
        self.rng = rng

    def valid_rng(self, rng):
        return rng if rng else self.rng

    def generate_nonout_pa(self, rng=None):
        rng = self.valid_rng(rng)
        return rng.negative_binomial(3, self.failure_prob)

    def generate_score(self, rng=None):
        return max(0, self.generate_nonout_pa(rng) - self.runs_offset)

    def sim_score(self, rng=None, innings=1):
        return sum([self.generate_score(rng) for _ in range(innings)])


def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--random-seed", default=20190927, type=int)
    parser.add_argument("--max-innings", default=9, type=int)
    parser.add_argument("--number-games", default=10000, type=int)
    args = parser.parse_args(args)
    return args


def sim_game(teamA, teamB, rng, max_inning=None):
    if max_inning is None:
        max_inning = MAX_INNING
    inning = 0
    score_diff = 0
    scores = [0, 0]
    while inning < max_inning or score_diff == 0:
        scoreA = teamA.sim_score(rng=rng, innings=1)
        scoreB = teamB.sim_score(rng=rng, innings=1)
        inning += 1
        scores[0] += scoreA
        scores[1] += scoreB
        score_diff = scores[1] - scores[0]
    return (scores[0], scores[1], inning)


def team_matchup_df(teamA, teamB, rng, n=10000):
    df = pd.DataFrame([sim_game(teamA, teamB, rng) for _ in range(n)]).rename(
        columns={0: "scoreA", 1: "scoreB", 2: "innings"}
    )
    return df


def get_result(df):
    return (
        df.assign(w=df.scoreB > df.scoreA)
        .assign(w=lambda r: r.w.astype(int))
        .assign(i9=df.innings > MAX_INNING, c=1)
    )


def print_result(teamA, teamB, rng, N=1000000):
    df = get_result(team_matchup_df(teamA, teamB, rng, n=N))
    print(df.groupby("i9").mean())
    print(
        pd.concat((df.mean(), df.std()), axis=1, ignore_index=False).rename(
            columns={0: "mean", 1: "std"}
        )
    )


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    rng = np.random.RandomState(args.random_seed)
    N = args.number_games
    MAX_INNING = args.max_innings

    team_walk = Team(success_prob=0.4, runs_offset=3, rng=None)
    team_hr = Team(success_prob=0.1, runs_offset=0, rng=None)
    team_double = Team(success_prob=0.2, runs_offset=1, rng=None)

    fmt_str = "*****\n** A: {} - B: {}\n*****"

    print(fmt_str.format("walk", "double"))
    print_result(team_walk, team_double, rng, N)

    print(fmt_str.format("walk", "hr"))
    print_result(team_walk, team_hr, rng, N)

    print(fmt_str.format("double", "hr"))
    print_result(team_double, team_hr, rng, N)

