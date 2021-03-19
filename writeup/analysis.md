# Analysis

## Some notes
- I use smoothed death statistics to reduce data-reporting related artifacts.


### Vacination efficacy
I defined some points with "reasonable" numbers for efficacy after x days and connected them with a linear fit.

[//]: # (EfficacyTable)

| days | one_dose | two_dose |
| ---: | -------: | -------: |
|    0 |        0 |        0 |
|    3 |        0 |        0 |
|    6 |        0 |        0 |
|    9 |       11 |       11 |
|   12 |       27 |       27 |
|   15 |       43 |       43 |
|   18 |       59 |       59 |
|   21 |       75 |       75 |
|   24 |       75 |       79 |
|   27 |       76 |       83 |
|   30 |       77 |       87 |
|   33 |       78 |       92 |
|   36 |       79 |       95 |
|   39 |       80 |       95 |

[//]: # (EfficacyTable)

### Death calculations & assumptions

The population has size `P` and people are infected and die from/with COVID with some rate `r`.
Some fraction `i` of the population is immune to COVID due to receiving a vaccination (or two of them). This results in the following formula `D = (1 - i) * P * r`.

The population is found in demographic data (I used data from the UN and the US census).
Deaths from/with COVID are taken from [Our World In Data](https://ourworldindata.org).

When comparing various vaccination strategies, referred to as `0D`, `1D` and `2D` (zero doses, 1 dose, 2 doses), I take the very conservative assumption that this only influences immune fraction `i` (realistically, it would also affect the rate `r` that contains the number of infections).
I refer to the immunity from the different strategies as `i_x`, i.e. `i1`, `i2` & `i3`

Therefore, if a country is using a two dose vaccination strategy, I the hypothetical number of deaths as follows:
```
D2 = (1-i2) * P * r 
D2 / (1-i2) = P * r
```
and also:
```
D1 / (1-i1) = P * r
```
Combining the two results in
```
D1 / (1-i1) = P * r = D2 / (1-i2)
D1 = D2 / (1-i2) * (1-i1) * P * r
```
A similar approach is used to estimate D0. 

# Results

## 1st Approach: Only count vaccinations
My initial approach was to just do the following:
- Estimate the daily level of immunization resulting from both, a 1D and 2D vaccination program
- Also estimate 0D
- Estimate resulting deaths from either of them




[//]: # (SimpleAnalysis)

|                |     0D |     1D |     2D |   1D vs 0D |   2D vs 0D |   1D vs 2D |
|:---------------|-------:|-------:|-------:|-----------:|-----------:|-----------:|
| Austria        |   4847 |   4803 |   4819 |         44 |         28 |         16 |
| United Kingdom |  66183 |  62687 |  63377 |       3496 |       2806 |        690 |
| United States  | 253228 | 243096 | 245221 |      10132 |       8007 |       2125 |

[//]: # (SimpleAnalysis)

## 2nd Approach: Take age into account
Older people have vastly higher chance of dying and are also vaccinated first (in most countries).
I found data for demographic distribution from most countries as well as data about age of COVID deaths of a few countries. Demographic data often uses bracketing that is useful to estimate the amount of people currently in school and in retirement, which is not what I am interested in. 

I split the age brackets provided by the UN (0-14,15-64,65+) into sub brackets. I took the distribution from the United States for this as it seemed reasonable enough to do so.

Furthermore, I split the deaths worldwide also with the same method into deaths by age bracket.
The data for this was obtained by the CDC.

