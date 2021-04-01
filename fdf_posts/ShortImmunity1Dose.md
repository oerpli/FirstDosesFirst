# Immunity from first dose of Pfizer/Biontech BNT162b2

People think that the Pfizer vaccine against COVID-19 only protects against the illness after the second shot has been administered. 
When looking at the data from the phase 3 trial, this is obviously wrong.
In this post I will try to clarify some of these misunderstandings as easy as possible.

The following picture is the relevant plot from the publication. The two curves (blue & red) shows the COVID-19 incidence in the placebo (blue) and treatment (red) groups.

![](img/days_after_d1.png)

If a doesn't work, one would expect both lines to have a similar slope. If it works, the slope of the treatment group will be less steep than that of the placebo group. 
Efficacy is calculated as the fraction of the gradients of the two slopes.

This means: If the placebo group rises by 10 units per day and the vaccine group rises by 2 units per day, this translates to a 80% efficacy.


Below the table the efficacy of various time-intervals are calculated:

- After dose 1 (day 0 to the end)
- After dose 1 and before dose 2 (day 0 to 21)
- Dose 2 to 7 days after dose 2 (day 21 to 28)
- More than 7 days after dose 2 (day 28 to the end)

One would think that second and third/fourth of these numbers correspond to the efficacy of 1 dose vs 2 doses but this is wrong because it neglects how vaccinations work the incubation period of COVID-19.


## The incubation period
If a person is exposed to the virus on day X, it takes a few days (4-5, up to a week) until this person gets sick. More importantly, even a PCR test wouldn't register the virus in directly after exposure.
An antigen test would detect it a few days after exposure. 

Therefore it's somewhat safe to assume that people that tested positive in the first days after dose 1 were already infected before they were vaccinated.

## How vaccinations work
A vaccine stimulates the immune system to produce protection against some virus.
As this process takes some time when a person gets infected with e.g. the flu (approx. 1 week afaik) it's safe to assume that it also takes some time when the immune system is triggered with a vaccine and not a real live virus. I have no idea how long exactly it would take, but the data from the trial actually shows it. 

If you look at the red and blue curves right after the injection, the follow a very similar trajectory until day 10-12 (the red one is below the blue one even earlier but this is likely random noise).


## How would one calculate the efficacy then? 
The same arguments as above also apply to the second dose. 
People that receive the 2nd dose on day 21 and test positive on day 23 were likely already infected before receiving the 2nd dose. 
People that test positive on day 26 might have been infected after receiving the second dose but it's likely that immune system didn't yet fully react to the second stimulation, meaning their level of protection against a severe case of COVID-19 (if it exists) is still from the first dose. 


Therefore, it's likely better to look at the sloop between days 14 and 28 to get the efficacy of the first dose and at day 28 and later for the efficacy of both shots. 

I used the professional medical data analysis tool MS Paint™ to remove the first ~10 days and put some slopes in there to estimate the efficacy of one dose (green line) and two doses (purple line).

The result can be seen here:

![](img/dad1_edit2.png)


## What does it mean? 

Several things:
- The green line is already way less steep than the blue one, i.e. the first dose is likely already enough to prevent spread symptomatic cases (afaik there wasn't a severe case of COVID in the population vaccinated with 1 dose after the initial period where the vaccine isn't effective yet)
- The purple line is slightly less steep than the green one, but compared to the blue one this increase is marginal. Data from the NHS says that the increase in immunity from the 2nd dose is approx 1/15th of the increase of the first dose (89% vs 95%)[^1] 

## What should we do with this information?

Put pressure on the politicians that waste 50% of doses on people that are already >80% immune and use it for persons that are still 0% immune.
People [^2] have calculated the optimal vaccination strategy taking these things into account, basically it is:
- Give people N to N+5 years old one dose (starting with old people)
- Give people in the brackets 15 years below the first dose
- Then give the old people the second dose



[^1]: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/955846/annex-b-comparison-between-1-and-2-dose-prioritisation-for-a-fixed-number-of-doses.pdf
[^2]: https://www.bmj.com/content/372/bmj.n710/rr