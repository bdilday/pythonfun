
## FiveThirtyEight baseball riddler

This repo includes code to solve the baseball oriented puzzle from FiveThirtyEight's Riddler for [Sept 27, 2019](https://fivethirtyeight.com/features/which-baseball-team-will-win-the-riddler-fall-classic/)

In this puzzle there are 3 teams.

* Moonwalkers

* Doubloons

* Taters

The three teams always either strikeout or (walk, hit doubles, hit homeruns), respectively. The probabilities for success are (0.4, 0.2, 0.1), respectively, i.e. the average number of bases obtained is 0.4 in each case. The question is, which team is most likely to win the league if the three teams play an equal number of games against each other.

### ftebb.py (Five Thirty Eight BaseBall)

This code computes exact probability distributions for runs scored, using the negative binomial distribution.

### bbnbinom.py (BaseBall with NegativeBinomial)

This code use numerical simulations. 

### Results

The exact computations from `ftebb.py` are more precise, as well as being computationally faster, and so are more interesting to examine. 

### Taters vs Doubloons 

The Taters win 62.7% of the time

```
$ python ./ftebb.py --success-prob 0.1 0.2 --offset 0 1 
   innings      tie_prob  win_prob  loss_prob  relative_prob
0        9  1.503555e-01  0.535313   0.314332       0.630043
1       10  9.411589e-02  0.569714   0.336170       0.628904
2       11  4.056275e-02  0.602465   0.356973       0.627935
3       12  1.313441e-02  0.619267   0.367599       0.627509
4       13  3.428531e-03  0.625231   0.371341       0.627382
5       14  7.598756e-04  0.626878   0.372363       0.627354
6       15  1.482687e-04  0.627257   0.372595       0.627350
7       16  2.611209e-05  0.627333   0.372641       0.627349
8       17  4.223029e-06  0.627347   0.372649       0.627349
9       18  6.349556e-07  0.627349   0.372650       0.627349
```

### Moonwalkers vs Doubloons 

The Moonwalkers win 58.7% of the time
```
$ python ./ftebb.py --success-prob 0.4 0.2 --offset 3 1 
   innings      tie_prob  win_prob  loss_prob  relative_prob
0        9  1.345929e-01  0.516078   0.349319       0.596348
1       10  9.217582e-02  0.537751   0.370064       0.592358
2       11  4.499739e-02  0.562473   0.392520       0.588981
3       12  1.635181e-02  0.577841   0.405797       0.587453
4       13  4.621735e-03  0.584274   0.411095       0.586992
5       14  1.058976e-03  0.586267   0.412664       0.586894
6       15  2.040442e-04  0.586754   0.413032       0.586879
7       16  3.409297e-05  0.586852   0.413104       0.586878
8       17  5.063430e-06  0.586869   0.413116       0.586878
9       18  6.815018e-07  0.586872   0.413117       0.586878
```

### Moonwalkers vs Taters

The real interesting matchup is the Moonwalkers vs the Taters. The Moonwalkers have more runs scored on average, but also a higher probability to have 0 runs. This of course means they have a higher probability for big innings also, i.e. they have a high variance. 

This means the Taters do better in short games. For this reason, if the game goes to extra innings they're lilely to win. 

In a game with 9-innings at baseline, they still win the majority of the time, namely 51.4% of the time

```
$ python ./ftebb.py --success-prob 0.1 0.4 --offset 0 3 
   innings      tie_prob  win_prob  loss_prob  relative_prob
0        9  1.245193e-01  0.441938   0.433533       0.504800
1       10  7.704385e-02  0.470229   0.452717       0.509487
2       11  3.177108e-02  0.496399   0.471820       0.512693
3       12  9.449060e-03  0.508949   0.481592       0.513809
4       13  2.181522e-03  0.512936   0.484873       0.514062
5       14  4.155437e-04  0.513884   0.485691       0.514102
6       15  6.838619e-05  0.514066   0.485855       0.514107
7       16  1.004784e-05  0.514097   0.485883       0.514107
8       17  1.348396e-06  0.514101   0.485888       0.514107
9       18  1.679013e-07  0.514102   0.485888       0.514107
```

However, if games were 12 innings long than the Moonwalkers would win 50.06% of the time

```
$ python ./ftebb.py --success-prob 0.1 0.4 --offset 0 3 --baseline-innings 12
   innings      tie_prob  win_prob  loss_prob  relative_prob
0       12  1.051695e-01  0.438391   0.456423       0.489924
1       13  6.507156e-02  0.462286   0.472626       0.494470
2       14  2.683399e-02  0.484390   0.488760       0.497755
3       15  7.980716e-03  0.494989   0.497013       0.498980
4       16  1.842523e-03  0.498356   0.499785       0.499284
5       17  3.509700e-04  0.499157   0.500476       0.499340
6       18  5.775927e-05  0.499311   0.500614       0.499348
7       19  8.486449e-06  0.499337   0.500638       0.499349
8       20  1.138861e-06  0.499341   0.500642       0.499349
9       21  1.418102e-07  0.499341   0.500642       0.499350
```

And if games had a 10-inning baseline, the Moonwalkers would be more likely to win in games that end after regulation, but more likely to lose overall due to extra inning games.

```
$ python ./ftebb.py --success-prob 0.1 0.4 --offset 0 3 --baseline-innings 10
   innings      tie_prob  win_prob  loss_prob  relative_prob
0       10  1.168322e-01  0.440927   0.442229       0.499263
1       11  7.228763e-02  0.467472   0.460229       0.503904
2       12  2.980972e-02  0.492027   0.478152       0.507151
3       13  8.865732e-03  0.503802   0.487321       0.508314
4       14  2.046848e-03  0.507542   0.490399       0.508589
5       15  3.898906e-04  0.508432   0.491167       0.508636
6       16  6.416444e-05  0.508603   0.491321       0.508642
7       17  9.427548e-06  0.508632   0.491347       0.508642
8       18  1.265154e-06  0.508636   0.491351       0.508642
9       19  1.575361e-07  0.508636   0.491352       0.508642

```