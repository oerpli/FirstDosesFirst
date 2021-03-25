#%%
from datetime import datetime

import re
from pathlib import Path
import pandas as pd
import numpy as np


OUT_FOLDER = Path("writeup")

# %% Some shorthands
D0 = "0D"
D1 = "1D"
D2 = "2D"

from enum import Enum


class Sources(Enum):
    Vaccinations = 1
    Deaths = 2
    DeathsByAge = 3
    Demographics = 4
    VaccAt = 5


DATA = {
    # OWID
    Sources.Vaccinations: r"https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv",
    # OWID, no idea from where
    Sources.Deaths: r"https://covid.ourworldindata.org/data/owid-covid-data.csv",
    # CDC https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-S/9bhg-hcku/
    Sources.DeathsByAge: Path(r"./data/death_count_by_age.csv"),
    # OWID, based on UN data
    Sources.Demographics: Path(r"./data/owid-population.csv"),
    Sources.VaccAt: r"https://info.gesundheitsministerium.at/data/timeline-eimpfpass.csv",
}



def fix_multilevel(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


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


def write_img_to_file(file, name, path: Path, alt_text="", caption=""):
    path = path.relative_to(OUT_FOLDER)
    x = str(path).replace("\\", "/")
    # print(x)
    c = f"{caption}\n".strip()  # empty if caption is empty
    img_tag = f"{c}![{alt_text}]({x})"
    write_to_file(file, name, img_tag)


# %%
def get_data_with_cache(name, sep=None) -> pd.DataFrame:
    source = DATA[name]
    if isinstance(source, Path):
        return pd.read_csv(source, sep=sep)
    elif isinstance(source, str):
        today = datetime.now().date().strftime("%Y-%m-%d")
        path = Path(f"./cache/{name}_{today}.pqt")
        if path.exists():
            df_raw = pd.read_parquet(path)
        else:
            df_raw = pd.read_csv(source, sep=sep)
            df_raw.to_parquet(path, compression="gzip")
        return df_raw
    else:
        raise Exception("Source must be either string or Path")


def get_vaccination_data(extend_by_days=0, per_million=True) -> pd.DataFrame:
    """Load data from CSV and prepare it for use

    Args:
        extend_by_days (int, optional): Add days at end of DF, must be >= 0
    """
    df_raw = get_data_with_cache(Sources.Vaccinations)
    df_raw["date"] = pd.to_datetime(df_raw["date"])
    vac_pp_col = (
        "daily_vaccinations_per_million" if per_million else "daily_vaccinations"
    )
    df = df_raw.pivot(index="date", columns="location", values=vac_pp_col)
    df = df.fillna(0)
    # Add additional rows on bottom
    start = df.index.max()
    new_range = pd.date_range(start, periods=extend_by_days + 1)[1:]
    add_below = pd.DataFrame(0, index=new_range, columns=df.columns)
    df = pd.concat([df, add_below])
    return df


def get_death_data(extend_by_days=0, smoothed=True) -> pd.DataFrame:
    # Smoothed data should lessen artifacts from data-reporting delays
    death_column = "new_deaths_smoothed" if smoothed else "new_deaths"
    df_raw = get_data_with_cache(Sources.Deaths)
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


def get_death_distr_by_age_us() -> pd.DataFrame:
    df = get_data_with_cache(Sources.DeathsByAge)
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


def get_age_data() -> pd.DataFrame:
    #%% get raw data from owid (source is UN afaik)
    df = get_data_with_cache(Sources.Demographics)
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
    # as death data 10y intervals, recalculate those brackets:
    df = pd.DataFrame(new_groups).set_index("Location")
    ages_new_brackets = {
        "0-4": ["0-4"],
        "5-14": ["5-9", "10-14"],
        "15-24": ["15-19", "20-24"],
        "25-34": ["25-29", "30-34"],
        "35-44": ["35-39", "40-44"],
        "45-54": ["45-49", "50-54"],
        "55-64": ["55-59", "60-64"],
        "65-74": ["65-69", "70-74"],
        "75-84": ["75-79", "80-84"],
        "85-99": ["85-99"],
    }
    return pd.DataFrame({k: df[v].sum(axis=1) for k, v in ages_new_brackets.items()})


#%%
def get_death_data_by_age() -> pd.DataFrame:
    death_distr = get_death_distr_by_age_us().transpose().loc["DeathShare"]
    deaths = get_death_data()
    age = get_age_data()
    age_t = age.transpose()

    us_distribution = age_t["United States"] / age_t["United States"].sum()
    countries = set(age.index) & set(deaths.columns)
    # Mostly small countries are missing, but also:
    # - Czechia, because it's sometimes called Czech Republic
    # - Serbia ?
    # - Kosovo ?
    columns = dict()
    for country in countries:
        age_distr = age_t[country] / age_t[country].sum()  # percentage in each bracket
        relative_to_us = age_distr / us_distribution  # not sure if this is a good idea
        x = relative_to_us * death_distr
        death_distr_x = x / x.sum()
        for group in death_distr_x.index:
            columns[(country, group)] = deaths[country] * death_distr_x[group]
        columns
    return pd.DataFrame(columns)


# %%


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


#%%
def get_eimpfpass_data(filter_region=None):
    df = get_data_with_cache(Sources.VaccAt)

    # Remove BOM from first column
    clean_special_chars = lambda x: x.replace("\ufeff", "")
    df.columns = map(clean_special_chars, df.columns)

    # Translate columns
    translate = {
        "Datum": "Date",
        "Bevölkerung": "Population",
        "BundeslandID": "StateId",
        "EingetrageneImpfungen": "Vacc",
        # "EingetrageneImpfungenAstraZeneca_1": "",
        # "EingetrageneImpfungenAstraZeneca_2": "",
        # "EingetrageneImpfungenBioNTechPfizer_1": "",
        # "EingetrageneImpfungenBioNTechPfizer_2": "",
        # "EingetrageneImpfungenModerna_1": "",
        # "EingetrageneImpfungenModerna_2": "",
        "EingetrageneImpfungenPro100": "VaccPer100",
        "Name": "Region",
        "Teilgeimpfte": "Vacc_1",
        "TeilgeimpftePro100": "Vacc_2",
        "Vollimmunisierte": "Imm",
        "VollimmunisiertePro100": "ImmPer100",
    }
    df = df.rename(translate, axis=1)
    df["Date"] = pd.to_datetime(df["Date"])

    relevant = [
        "Date",
        "Population",
        "Vacc",
        "VaccPer100",
        "Vacc_1",
        "Vacc_2",
        "Imm",
        "ImmPer100",
    ]

    df_full = df.copy()
    regions = dict()
    for region in df.Region.unique():
        df = df_full[df_full.Region == region]
        groups = {
            D1: {
                "00-24": ["Gruppe<24_M_1", "Gruppe<24_W_1", "Gruppe<24_D_1"],
                "25-34": ["Gruppe_25-34_M_1", "Gruppe_25-34_W_1", "Gruppe_25-34_D_1"],
                "35-44": ["Gruppe_35-44_M_1", "Gruppe_35-44_W_1", "Gruppe_35-44_D_1"],
                "45-54": ["Gruppe_45-54_M_1", "Gruppe_45-54_W_1", "Gruppe_45-54_D_1"],
                "55-64": ["Gruppe_55-64_M_1", "Gruppe_55-64_W_1", "Gruppe_55-64_D_1"],
                "65-74": ["Gruppe_65-74_M_1", "Gruppe_65-74_W_1", "Gruppe_65-74_D_1"],
                "75-84": ["Gruppe_75-84_M_1", "Gruppe_75-84_W_1", "Gruppe_75-84_D_1"],
                "85-99": ["Gruppe_>84_M_1", "Gruppe_>84_W_1", "Gruppe_>84_D_1"],
            },
            D2: {
                "00-24": ["Gruppe<24_M_1", "Gruppe<24_W_1", "Gruppe<24_D_1"],
                "25-34": ["Gruppe_25-34_M_1", "Gruppe_25-34_W_1", "Gruppe_25-34_D_1"],
                "35-44": ["Gruppe_35-44_M_1", "Gruppe_35-44_W_1", "Gruppe_35-44_D_1"],
                "45-54": ["Gruppe_45-54_M_1", "Gruppe_45-54_W_1", "Gruppe_45-54_D_1"],
                "55-64": ["Gruppe_55-64_M_1", "Gruppe_55-64_W_1", "Gruppe_55-64_D_1"],
                "65-74": ["Gruppe_65-74_M_1", "Gruppe_65-74_W_1", "Gruppe_65-74_D_1"],
                "75-84": ["Gruppe_75-84_M_1", "Gruppe_75-84_W_1", "Gruppe_75-84_D_1"],
                "85-99": ["Gruppe_>84_M_2", "Gruppe_>84_W_2", "Gruppe_>84_D_2"],
            },
        }
        dfn = df[relevant].copy()
        # necessary in both
        df = df.set_index(["Date"]).sort_index()
        dfn = dfn.set_index(["Date"]).sort_index()
        for d, g in groups.items():
            for k, v in g.items():
                # Sum over m/f/x, derive to get daily numbers, fill up empty with 0
                dfn[(d, k)] = df[v].sum(axis=1).diff().fillna(0).astype(int)

        dfn.columns = [("Meta", x) if isinstance(x, str) else x for x in dfn.columns]
        # throw away first row as derivative doesn't really work when multiple regions exist
        regions[region] = dfn
    for k, v in regions.items():
        v.columns = [(k, *x) for x in v.columns]
    dft = pd.concat(regions.values(), axis=1)
    dft.columns = pd.MultiIndex.from_tuples(dft.columns)
    selection = dft[
        [
            "Österreich",
            "Burgenland",
            # "KeineZuordnung",
            "Kärnten",
            "Niederösterreich",
            "Oberösterreich",
            "Salzburg",
            "Steiermark",
            "Tirol",
            "Vorarlberg",
            "Wien",
        ]
    ].copy()
    return fix_multilevel(selection)

# %%
