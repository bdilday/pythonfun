from hit_markov import HitState, HitEvent, state_transition


def test_hit_state():
    hit_state = HitState()
    assert hit_state.hits == 0


def test_state_transition():
    initial_state = HitState()

    state = state_transition(initial_state, HitEvent(0), 2)

    assert state == HitState(hits=0, current_streak=0, did_reach_streak_target=0)

    state = state_transition(state, HitEvent(1), 2)
    assert state == HitState(hits=1, current_streak=1, did_reach_streak_target=0)

    state = state_transition(state, HitEvent(1), 2)
    assert state == HitState(hits=2, current_streak=2, did_reach_streak_target=1)

    state = state_transition(state, HitEvent(0), 2)
    assert state == HitState(hits=2, current_streak=0, did_reach_streak_target=1)
