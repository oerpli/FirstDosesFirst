# Could we have vaccinated more efficiently? 

tl;dr: Yes. Epistemic status: Sure

- [Could we have vaccinated more efficiently?](#could-we-have-vaccinated-more-efficiently)
  - [Current state of the vaccination effort](#current-state-of-the-vaccination-effort)
    - [Vaccinations per age group](#vaccinations-per-age-group)
    - [Vaccinated per age group](#vaccinated-per-age-group)
- [Disclaimers & Notes](#disclaimers--notes)

Vorarlberg has a population of slightly below 400k and its vaccination program (just like every other in the EU) is constrained by vaccine supply.

In this post I will present the current state of the program and try to estimate how much a better strategy could have improved immunization.

## Current state of the vaccination effort

### Vaccinations per age group
Number of vaccinations per age group:

[//]: # (VaccTotal)

![](img/vlbg/VaccTotal.png)

[//]: # (VaccTotal)

And normalized with the population per group (the target value for each age group is 2, i.e. two doses of whatever vaccine):

[//]: # (VaccRelative)

![](img/vlbg/VaccRelative.png)

[//]: # (VaccRelative)

### Vaccinated per age group
More relevant than the number of vaccinations per age group is the number of people that received at least one shot of any of the currently available vaccines, as this seems to be sufficient as protection against severe and fatal disease.


[//]: # (D1Relative)

![](img/vlbg/D1Relative.png)

[//]: # (D1Relative)


[//]: # (D1Data)

|       |   1 dose Absolute |   1 dose % |
|:------|------------------:|-----------:|
| 25-34 |              3111 |       5.88 |
| 35-44 |              4409 |       8.23 |
| 45-54 |              6808 |      11.37 |
| 55-64 |              8610 |      16.22 |
| 65-74 |              9361 |      26.36 |
| 75-84 |             14451 |      57.76 |
| 85-99 |              6069 |      66.39 |

[//]: # (D1Data)

And the number of people fully vaccinated (received 2 doses)

[//]: # (D2Relative)

![](img/vlbg/D2Relative.png)

[//]: # (D2Relative)
[//]: # (D2Data)

|       |   2 doses Absolute |   2 doses % |
|:------|-------------------:|------------:|
| 25-34 |               1312 |        2.48 |
| 35-44 |               1785 |        3.33 |
| 45-54 |               2818 |        4.71 |
| 55-64 |               2921 |        5.5  |
| 65-74 |               2093 |        5.89 |
| 75-84 |               8401 |       33.58 |
| 85-99 |               5301 |       57.99 |

[//]: # (D2Data)


And as a preparation for a point that will be made later, the number of people that received only (!) one dose. 
This one is not strictly increasing as people might get a second shot at some point.

[//]: # (D1Only)

![](img/vlbg/D1Only.png)

[//]: # (D1Only)

[//]: # (D1OnlyData)

|       |   Only 1 dose Absolute |   Only 1 dose % |
|:------|-----------------------:|----------------:|
| 25-34 |                   1799 |            3.4  |
| 35-44 |                   2624 |            4.9  |
| 45-54 |                   3990 |            6.66 |
| 55-64 |                   5689 |           10.72 |
| 65-74 |                   7268 |           20.47 |
| 75-84 |                   6050 |           24.18 |
| 85-99 |                    768 |            8.4  |

[//]: # (D1OnlyData)


# Disclaimers & Notes

- Currently, I don't take differences between the various vaccines into account. There are multiple reasons for this:
  - I am mostly interested in the impact on deaths/severe cases. All currently available vaccines are very effective in preventing those. The higher efficacy of mRNA would mostly manifest in a slower spread which is beyond the scope of this work.
  - Tracking how different age cohorts were vaccinated is pretty bothersome, due to changing rules (no AZ for old people, no AZ for young people, ...). I also think that there is no data available at this level of granularity.
- The age group `85-99` also contains all persons over 99. 