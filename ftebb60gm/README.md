
## FiveThirtyEight 60-game baseball season riddler

This module uses Markov chains to solve the fivethirtyeight riddler from 
July 17, 2020. https://fivethirtyeight.com/features/can-the-hare-beat-the-tortoise/

### Method

The questions are, given a true hit-per-AB probability of 0.35, 
 what are the odds of 
 
 * hitting 0.400
 * hitting in at least 56 straights games
 * hitting both 0.400 and in at least 56 straight games
 
 for seasons of length 60 and 162.
 
 The approach I took is to model the problem as 
 a Markov chain, where a state comprises
 
 * `hits`: number of total hits
 * `current_streak`: current streak of games hit in
 * `did_reach_streak_target`: a boolean indicating if the target streak has been broken
 
 A chain starts in the state with `hits`=0, `current_streak`=0,
 and `did_reach_streak_target`=False. Then after applying the 
 transition matrix for `G` games, we can compute the probabilities.
 
 ### Solution
 
 ```bash
$ python ./ftebb60gm/hit_markov.py --num-games 162 --hit-prob 0.35 --num-abs 4 --streak-target 56 --ba-target 0.35 --game-checks 60 162

------------------------------------------------------------
--  probability to hit 0.400
------------------------------------------------------------
     games  did_reach_ba_target       prob
119     60                    0 9.3916e-01
120     60                    1 6.0839e-02
     games  did_reach_ba_target       prob
323    162                    0 9.9621e-01
324    162                    1 3.7899e-03
------------------------------------------------------------
--  probability to achieve hit streak
------------------------------------------------------------
    games  did_reach_streak_target       prob
64     60                        0 9.9997e-01
65     60                        1 2.8305e-05
     games  did_reach_streak_target       prob
268    162                        0 9.9967e-01
269    162                        1 3.2896e-04
------------------------------------------------------------
--  probability to hit 0.400 AND achieve hit streak
------------------------------------------------------------
     games  did_reach_ba_target  did_reach_streak_target       prob
127     60                    0                        0 9.3916e-01
128     60                    0                        1 5.9039e-06
129     60                    1                        0 6.0816e-02
130     60                    1                        1 2.2401e-05
     games  did_reach_ba_target  did_reach_streak_target       prob
535    162                    0                        0 9.9590e-01
536    162                    0                        1 3.0663e-04
537    162                    1                        0 3.7676e-03
538    162                    1                        1 2.2337e-05

```