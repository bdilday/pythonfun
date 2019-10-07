
This code solves the 538 birthday riddler from [2019-10-04](https://fivethirtyeight.com/features/who-wants-to-be-a-riddler-millionaire/). 

The question is:

```
Given that you need to have 23 people in a group before there's 50-50 chance that at least one pair share a birthday, how many people do you need to have in order to have a 50-50 chance that at least any set of three share a birthday? 
```

```
$ python ./birthday.py --help
usage: Probability to have at least 1 shared birthday by N people
       [-h] [--slots SLOTS] [--target TARGET]
       [--probability-threshold PROBABILITY_THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  --slots SLOTS, -s SLOTS
                        number of slots (i.e. days in a year)
  --target TARGET, -t TARGET
                        number of shared birthdays to track
  --probability-threshold PROBABILITY_THRESHOLD, -p PROBABILITY_THRESHOLD
                        probability thtreshold at which to stop
```

```
$ python ./birthday.py -t 3 -s 365 -p 0.5 | tail -2
87 0.49945485063139783
88 0.5110651106247271
```

To confirm the 23 number for 2 or more shared birthdays, 

```
$ python ./birthday.py -t 2 -s 365 -p 0.5 | tail -2
22 0.47569530766254975
23 0.5072972343239849
```

