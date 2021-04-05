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
| 25-34 |              3123 |       5.9  |
| 35-44 |              4432 |       8.27 |
| 45-54 |              6850 |      11.44 |
| 55-64 |              8809 |      16.6  |
| 65-74 |             11797 |      33.22 |
| 75-84 |             16693 |      66.72 |
| 85-99 |              6096 |      66.68 |

[//]: # (D1Data)

And the number of people fully vaccinated (received 2 doses)

[//]: # (D2Relative)

![](img/vlbg/D2Relative.png)

[//]: # (D2Relative)
[//]: # (D2Data)

|       |   2 doses Absolute |   2 doses % |
|:------|-------------------:|------------:|
| 25-34 |               1316 |        2.49 |
| 35-44 |               1792 |        3.35 |
| 45-54 |               2834 |        4.73 |
| 55-64 |               3196 |        6.02 |
| 65-74 |               2963 |        8.34 |
| 75-84 |               9235 |       36.91 |
| 85-99 |               5460 |       59.72 |

[//]: # (D2Data)


And as a preparation for a point that will be made later, the number of people that received only (!) one dose. 
This one is not strictly increasing as people might get a second shot at some point.

[//]: # (D1Only)

![](img/vlbg/D1Only.png)

[//]: # (D1Only)

[//]: # (D1OnlyData)

|       |   Only 1 dose Absolute |   Only 1 dose % |
|:------|-----------------------:|----------------:|
| 25-34 |                   1807 |            3.42 |
| 35-44 |                   2640 |            4.93 |
| 45-54 |                   4016 |            6.71 |
| 55-64 |                   5613 |           10.58 |
| 65-74 |                   8834 |           24.88 |
| 75-84 |                   7458 |           29.81 |
| 85-99 |                    636 |            6.96 |

[//]: # (D1OnlyData)


# Disclaimers & Notes

- Currently, I don't take differences between the various vaccines into account. There are multiple reasons for this:
  - I am mostly interested in the impact on deaths/severe cases. All currently available vaccines are very effective in preventing those. The higher efficacy of mRNA would mostly manifest in a slower spread which is beyond the scope of this work.
  - Tracking how different age cohorts were vaccinated is pretty bothersome, due to changing rules (no AZ for old people, no AZ for young people, ...). I also think that there is no data available at this level of granularity.
- The age group `85-99` also contains all persons over 99. 