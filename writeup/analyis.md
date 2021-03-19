# Analysis

## Some notes
- I use smoothed death statistics to reduce data-reporting related artifacts.
- 

## 1st Approach: Only count vaccinations
My initial approach was to just do the following:
- Estimate the daily level of immunization resulting from both, a 1D and 2D vaccination program
- Also estimate 0D
- Estimate resulting deaths from either of them

The formula for either of these is:



|                |     0D |     1D |     2D |   1D vs 0D |   2D vs 0D |   1D vs 2D |
|:---------------|-------:|-------:|-------:|-----------:|-----------:|-----------:|
| Austria        |   4847 |   4803 |   4819 |        -44 |        -28 |        -16 |
| United Kingdom |  66187 |  62682 |  63377 |      -3505 |      -2810 |       -695 |
| United States  | 253249 | 243088 | 245221 |     -10161 |      -8028 |      -2133 |


## 2nd Approach: Take age into account
Older people have vastly higher chance of dying and are also vaccinated first (in most countries).
I found data for demographic distribution from most countries as well as data about age of COVID deaths of a few countries. Demographic data often uses bracketing that is useful to estimate the amount of people currently in school and in retirement, which is not what I am interested in. 

I split the age brackets provided by the UN (0-14,15-64,65+) into sub brackets. I took the distribution from the United States for this as it seemed reasonable enough to do so.

Furthermore, I split the deaths worldwide also with the same method into deaths by age bracket.
The data for this was obtained by the CDC.

