import argparse
import attr
from collections import defaultdict
from functools import lru_cache
import sys
import logging

from scipy.stats.distributions import binom
import pandas as pd

logging.basicConfig(level=logging.INFO)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-games", type=int, required=True)
    parser.add_argument("--hit-prob", type=float, required=False, default=0.35)
    parser.add_argument("--num-abs", type=int, default=4)
    parser.add_argument("--ba-target", type=float, default=0.35)
    parser.add_argument("--streak-target", "-t", type=int, required=False, default=56)
    parser.add_argument("--game-checks", nargs="+", type=int, required=False)
    parser.add_argument("--output-path", "-o", required=False)
    return parser.parse_args(sys.argv[1:])


@attr.s(frozen=True, hash=True)
class HitState:
    hits = attr.ib(type=int, default=0)
    current_streak = attr.ib(type=int, default=0)
    did_reach_streak_target = attr.ib(type=int, default=0)

    def __iter__(self):
        yield self.hits
        yield self.current_streak
        yield self.did_reach_streak_target


@attr.s(frozen=True, hash=True)
class HitEvent:
    num_hits = attr.ib(type=int)


@lru_cache(maxsize=1024 ** 3)
def state_transition(initial_state, hit_event, streak_target):
    hits = initial_state.hits + hit_event.num_hits
    updated_streak = 0 if hit_event.num_hits == 0 else initial_state.current_streak + 1
    did_reach_streak_target = (
        1 if updated_streak >= streak_target else initial_state.did_reach_streak_target
    )
    return attr.evolve(
        initial_state,
        hits=hits,
        current_streak=updated_streak,
        did_reach_streak_target=did_reach_streak_target,
    )


def state_vector_total_prob(state_vector):
    return sum(state_vector.values())


@lru_cache(maxsize=128)
def hits_prob_fun(num_hits, num_abs, hit_prob):
    return binom(n=num_abs, p=hit_prob).pmf(num_hits)


def state_vector_to_dicts(state_vector, idx):
    logging.debug("state dicts %d", idx)
    return [
        {
            **dict(
                zip(("hits", "current_streak", "did_reach_streak_target"), hit_state)
            ),
            **{"prob": prob, "games": idx},
        }
        for hit_state, prob in state_vector.items()
    ]


def states_to_df(states):
    results = []
    for idx, state in enumerate(states):
        results += state_vector_to_dicts(state, idx)
    return pd.DataFrame(results)


def longest_streaks(hit_prob, num_abs, num_games, streak_target):
    state_vector = defaultdict(float)
    initial_state = HitState()
    state_vector[initial_state] += 1
    states = [state_vector]

    for idx in range(num_games):
        logging.info("game %d of %d", idx + 1, num_games)
        state_vector = states[-1]
        new_state_vector = defaultdict(float)
        for state, state_prob in state_vector.items():
            for num_hits in range(num_abs + 1):
                hit_event_prob = hits_prob_fun(num_hits, num_abs, hit_prob)
                new_state = state_transition(state, HitEvent(num_hits), streak_target)
                new_state_vector[new_state] += hit_event_prob * state_prob
        states.append(new_state_vector)

    result_df = states_to_df(states).assign(total_ab=lambda row: row.games * num_abs)
    return result_df.assign(ba=lambda row: row.hits / row.total_ab)


def summary(result_df, columns):
    summary_df = result_df.groupby(["games"] + columns).prob.sum().reset_index()
    return summary_df


def overall_summary(result_df, games):
    summary_types = (
        ["did_reach_ba_target"],
        ["did_reach_streak_target"],
        ["did_reach_ba_target", "did_reach_streak_target"],
    )
    descriptors = (
        "probability to hit 0.400",
        "probability to achieve hit streak",
        "probability to hit 0.400 AND achieve hit streak",
    )

    pd.set_option("display.float_format", "{:,.4e}".format)
    for descriptor, summary_type in zip(descriptors, summary_types):
        summary_df = summary(result_df, summary_type)
        print("-" * 60)
        print("-- ", descriptor)
        print("-" * 60)
        for num_games in games:
            prob_df = summary_df.query(f"games == {num_games}")
            print(prob_df)


def main():
    pd.set_option("display.max_columns", 999)
    pd.set_option("display.max_rows", 999)

    args = _parse_args()

    game_checks = args.game_checks or [60, 162]

    result_df = longest_streaks(args.hit_prob, args.num_abs, args.num_games, args.streak_target)
    result_df = result_df.assign(
        did_reach_ba_target=lambda row: (row.ba >= args.ba_target).astype(int)
    )
    overall_summary(result_df, game_checks)

    if args.output_path:
        result_df.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main()
