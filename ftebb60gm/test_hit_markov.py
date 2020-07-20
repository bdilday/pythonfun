from hit_markov import HitState, MarkovHitState, HitEvent, state_transition


def test_hit_state():
    hit_state = HitState()
    assert hit_state.hits == 0


def test_hit_markov_state():
    markov_hit_state = MarkovHitState()


def test_state_transition():
    initial_state = HitState()

    state = state_transition(initial_state, HitEvent(0))

    assert state == HitState(hits=0, current_streak=0, longest_streak=0)

    state = state_transition(state, HitEvent(1))
    assert state == HitState(hits=1, current_streak=1, longest_streak=1)

    state = state_transition(state, HitEvent(0))
    assert state == HitState(hits=1, current_streak=0, longest_streak=1)
