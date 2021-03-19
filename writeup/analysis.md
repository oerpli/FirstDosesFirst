# Analysis

- [Analysis](#analysis)
  - [Some notes](#some-notes)
  - [Vacination efficacy](#vacination-efficacy)
  - [Death calculations & assumptions](#death-calculations--assumptions)
- [Results](#results)
  - [1st Approach: Only count vaccinations](#1st-approach-only-count-vaccinations)
  - [2nd Approach: Take age into account](#2nd-approach-take-age-into-account)

## Some notes
- I use smoothed death statistics to reduce data-reporting related artifacts.


## Vacination efficacy
I defined some points with "reasonable" numbers for efficacy after x days and connected them with a linear fit.

[//]: # (EfficacyTable)

|   days |   one_dose |   two_dose |
|-------:|-----------:|-----------:|
|      0 |          0 |          0 |
|      3 |          0 |          0 |
|      6 |          0 |          0 |
|      9 |         11 |         11 |
|     12 |         27 |         27 |
|     15 |         43 |         43 |
|     18 |         59 |         59 |
|     21 |         75 |         75 |
|     24 |         75 |         79 |
|     27 |         76 |         83 |
|     30 |         77 |         87 |
|     33 |         78 |         92 |
|     36 |         79 |         95 |
|     39 |         80 |         95 |

[//]: # (EfficacyTable)

## Death calculations & assumptions

The population has size `P` (which is more or less stable) and people are infected and die from/with COVID with some rate `r` (which changes over time).
Some fraction `i` of the population is immune to COVID due to receiving a vaccination (or two of them). This results in the following formula for deaths (`D`): `D = (1 - i) * P * r`.

The population is found in demographic data (I used data from the UN and the US census).
Deaths from/with COVID are taken from [Our World In Data](https://ourworldindata.org).

When comparing various vaccination strategies, referred to as `0D`, `1D` and `2D` (zero doses, 1 dose, 2 doses), I take the very conservative assumption that this only influences the immune fraction `i` (realistically, it would also change the rate `r` that contains the number of infections).
I refer to the immunity from the different strategies as `ix`, i.e. `i1`, `i2` & `i0`

Therefore, if a country is using a two dose vaccination strategy, I estimate the number of deaths from a one dose strategy as follows:
```
D2          = (1-i2) * P * r
D2 / (1-i2) = P * r                      (1)
```
and also:
```
D1          = (1-i1) * P * r 
D1 / (1-i1) = P * r                      (2)
```
Combining (1) and (2) results in
```
D1 / (1-i1) = P * r = D2 / (1-i2)
D1                  = D2 / (1-i2) * (1-i1)
```
The same approach is used to estimate D0.

# Results

## 1st Approach: Only count vaccinations
My initial approach was to just do the following:
- Estimate the daily level of immunization resulting from both, a 1D and 2D vaccination program
- Also estimate 0D
- Estimate resulting deaths from either of them




[//]: # (SimpleAnalysis)

|                |     0D |     1D |     2D |   2D vs 0D |   1D vs 0D |   1D vs 2D |
|:---------------|-------:|-------:|-------:|-----------:|-----------:|-----------:|
| Austria        |   4793 |   4753 |   4767 |         26 |         40 |         14 |
| Germany        |  53680 |  53113 |  53224 |        456 |        567 |        111 |
| United Kingdom |  65924 |  62495 |  63161 |       2763 |       3429 |        666 |
| United States  | 250379 | 240787 | 242745 |       7634 |       9592 |       1958 |

[//]: # (SimpleAnalysis)

## 2nd Approach: Take age into account
Older people have vastly higher chance of dying and are also vaccinated first (in most countries).
I found data for demographic distribution from most countries as well as data about age of COVID deaths of a few countries. Demographic data often uses bracketing that is useful to estimate the amount of people currently in school and in retirement, which is not what I am interested in. 

I split the age brackets provided by the UN (0-14,15-64,65+) into sub brackets. I took the distribution from the United States for this as it seemed reasonable enough to do so.

Furthermore, I split the deaths worldwide also with the same method into deaths by age bracket.
The data for this was obtained by the CDC.

