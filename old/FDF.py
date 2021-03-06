#%%
import itertools
from collections import defaultdict, deque
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme()

from data_loading import *
from utility import (
    write_img_to_file,
    write_to_file,
    write_img_to_file,
    OUT_FOLDER,
)

ANALYSIS_NOTES = OUT_FOLDER / "analysis.md"


current_dosing = {
    "Austria": 2,
    "United States": 2,
    "United Kingdom": 1,
    "Test": 2,
}

at = "Austria"
uk = "United Kingdom"
us = "United States"
iz = "Israel"
de = "Germany"

countries = [at, us, uk, iz, de]


#%% Load data
age = get_age_data()
deaths = get_death_data()
deaths_by_age = get_death_distr_by_age_us()


# %% Data for Immunity stemming from Vaccination:
# TODO: This should be made somehow less shitty s.t it is easy to plop in a replacement
# immunity-curve to see results


class VaccineEfficacy:
    def __init__(self) -> None:
        self.days_between_shots = 21
        base_immunity = 0
        first_dose = [
            (0, base_immunity),
            (7, base_immunity + 0.005),  # negligible gain in first week after shot
            (self.days_between_shots, 0.75),
        ]

        # In either case, vacc starts with 1st dose and divergence happens after ~3 weeks

        # TODO: Find data from UK regarding this number
        one_dose = first_dose + [(self.days_between_shots + 10, 0.75)]
        # From biontech study
        two_dose = first_dose + [(self.days_between_shots + 14, 0.90)]

        max_days = max([d for d, _ in one_dose] + [d for d, _ in two_dose])
        days = pd.DataFrame({"days": range(max_days + 1)}).set_index("days")
        eff_1d = pd.DataFrame(one_dose, columns=["days", D1]).set_index("days")
        eff_2d = pd.DataFrame(two_dose, columns=["days", D2]).set_index("days")
        # create df from interpolation of data points
        tmp = days.join(eff_1d).join(eff_2d)
        self.efficacy = tmp.sort_index().interpolate(axis=0)

    def print_table(self):
        tmp = (self.efficacy.iloc[:50:3] * 100).astype(int)
        tmp.columns = [x + " (%)" for x in tmp.columns]
        write_to_file(ANALYSIS_NOTES, "EfficacyTable", tmp.to_markdown())
        tmp.plot()
        imgPath = OUT_FOLDER / "img" / "Efficacy.png"
        plt.savefig(imgPath)
        caption = "Estimated efficacy after n days"
        write_img_to_file(ANALYSIS_NOTES, "EfficacyFigure", imgPath, caption)

    def __get_eff(self, doses, days):
        d = [D0, D1, D2][doses]
        x = self.efficacy[d]
        if days > len(self.efficacy) - 1:
            return x.iloc[-1]
        else:
            return x[days]

    def one_dose(self, x):
        return self.__get_eff(1, x)

    def two_dose(self, x):
        return self.__get_eff(2, x)


VACC = VaccineEfficacy()
VACC.print_table()

# %% Calculate immunity from two regimes
def calc_immunity_1d(df):
    """Input is DF with #vacc per mill/day (one column per country)
    Iterates over all rows, calculates the added immunity of each row to
    subsequent rows.
    At the end, divides per 1e6 to get the immunity per person (I was a bit unsure about this step)
    """
    df_columns = list(df.columns)
    result = pd.DataFrame(0, index=df.index, columns=df_columns)
    num_days = len(df)
    days = np.arange(result.shape[0])
    cols = list(df.columns)
    for (_, row), i in zip(df.iterrows(), days):
        days_since = [max(0, x - i) for x in range(num_days)]
        for country in cols:
            new_vac = row[country]
            result[country] += [e * new_vac for e in map(VACC.one_dose, days_since)]
    result /= 1e6
    return result


#%%


def calc_immunity_2d(df):
    """Does the same as `calc_immunity_1d` for two doses.
    This is achieved by having a backlog for each country.
    - If someone is vaccinated, they are added to a deque
    - After N days (whatever the time  between vaccs) the people from backlog are prioritised
        - on day X there are 100 vaccs, 5 people on backlog: 5 snd doses, 95 new doses, put 95 on backlog on day X+N
        - on day Y 100 vaccs, 105 on backlog: no new doses, but 5 remain, put 5 on backlog of Y+1
    """
    # Init backlog with all zeros
    BACKLOG = defaultdict(lambda: deque([0] * VACC.days_between_shots))
    df_columns = list(df.columns)
    result = pd.DataFrame(0, index=df.index, columns=df_columns)
    num_days = len(df)
    days = np.arange(result.shape[0])
    cols = list(df.columns)
    for (_, row), i in zip(df.iterrows(), days):
        days_since = [max(0, x - i) for x in range(num_days)]
        for country in cols:
            backlog = BACKLOG[country]  # get backlog of country
            need_2nd = backlog.popleft()  # remove first
            total_vacs_of_day = row[country]
            if need_2nd > total_vacs_of_day:
                new_vac_on_day = 0
                # give vacc to those that need 2nd shot
                # and add remaining to backlog for next day
                didnt_get_second = need_2nd - total_vacs_of_day
                backlog[0] += didnt_get_second
            else:
                new_vac_on_day = total_vacs_of_day - need_2nd
            backlog.append(new_vac_on_day)  # add new one
            result[country] += [
                e * new_vac_on_day for e in map(VACC.two_dose, days_since)
            ]
            # TOTAL_VAC[(country, D2)].append(new_vac_on_day)
            # TOTAL_JAB[(country, D2)].append(total_vacs_of_day)
    result /= 1e6
    return result


dvs = get_vaccination_data(extend_by_days=15)[countries]
dds = get_death_data(extend_by_days=15)[countries][dvs.index.min() :]
dds = dds.ffill()

imm1 = calc_immunity_1d(dvs)
imm2 = calc_immunity_2d(dvs)

#%%


def guesstimate_excess_deaths(imm1, imm2, deaths: pd.DataFrame, method):
    """Takes two estimated immunities and the resulting death count
    and scales death count

    Args:
        immunity ([type]): [description]
        deaths ([type]): [description]
    """
    start = imm1.index.min()
    imm = [None, imm1, imm2]  # None to have 1D in [1] and 2D in [2]

    countries = deaths.columns
    scaled_deaths = dict()
    for country in countries:
        # f1 = method[country]  # 1 or 2
        # f2 = 3 - f1  # the other one
        f1 = 1  # always use 1D and 2D
        f2 = 2  # always use 1D and 2D
        scaled_deaths[(country, D0)] = (
            (deaths[country] / (1 - imm[f2][country])).fillna(0).astype(int)
        )
        scaled_deaths[(country, D1)] = (
            (deaths[country] / (1 - imm[f2][country]) * (1 - imm[f1][country]))
            .fillna(0)
            .astype(int)
        )
        scaled_deaths[(country, D2)] = deaths[country].fillna(0).astype(int)

    df = pd.DataFrame(scaled_deaths)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    # return pd.DataFrame(scaled_deaths).join(deaths, rsuffix="_orig")
    return df


def simple_analysis():
    pass


ed = guesstimate_excess_deaths(imm1, imm2, dds, current_dosing)
ed[at].cumsum().plot()
ed[us].cumsum().plot()
ed[uk].plot()

#%%
cumsum = ed.cumsum()
cumsum.plot()
cumsum.max()
#%%%
current_total_deaths = cumsum.loc["2021-03-20"].unstack()
for (x, y) in [(D2, D0), (D1, D0), (D1, D2)]:
    current_total_deaths[f"{x} vs {y}"] = (
        current_total_deaths[y] - current_total_deaths[x]
    )

write_to_file(ANALYSIS_NOTES, "SimpleAnalysis", current_total_deaths.to_markdown())

# %%
def calc_immunity_1d_age():
    # Load data
    vacc = get_vaccination_data(per_million=False).astype(int)
    age = get_age_data()  #

    # Make 2 tier index & change order of age-brackets
    cols = set(vacc.columns) & set(age.index)  # countries available in both datasets
    age_groups = list(reversed(age.columns))  # age brackets
    age = age[age_groups]  # most important groups first
    new_cols = list(itertools.product(cols, age_groups))
    result = pd.DataFrame(0, index=vacc.index, columns=new_cols)  # immunity [0,1]
    need_1 = age.copy()  # needs 1 dose
    need_1[["0-4", "5-14"]] = 0  # young people don't get vaccine, tough luck!
    result.columns = pd.MultiIndex.from_tuples(result.columns)
    #
    num_days = len(vacc)
    days = np.arange(result.shape[0])
    for (day, row), i in zip(vacc.iterrows(), days):
        days_since = [max(0, x - i) for x in range(num_days)]
        for country in cols:
            new_vac = row[country]
            if country not in need_1.index:
                print(country)
                continue
            n1 = need_1.loc[country]
            get_one = []
            for grp in age_groups:
                need = n1[grp]
                if need == 0:
                    continue
                # print(f"{grp}: {need} {new_vac}")
                if need > new_vac:
                    get_one.append((grp, new_vac))
                    need_1.loc[country][grp] -= new_vac
                    new_vac = 0
                    break  # most important group not finished, break here
                elif need > 0:
                    get_one.append((grp, need))
                    need_1.loc[country][grp] = 0
                    new_vac -= need
            if new_vac:
                print(country, new_vac)
            for grp, n in get_one:
                # n = number of vacc
                # this must be normalized by size of group in question
                p = n / age.loc[country][grp]
                result[country, grp] += [e * p for e in map(VACC.one_dose, days_since)]
    for c in cols:
        # calculate weighted mean immunisation for whole countries
        population = age.loc[c]
        element_wise_mult = (result[c] * population[age_groups]).sum(axis=1)
        result[c, "Total"] = element_wise_mult / age.loc[c].sum()
    return result


def calc_immunity_2d_age():
    # Load data
    vacc = get_vaccination_data(per_million=False).astype(int)
    age = get_age_data()  #

    # Make 2 tier index & change order of age-brackets
    cols = set(vacc.columns) & set(age.index)  # countries available in both datasets
    age_groups = list(reversed(age.columns))  # age brackets
    age = age[age_groups]  # most important groups first
    new_cols = list(itertools.product(cols, age_groups))
    result = pd.DataFrame(0, index=vacc.index, columns=new_cols)  # immunity [0,1]
    need_1 = age.copy()  # needs 1 dose
    need_1[["0-4", "5-14"]] = 0  # young people don't get vaccine, tough luck!
    result.columns = pd.MultiIndex.from_tuples(result.columns)
    #
    num_days = len(vacc)
    days = np.arange(result.shape[0])
    BACKLOG = defaultdict(lambda: deque([0] * VACC.days_between_shots))
    for (day, row), i in zip(vacc.iterrows(), days):
        days_since = [max(0, x - i) for x in range(num_days)]
        for country in cols:
            # Add backlog mechanism from calc_immunity_2d above
            backlog = BACKLOG[country]  # get backlog of country
            need_2nd = backlog.popleft()  # remove first
            total_vacs_of_day = row[country]
            if need_2nd > total_vacs_of_day:
                new_vac_on_day = 0
                # give vacc to those that need 2nd shot
                # and add remaining to backlog for next day
                didnt_get_second = need_2nd - total_vacs_of_day
                backlog[0] += didnt_get_second
            else:
                new_vac_on_day = total_vacs_of_day - need_2nd
            backlog.append(new_vac_on_day)  # add new one

            new_vac = new_vac_on_day
            if country not in need_1.index:
                print(country)
                continue
            n1 = need_1.loc[country]
            get_one = []
            for grp in age_groups:
                need = n1[grp]
                if need == 0:
                    continue
                # print(f"{grp}: {need} {new_vac}")
                if need > new_vac:
                    get_one.append((grp, new_vac))
                    need_1.loc[country][grp] -= new_vac
                    new_vac = 0
                    break  # most important group not finished, break here
                elif need > 0:
                    get_one.append((grp, need))
                    need_1.loc[country][grp] = 0
                    new_vac -= need
            if new_vac:
                print(country, new_vac)
            for grp, n in get_one:
                # n = number of vacc
                # this must be normalized by size of group in question
                p = n / age.loc[country][grp]
                result[country, grp] += [e * p for e in map(VACC.two_dose, days_since)]
    for c in cols:
        # calculate weighted mean immunisation for whole countries
        population = age.loc[c]
        element_wise_mult = (result[c] * population[age_groups]).sum(axis=1)
        result[c, "Total"] = element_wise_mult / age.loc[c].sum()
    return result


if True:
    if __name__ == "__main__":
        imm1d_age = calc_immunity_1d_age()
        imm2d_age = calc_immunity_2d_age()


def guesstimate_excess_deaths_age(imm1, imm2):
    """Takes two estimated immunities and the resulting death count
    and scales death count

    Args:
        immunity ([type]): [description]
        deaths ([type]): [description]
    """
    deaths = get_death_data_by_age().loc[imm1.index]
    imm = [None, imm1, imm2]  # None to have 1D in [1] and 2D in [2]

    countries = set(deaths.columns) & set(imm1.columns)
    scaled_deaths = dict()
    for country in countries:
        if country[0] != "Austria":
            continue
        print(country)
        f1 = 1
        f2 = 2
        d = deaths[country]
        i1 = imm[f1][country]
        i2 = imm[f2][country]
        display(d)
        display(i1)
        display(i2)
        scaled_deaths[(*country, D0)] = (d / (1 - i2)).fillna(0).astype(int)
        scaled_deaths[(*country, D1)] = (d / (1 - i2) * (1 - i1)).fillna(0).astype(int)
        scaled_deaths[(*country, D2)] = d.fillna(0).astype(int)

    df = pd.DataFrame(scaled_deaths)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


ed_age = guesstimate_excess_deaths_age(imm1d_age, imm2d_age)
#%%
d_total = ed_age.sum(axis=1, level=[0, 2]).cumsum()
d_total[at]

# %%
