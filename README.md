# FirstDosesFirst

Around the globe (with a few exceptions), vaccination efforts are currently constrained by supply.
My goal is not to address why there isn't a viable path to fix these supply issues (Curtis Yarvin would certainly be able to write a few dozen of pages about it if anyone asked him nicely) but how existing supply could and should be used more effectively.

## Dosing strategy

Currently, a handful of vaccinations with varying levels of efficacy are approved.
Most of them are to be administered in two doses, with several weeks in between. 


| Name              | Doses | Recommended Interval |
| ----------------- | ----: | -------------------- |
| Johnson & Johnson |     1 | -                    |
| Pfizer/Biontech   |     2 | 3 weeks              |
| Sputnik           |     2 | 3 weeks              |
| Novovax           |     2 | 3 weeks              |
| Coronavac         |     2 | 3 weeks              |
| Moderna           |     2 | 4 weeks              |
| Astra Zeneca      |     2 | 8-12 weeks           |


When searching for information, why some vaccines need two doses and others do not, one can find things like:

- Weak efficacy after first dose, good efficacy after second dose [Link](https://www.healthline.com/health/why-two-doses-of-covid-vaccine#immunity-after-first-dose)
- Designed that way [Link](https://abc11.com/johnson-and-vaccine-covid-pfizer/10379441/)
- Two doses of Pfizer/Moderna are necessary [Link](https://jamanetwork.com/journals/jama/fullarticle/2776229)

When reading those and similar articles as well as their sources, my overall impression is that it's a whole lot of FUD and not much more.
I will try to address each of these points with a subsection.

### Weak after first dose, strong after second
"Weak after first dose" is measured a few days after the vaccine is administered, i.e. mostly before the immune system had enough time to build up immunity.
This is measured as follows:
- N persons believe they are vaccinated at day x, half of them are given only a placebo. 
- Number of people that tested COVID positive after up to 14 days is 50% lower in vaccine group than the placebo group

As the incubation period of COVID is approximately four to five days[^1], people that develop symptoms in the first week were (likely) either infected shortly before or after they were given the vaccine.

![Cases n days after 1st dose](img/days_after_d1.png)

If the first week after the 1st dose is cropped out of the picture, one gets the following result:

![Cases n days after 7 days after 1st dose](img/dad1_edit.png)

As approximately 50% of the cases that contribute to the 52% efficacy occurred in the first week after the 1st dose, the resulting 52% severely underestimates how effective the first dose actually is.

The 90.5% (61.0-98.9) efficacy from the first week after the second dose is likely a better estimation of the actual efficacy of the first dose (because if someone is infected 20 days after the first dose, the positive test would fall in this time interval).
Note that the confidence interval is rather large - this is due to the fact that the observed time interval is small.

### Designed that way

There were several goals & constraints when developing vaccinations for COVID:
- Get above some threshold for efficacy. I vaguely remember that back in the summer of 2020 around 60% would have been enough.
- Trials should be done as fast as possible.
- All red tape put up in dozens of years by regulations has to be respected.

The discussion at [Pfizer/Moderna/...] probably went something like this:

> A: A new virus seems to go around, could be a big thing. Let's create some vaccine
> 
> B: Okay. I will try out this new mRNA thing
> 
> `[2 days later]`[^2]
> 
> B: I have something promising. Let's do some tests!
> 
> A: Okay. How much should we give participants? 
> 
> C: No idea. One syringe, approx. one third full, like on my favorite syringe clip art that I use for my PowerPoint slides
> ![Image of syringe](img/syringe.png)
> 
> A: How much is that? 
> 
> B: (grabbing a random syringe from a box lying around) This one has 300µm, so let's go with 100µm
> 
> A: And let's do two doses, it's usually better than one. But how much apart? 1 week? 1 month? 1 year? 
> 
> C: Let's go with something short, else our trials will take forever.
> 
> CEO: 2 doses, 100µg each, 3 weeks apart it is! 

While I am not entirely sure that it is how it went, various studies have been released that show:
- Vastly smaller doses resulting in comparable immune reaction [SOURCES!!!]
- Improved long term immunity with longer interval between two doses.
- Pretty good immunity from one dose only (at least for mRNA vaccines)
Illiterate bureaucrats treat 

[^1]: https://www.health.harvard.edu/diseases-and-conditions/if-youve-been-exposed-to-the-coronavirus

[^2]: https://www.businessinsider.com/moderna-designed-coronavirus-vaccine-in-2-days-2020-11?r=DE&IR=T