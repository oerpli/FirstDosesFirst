#%%
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd

# %%
SOURCE = r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"
SOURCE_DEATHS = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"


def get_death_data(extend_by_days=0):
    df_raw = pd.read_csv(SOURCE_DEATHS)
    df_raw["date"] = pd.to_datetime(df_raw["date"])
    death_column = "new_deaths"
    death_column = "new_deaths_smoothed"
    df = df_raw.pivot(index="date", columns="location", values=death_column)
    df = df.fillna(0)
    # Add additional rows on bottom
    start = df.index.max()
    new_range = pd.date_range(start, periods=extend_by_days + 1)[1:]
    add_below = pd.DataFrame(np.nan, index=new_range, columns=df.columns)
    df = pd.concat([df, add_below])
    df.ffill()
    return df


def get_vaccination_data(extend_by_days=0):
    """Load data from CSV and prepare it for use

    Args:
        extend_by_days (int, optional): Add days at end of DF, must be >= 0
    """
    df_raw = pd.read_csv(SOURCE)
    df_raw["date"] = pd.to_datetime(df_raw["date"])
    vac_pp_col = "daily_vaccinations_per_million"
    df = df_raw.pivot(index="date", columns="location", values=vac_pp_col)
    df = df.fillna(0)
    # Add additional rows on bottom
    start = df.index.max()
    new_range = pd.date_range(start, periods=extend_by_days + 1)[1:]
    add_below = pd.DataFrame(0, index=new_range, columns=df.columns)
    df = pd.concat([df, add_below])
    return df


# %% Data for Immunity stemming from Vaccination:

base_immunity = 0
x = 21  # 3 weeks
DAYS_BETWEEN_SHOTS = x
eff_after_fst_x = 0.65
y = 35  # 5 weeks
eff_after_fst_y = 0.85
z = 14  # 2 weeks
eff_after_snd_z = 0.98
total = x + y + z


one_dose = [
    (0, base_immunity),
    (x, eff_after_fst_x),
    (x + y, eff_after_fst_y),
]
two_dose = [
    (0, 0),
    (x, eff_after_fst_x),
    (x + z, eff_after_snd_z),
]

days = pd.DataFrame({"days": list(range(total))}).set_index("days")
eff_1d = pd.DataFrame(one_dose, columns=["days", "one_dose"]).set_index("days")
eff_2d = pd.DataFrame(two_dose, columns=["days", "two_dose"]).set_index("days")

# create df from interpolation of data points
combined = days.join(eff_1d).join(eff_2d).sort_index().interpolate(axis=0)

# function to get expected immunity after n days for 1d/2d regime
def get_eff(doses, days):
    x = combined.one_dose if doses == 1 else combined.two_dose
    if days > len(combined) - 1:
        return x.max()
    else:
        return x[days]


# for ease of use
one_dose = lambda x: get_eff(1, x)
two_dose = lambda x: get_eff(2, x)


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
        for c in cols:
            days_from_jab = [max(0, x - i) for x in range(num_days)]
            result[c] += [x * row[c] for x in map(one_dose, days_from_jab)]
    result /= 1e6
    return result


def calc_immunity_2d(df):
    """Does the same as `calc_immunity_1d` for two doses.
    This is achieved by having a backlog for each country.
    - If someone is vaccinated, they are added to a deque
    - After N days (whatever the time  between vaccs) the people from backlog are prioritised
        - on day X there are 100 vaccs, 5 people on backlog: 5 snd doses, 95 new doses, put 95 on backlog on day X+N
        - on day Y 100 vaccs, 105 on backlog: no new doses, but 5 remain, put 5 on backlog of Y+1
    """
    # Init backlog with all zeros
    BACKLOG = defaultdict(lambda: deque([0] * DAYS_BETWEEN_SHOTS))
    df_columns = list(df.columns)
    result = pd.DataFrame(0, index=df.index, columns=df_columns)
    num_days = len(df)
    days = np.arange(result.shape[0])
    cols = list(df.columns)
    for (_, row), i in zip(df.iterrows(), days):
        for c in cols:
            backlog = BACKLOG[c]  # get backlog of country
            need_2nd = backlog.popleft()  # remove first
            total_vacs = row[c]
            if need_2nd > total_vacs:
                new_vacs = 0
                # add leftover backlog for next day
                backlog[0] += need_2nd - total_vacs
            else:
                new_vacs = total_vacs - need_2nd
            backlog.append(new_vacs)  # add new one
            days_from_jab = [max(0, x - i) for x in range(num_days)]
            result[c] += [x * new_vacs for x in map(two_dose, days_from_jab)]
    result /= 1e6
    return result


#%%
countries = ["Austria", "United States", "United Kingdom"]
dvs = get_vaccination_data(extend_by_days=100)[countries]
dds = get_death_data(extend_by_days=100)[countries][dvs.index.min() :]
#%%
dds = dds.ffill()

imm1 = calc_immunity_1d(dvs)
imm2 = calc_immunity_2d(dvs)


#%%
current_dosing = {
    "Austria": 2,
    "United States": 2,
    "United Kingdom": 1,
    "Test": 2,
}

at = "Austria"
uk = "United Kingdom"
us = "United States"


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
        f1 = method[country]  # 1 or 2
        f2 = 3 - f1  # the other one
        scaled_deaths[country] = (
            deaths[country] / (1 + imm[f2][country]) * (1 + imm[f1][country])
        )
    return pd.DataFrame(scaled_deaths).join(deaths, rsuffix="_orig")


ed = guesstimate_excess_deaths(imm1, imm2, dds, current_dosing)
ed[[at, at + "_orig"]].cumsum().plot()
ed[[us, us + "_orig"]].plot()
ed[[uk, uk + "_orig"]].plot()

#%%
cumsum = ed.cumsum()
cumsum.plot()
cumsum.max()

# %%