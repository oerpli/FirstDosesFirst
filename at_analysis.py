#%%
from utility import *
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import altair as alt

sns.set_theme()
from pathlib import Path

PLOT_FOLDER = Path("Y:/GitRepos/oerpli.github.io/fdf")

ALTAIR_WIDTH = 500

region = "Vorarlberg"
short = "vlbg"
vlbg_img = OUT_FOLDER / "img" / short
vlbg_report = OUT_FOLDER / "CaseStudyVlbg.md"

deaths_at = get_deaths_by_age_at()


def save_fig(ax, name, alt_text=None, caption=None):
    path = vlbg_img / f"{name}.png"
    plt.savefig(path)
    write_img_to_file(vlbg_report, name, path, alt_text=alt_text, caption=caption)


def save_table(df: pd.DataFrame, name: str):
    df.columns = map(lambda x: " ".join(x), df.columns)
    write_to_file(vlbg_report, name, df.to_markdown())


#%% Get Data Austria
df_full = get_vaccinations_at()
population = get_demographics_at()
pt = pd.DataFrame(population.unstack()).T

# Some global stuff
plt.rcParams["figure.figsize"] = [10, 5]

O = "Old"
Y = "Young"
T = "Total"


#%% Select subset of region
df = df_full[region]
pop = pt[region].loc[0]


#%% Plot overall vaccinations
cumTotalVac = (df[D1] + df[D2]).cumsum()
ax = cumTotalVac.plot(title="Cumulative number of vaccinations")
save_fig(ax, "VaccTotal")

#%% Per population
ax = (cumTotalVac / pop).plot(title="Vaccinations per person in each age group")
save_fig(ax, "VaccRelative")


#%% Prepare table
def prepare_table(x, name, prec=1):
    df = pd.concat(x).T
    df.columns = [(name, "Absolute"), (name, "%")]
    df[(name, "%")] = df[(name, "%")].astype(float).round(2)
    return fix_multilevel(df)


#%% D1 per pop
d1a = df[D1].cumsum()
ax = (d1a / pop).plot(title="Share of age group with at least 1 dose")
save_fig(ax, "D1Relative")

x = [d1a.iloc[-2:-1], d1a.iloc[-2:-1] / pop * 100]
d1data = prepare_table(x, "1 dose")
save_table(d1data, "D1Data")

#%% Same for D2
d2a = df[D2].cumsum()
ax = (d2a / pop).plot(title="Share of age group that received 2 doses")
save_fig(ax, "D2Relative")

x = [d2a.iloc[-2:-1], d2a.iloc[-2:-1] / pop * 100]
d2data = prepare_table(x, "2 doses")

save_table(d2data, "D2Data")

#%% Only 1 Dose
d1only = d1a - d2a
ax = d1only.plot(title="Share of age group that received only 1 dose")
save_fig(ax, "D1Only")
x = [d1only.iloc[-2:-1], d1only.iloc[-2:-1] / pop * 100]
d1only = prepare_table(x, "Only 1 dose")
save_table(d1only, "D1OnlyData")


#%% Combined table
d1d2o1 = d1data.join(d2data).join(d1only)  # .sort_index(axis=1)
d1d2o1
# save_table(d1d2o1, "CompleteTable")
#%% df[[D1,D2]].cumsum().plot()


region_names = {
    "Burgenland": "at-bg",
    "Kärnten": "at-k",
    "Niederösterreich": "at-noe",
    "Oberösterreich": "at-ooe",
    "Salzburg": "at-sbg",
    "Steiermark": "at-stmk",
    "Tirol": "at-t",
    "Vorarlberg": "at-vlbg",
    "Wien": "at-vienna",
    "Österreich": "at",
}

# region = "Österreich"
# df = df_full[region]
# pop = pt[region].loc[0]
# dfv = df[[D1, D2]]


def get_avg_immunity(df, pop):
    df = df.cumsum().copy()
    df[D1] -= df[D2]  # D1 contains now only 1st dose instead
    imm_p = df[D1].copy() * 0
    imm_p += (df[D1] * 0.89) / pop
    imm_p += (df[D2] * 0.95) / pop
    return imm_p


def create_altair_plot_immunity(imm, title, name):
    chart_data = pd.melt(
        imm.reset_index(),
        id_vars="Date",
        value_vars=imm.columns,
        var_name="Age Group",
        value_name="Immunity",
    )
    chart = (
        alt.Chart(chart_data, width=ALTAIR_WIDTH)
        .mark_line(clip=True)
        .encode(
            x="Date",
            y=alt.Y("Immunity", scale=alt.Scale(domain=(0, 1))),
            color="Age Group",
            strokeDash="Age Group",
        )
        .properties(title=f"Estimated Immunity: {title}")
        .interactive()
    )
    chart.save(str(PLOT_FOLDER / f"imm_{name}.json"))
    return chart


#%%
def create_altair_plot_vacc(vacc, title, name):
    chart_data = pd.melt(
        vacc.reset_index(),
        id_vars="Date",
        value_vars=vacc.columns,
        var_name="Age Group",
        value_name="Vaccinations",
    )
    chart = (
        alt.Chart(chart_data, width=ALTAIR_WIDTH)
        .mark_line(clip=True)
        .encode(
            x="Date",
            y="Vaccinations",
            color="Age Group",
            strokeDash="Age Group",
        )
        .properties(title=f"Number of vaccinations: {title}")
        .interactive()
    )
    chart.save(str(PLOT_FOLDER / f"vacc_{name}.json"))
    return chart


#%%
def calc_weighted_immunity(imm, weights):
    dfs = []
    for name, weight in weights.items():
        imm_w = (imm * weight).sum(axis=1) / weight.sum()
        df = pd.DataFrame({name: imm_w})
        dfs.append(df)
    a, *bs = dfs
    for b in bs:
        a = a.join(b)
    return a


weightings = {
    "Avg": pop,  # calc immunity on average
    "AvgD": deaths_at.loc["Deaths"],  # weighted by deaths
}

normal_imm = calc_weighted_immunity(imm_normal, weightings)
fdf_imm = calc_weighted_immunity(imm_fdf, weightings)

#%%
regions = region_names  # all regions
regions = {"Vorarlberg": "test"}  # for debugging
for k, v in regions.items():
    df = df_full[k]  # get subset of region
    pop = pt[k].loc[0]  # get population of region
    dfv = df[[D1, D2]]  # 1D,2D get vaccination data of region
    # Choose one from the following two
    rd = redistribute_doses(dfv, pop, distr_first=False)  # more conservative
    # rd = redistribute_doses(dfv, pop, distr_first=True) # also reassign first doses based on prio

    imm_normal = get_avg_immunity(dfv, pop)
    imm_fdf = get_avg_immunity(rd, pop)
    create_altair_plot_immunity(imm_normal, f"{k}", f"real_{v}")
    create_altair_plot_immunity(imm_fdf, f"{k} (FDF)", f"fdf_{v}")
    create_altair_plot_vacc((dfv[D1] + dfv[D2]).cumsum(), f"{k} Total", f"real_t_{v}")
    create_altair_plot_vacc(dfv[D1].cumsum(), f"{k} {D1}", f"real_d1_{v}")
    create_altair_plot_vacc(dfv[D2].cumsum(), f"{k} {D2}", f"real_d2_{v}")
    create_altair_plot_vacc(rd[D1].cumsum(), f"{k} {D1} (FDF)", f"fdf_d1_{v}")
    create_altair_plot_vacc(rd[D2].cumsum(), f"{k} {D2} (FDF)", f"fdf_d2_{v}")

    # plot immunity levels with matplotlib
    ax = imm_normal.plot(title=f"Immunity {k}")
    ax.set_ylim(0, 1)
    ax2 = imm_fdf.plot(title=f"FDF Immunity {k}")
    ax2.set_ylim(0, 1)

# %%
create_altair_plot_vacc(rd[D2].cumsum(), f"{k} {D2} (FDF)", f"test")
# %%
