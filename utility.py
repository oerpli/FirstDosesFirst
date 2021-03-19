#%%
from datetime import datetime

import re
from pathlib import Path
from numpy import isin
import pandas as pd
import numpy as np


SOURCE_VACCINATIONS = r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"
SOURCE_DEATHS = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"
DEATH_DISTRIBUTION = Path(r"./data/death_count_by_age.csv")
# Population worldwide - age brackets
POPULATION_DATA = Path(r"./data/owid-population.csv")

DATA = {
    "population": r"https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Population%20by%20age%20group%20to%202100%20(based%20on%20UNWPP%2C%202017%20medium%20scenario)/Population%20by%20age%20group%20to%202100%20(based%20on%20UNWPP%2C%202017%20medium%20scenario).csv",
}


DATA = {
    # OWID
    "vaccinations": r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv",
    # OWID, no idea from where
    "deaths": r"https://covid.ourworldindata.org/data/owid-covid-data.csv",
    # CDC https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-S/9bhg-hcku/
    "deaths_by_age": Path(r"./data/death_count_by_age.csv"),
    # OWID, based on UN data
    "demographics": Path(r"./data/owid-population.csv"),
}


def write_to_file(file, name, value):
    pattern_tag = rf"\[//\]: # \({name}\)"

    pattern_full = rf"({pattern_tag})([\s\S]*)({pattern_tag})"
    file_content = file.read_text()

    # print("===================")
    # print(re.findall(pattern_tag, file_content))
    # print(re.findall(pattern_full, file_content))
    # print("===================")
    repl = re.sub(pattern_full, rf"\1\n\n{value.strip()}\n\n\3", file_content)
    file.write_text(repl)


# %%
def get_data_with_cache(name):
    source = DATA[name]
    if isinstance(source, Path):
        return pd.read_csv(source)
    elif isinstance(source, str):
        today = datetime.now().date().strftime("%Y-%m-%d")
        path = Path(f"./cache/{name}_{today}.pqt")
        if path.exists():
            df_raw = pd.read_parquet(path)
        else:
            df_raw = pd.read_csv(source)
            df_raw.to_parquet(path, compression="gzip")
        return df_raw
    else:
        print("Source must be either string or Path")


def get_vaccination_data(extend_by_days=0):
    """Load data from CSV and prepare it for use

    Args:
        extend_by_days (int, optional): Add days at end of DF, must be >= 0
    """
    df_raw = get_data_with_cache("vaccinations")
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


def get_death_data(extend_by_days=0, smoothed=True):
    # Smoothed data should lessen artifacts from data-reporting delays
    death_column = "new_deaths_smoothed" if smoothed else "new_deaths"
    df_raw = get_data_with_cache("deaths")
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


def get_death_distr_by_age_us():
    df = get_data_with_cache("deaths_by_age")
    # Only get data from 2020 because vaccination changes distribution in 2021
    #! This will mess up things when most old people are vaccinated and distribution changes
    df = df[df["Group"] == "By Year"]
    df = df[df["Year"] == 2020]
    df = df[df["State"] == "United States"]
    df = df[df["Sex"] == "All Sexes"]
    #
    df = df.set_index("Age Group")[["COVID-19 Deaths"]].iloc[2:]
    df = df.rename({"COVID-19 Deaths": "Deaths"}, axis=1)
    # some age groups are overlapping (why???) - remove those
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


def get_age_data():
    #%% get raw data from owid (source is UN afaik)
    df = get_data_with_cache("demographics")
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

# %%
