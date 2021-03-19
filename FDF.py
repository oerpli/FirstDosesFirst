#%%
from datetime import datetime
from collections import defaultdict, deque
from os import write
from pathlib import Path

import numpy as np
import pandas as pd

from utility import write_to_file


TODAY = datetime.now().date().strftime("%Y-%m-%d")

ANALYSIS_NOTES = Path("writeup") / "analysis.md"


# %%
SOURCE_VACCINATIONS = r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"
SOURCE_DEATHS = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"
# CDC https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-S/9bhg-hcku/
DEATH_DISTRIBUTION = Path(r"./data/death_count_by_age.csv")
# Population worldwide - age brackets
POPULATION_DATA = Path(r"./data/owid-population.csv")

DATA = {
    "population": r"https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Population%20by%20age%20group%20to%202100%20(based%20on%20UNWPP%2C%202017%20medium%20scenario)/Population%20by%20age%20group%20to%202100%20(based%20on%20UNWPP%2C%202017%20medium%20scenario).csv",
}

D0 = "0D"
D1 = "1D"
D2 = "2D"


current_dosing = {
    "Austria": 2,
    "United States": 2,
    "United Kingdom": 1,
    "Test": 2,
}

at = "Austria"
uk = "United Kingdom"
us = "United States"


def get_age_data():
    #%% get raw data from owid (source is UN afaik)
    df = pd.read_csv(POPULATION_DATA)
    df = df[df.Year == 2020]
    # rename columns to be less wordy
    rename = {
        "Entity": "Location",
        "Under 15 years old (UNWPP, 2017)": "0-15",
        "Working age (15-64 years old) (UNWPP, 2017)": "15-64",
        "65+ years old (UNWPP, 2017)": "65-99",
        "Under 5 years old (UNWPP, 2017)": "0-4",
        "5-14 years old (UNWPP, 2017)": "5-14",
        "15-24 years old (UNWPP, 2017)": "15-24",
        "25-64 years old (UNWPP, 2017)": "25-64",
    }
    df = df.rename(rename, axis=1)
    # age brackets don't match with population data, use data from USA to split up groups
    # https://www.census.gov/data/tables/time-series/demo/popest/2010s-national-detail.html
    # basically, assume that age distribution of USA is broadly representative of whole world
    age_factors = {  # each letter group sums up to 1
        "0-4": {(0, 4): 19576683 / 19576683},  # A
        "5-14": {  # B
            (5, 9): 20195895 / 40994163,
            (10, 14): 20798268 / 40994163,
        },
        "15-24": {  # C
            (15, 19): 21054570 / 42687510,
            (20, 24): 21632940 / 42687510,
        },
        "25-64": {  # D
            (25, 29): 23509016 / 170922904,
            (30, 34): 22431305 / 170922904,
            (35, 39): 21737521 / 170922904,
            (40, 44): 19921623 / 170922904,
            (45, 49): 20397751 / 170922904,
            (50, 54): 20477151 / 170922904,
            (55, 59): 21877391 / 170922904,
            (60, 64): 20571146 / 170922904,
        },
        "65-99": {  # E
            (65, 69): 17455001 / 54058263,
            (70, 74): 14028432 / 54058263,
            (75, 79): 9652665 / 54058263,
            (80, 84): 6317207 / 54058263,
            (85, 99): 6604958 / 54058263,
        },
    }
    # rearrange and drop useless stuff
    new_groups = {"Location": df["Location"]}
    for group, subgroups in age_factors.items():
        for (lower, upper), factor in subgroups.items():
            new_groups[f"{lower}-{upper}"] = (df[group] * factor).astype(int)
    return pd.DataFrame(new_groups).set_index("Location")


age = get_age_data()
age

#%%
def get_death_data(extend_by_days=0, smoothed=True):
    # Smoothed data should lessen artifacts from data-reporting delays
    death_column = "new_deaths_smoothed" if smoothed else "new_deaths"
    path = Path(f"./cache/deaths_{TODAY}.pqt")
    if path.exists():
        df_raw = pd.read_parquet(path)
    else:
        df_raw = pd.read_csv(SOURCE_DEATHS)
        df_raw.to_parquet(path, compression="gzip")
    df_raw["date"] = pd.to_datetime(df_raw["date"])
    df = df_raw.pivot(index="date", columns="location", values=death_column)
    df = df.fillna(0)
    # Add additional rows on bottom
    start = df.index.max()
    new_range = pd.date_range(start, periods=extend_by_days + 1)[1:]
    add_below = pd.DataFrame(np.nan, index=new_range, columns=df.columns)
    df = pd.concat([df, add_below])
    df.ffill()
    return df


deaths = get_death_data()

#%%
def get_death_by_age_us():
    df = pd.read_csv(DEATH_DISTRIBUTION)
    # Only get data from 2020 because vaccination changes distribution in 2021
    #! This will mess up things when most old people are vaccinated and distribution changes
    df = df[df["Group"] == "By Year"]
    df = df[df["Year"] == 2020]
    df = df[df["State"] == "United States"]
    df = df[df["Sex"] == "All Sexes"]
    #
    df = df.set_index("Age Group")[["COVID-19 Deaths"]].iloc[2:]
    df = df.rename({"COVID-19 Deaths": "Deaths"}, axis=1)
    # some age groups are overlapping (why???)
    df = df.transpose()[
        [
            # "0-17 years",
            "1-4 years",
            "5-14 years",
            "15-24 years",
            # "18-29 years",
            "25-34 years",
            # "30-39 years",
            "35-44 years",
            # "40-49 years",
            "45-54 years",
            # "50-64 years",
            "55-64 years",
            "65-74 years",
            "75-84 years",
            "85 years and over",
        ]
    ].rename(
        {
            "1-4 years": "0-4",  # Mislabeled but matches with UN data and likely irrelevant
            "5-14 years": "5-14",
            "15-24 years": "15-24",
            "25-34 years": "25-34",
            "35-44 years": "35-44",
            "45-54 years": "45-54",
            "55-64 years": "55-64",
            "65-74 years": "65-74",
            "75-84 years": "75-84",
            "85 years and over": "85-99",
        },
        axis=1,
    )
    df = df.transpose()
    df["DeathShare"] = df["Deaths"] / df["Deaths"].sum()
    return df


deaths_by_age = get_death_by_age_us()
deaths_by_age

#%%


def get_vaccination_data(extend_by_days=0):
    """Load data from CSV and prepare it for use

    Args:
        extend_by_days (int, optional): Add days at end of DF, must be >= 0
    """
    df_raw = pd.read_csv(SOURCE_VACCINATIONS)
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
eff_after_fst_x = 0.75
y = 35  # 5 weeks
eff_after_fst_y = 0.85
z = 14  # 2 weeks
eff_after_snd_z = 0.95
total = x + y + z


# In either case, vacc starts with 7st dose and divergence happens after ~3 weeks
first_dose = [
    (0, base_immunity),
    (7, base_immunity + 0.005),
    (x, eff_after_fst_x),
]

one_dose = [*first_dose, (x + y, eff_after_fst_y)]
two_dose = [*first_dose, (x + z, eff_after_snd_z)]

days = pd.DataFrame({"days": list(range(total))}).set_index("days")
eff_1d = pd.DataFrame(one_dose, columns=["days", "one_dose"]).set_index("days")
eff_2d = pd.DataFrame(two_dose, columns=["days", "two_dose"]).set_index("days")

# create df from interpolation of data points
combined = days.join(eff_1d).join(eff_2d).sort_index().interpolate(axis=0)


efficacy_table = (combined.iloc[:40:3] * 100).astype(int)
write_to_file(ANALYSIS_NOTES, "EfficacyTable", efficacy_table.to_markdown())
#%%

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

TOTAL_VAC = defaultdict(list)
TOTAL_JAB = defaultdict(list)


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
        for country in cols:
            new_vac = row[country]
            days_from_jab = [max(0, x - i) for x in range(num_days)]
            result[country] += [x * new_vac for x in map(one_dose, days_from_jab)]
            TOTAL_VAC[(country, D1)].append(new_vac)
            TOTAL_JAB[(country, D1)].append(new_vac)
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
            days_from_jab = [max(0, x - i) for x in range(num_days)]
            result[country] += [
                x * new_vac_on_day for x in map(two_dose, days_from_jab)
            ]
            TOTAL_VAC[(country, D2)].append(new_vac_on_day)
            TOTAL_JAB[(country, D2)].append(total_vacs_of_day)
    result /= 1e6
    return result


countries = ["Austria", "United States", "United Kingdom"]
dvs = get_vaccination_data(extend_by_days=15)[countries]
dds = get_death_data(extend_by_days=15)[countries][dvs.index.min() :]
dds = dds.ffill()

imm1 = calc_immunity_1d(dvs)
imm2 = calc_immunity_2d(dvs)

df_V = pd.DataFrame(TOTAL_VAC)
df_V.index = imm1.index
df_V.columns = pd.MultiIndex.from_tuples(df_V.columns)
df_J = pd.DataFrame(TOTAL_JAB)
df_J.index = imm1.index
df_J.columns = pd.MultiIndex.from_tuples(df_J.columns)

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


#%%
age = get_age_data()
age


def get_risk_by_age():
    # data from CDC
    # https://www.cdc.gov/coronavirus/2019-ncov/images/need-extra-precautions/319360-A_COVID-19_RiskForSevereDisease_Race_Age_2.18_p1.jpg
    # tuples denote inclusive ranges
    age_risk_factor = {
        (0, 4): 2,  # X
        (5, 17): 1,  # reference group A
        (18, 29): 15,  # B
        (30, 39): 45,  # C
        (40, 49): 130,  # D
        (50, 64): 400,  # E
        (65, 74): 1100,  # F
        (75, 84): 2800,  # G
        (85, 99): 7900,  # H
    }


# %%
