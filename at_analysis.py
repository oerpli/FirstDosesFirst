#%%
import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from dose_redistributing_methods import redistribute_doses
from data_loading import *
from utility import write_img_to_file, write_to_file

from pathlib import Path

sns.set_theme()
PLOT_FOLDER = Path("Y:/GitRepos/oerpli.github.io/fdf")

ALTAIR_WIDTH = 500
plt.rcParams["figure.figsize"] = [10, 5]

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


def get_avg_immunity(df, pop):
    df = df.cumsum().copy()
    df[D1] -= df[D2]  # D1 contains now only 1st dose instead
    imm_p = df[D1].copy() * 0
    imm_p += (df[D1] * 0.89) / pop
    imm_p += (df[D2] * 0.95) / pop
    return imm_p


def create_altair_plot_immunity(imm, title, name=None):
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
    if name:
        chart.save(str(PLOT_FOLDER / f"imm_{name}.json"))
    return chart


#%%
def create_altair_plot_vacc(vacc, title, name=None):
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
    if name:
        chart.save(str(PLOT_FOLDER / f"vacc_{name}.json"))
    return chart


#%%
def create_altair_plot_weighted_immunity(imm_w, title, name=None):
    chart_data = pd.melt(
        imm_w.reset_index(),
        id_vars="Date",
        value_vars=imm_w.columns,
        var_name="Weighted by",
        value_name="Immunity",
    )
    chart = (
        alt.Chart(chart_data, width=ALTAIR_WIDTH)
        .mark_line(clip=True)
        .encode(
            x="Date",
            y=alt.Y("Immunity", scale=alt.Scale(domain=(0, 1))),
            color="Weighted by",
            strokeDash="Weighted by",
        )
        .properties(title=f"Weighted average immunity: {title}")
        .interactive()
    )
    if name:
        chart.save(str(PLOT_FOLDER / f"imm_w{name}.json"))
    return chart


#%%
def create_altair_plot_at_least_1d(df, title, name=None):
    chart_data = pd.melt(
        df.reset_index(),
        id_vars=["Date"],
        value_vars=df.columns,
        var_name="Age group",
        value_name="Fraction",
    )
    chart = (
        alt.Chart(chart_data, width=ALTAIR_WIDTH)
        .mark_line(clip=True)
        .encode(
            x="Date",
            y=alt.Y("Fraction", scale=alt.Scale(domain=(0, 1))),
            color="Age group",
            strokeDash="Age group",
        )
        .properties(title=f"At least one dose: {title}")
        .interactive()
    )
    if name:
        chart.save(str(PLOT_FOLDER / f"_1d_{name}.json"))
    return chart


#%%
def calc_weighted_immunity(imm, weights) -> pd.DataFrame:
    dfs = []
    for name, weight in weights.items():
        imm_w = (imm * weight).sum(axis=1) / weight.sum()
        df = pd.DataFrame({name: imm_w})
        dfs.append(df)
    a, *bs = dfs
    for b in bs:
        a = a.join(b)
    return a


#%%
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


def get_vaccination_rate(df, pop) -> pd.DataFrame:
    vacc_rate = df.copy().cumsum()
    vacc_rate[D1] /= pop
    vacc_rate[D2] /= pop
    return vacc_rate


regions = region_names  # all regions
# regions = {"Österreich": "at"}  # for debugging
for nice, short in regions.items():
    df = df_full[nice]  # get subset of region
    pop = pt[nice].loc[0]  # get population of region
    dfv = df[[D1, D2]]  # 1D,2D get vaccination data of region
    # Choose one from the following two
    rd = redistribute_doses(dfv, pop, distr_first=False)  # more conservative
    rdfd = redistribute_doses(dfv, pop, distr_first=False, fractional_dosing=True)
    # This method basically ignores members of "critical groups" except old people
    # Gives nicer but likely wrong numbers.
    # rd = redistribute_doses(dfv, pop, distr_first=True) # also reassign first doses based on prio

    imm_normal = get_avg_immunity(dfv, pop)
    imm_fdf = get_avg_immunity(rd, pop)

    weightings = {
        "Population": pop,  # calc immunity on average
        "Death distribution": deaths_at.loc["Deaths"],  # weighted by deaths
    }

    imm_w_n = calc_weighted_immunity(imm_normal, weightings)
    imm_w_fdf = calc_weighted_immunity(imm_fdf, weightings)
    imm_w = imm_w_n.join(imm_w_fdf, rsuffix=" (FDF)", lsuffix=" (Normal)")
    per_pop_c = imm_w.columns[0::2]
    per_death_c = imm_w.columns[1::2]
    total = dfv[D1] + dfv[D2]

    # Avg immunity plot per age group, normal and FDF
    create_altair_plot_immunity(imm_normal, f"{nice}", f"real_{short}")
    create_altair_plot_immunity(imm_fdf, f"{nice} (FDF)", f"fdf_{short}")

    # FDF + FD Comparison
    vrr = get_vaccination_rate(dfv, pop)
    vr_fdf = get_vaccination_rate(rd, pop)
    vr_fdf_fd = get_vaccination_rate(rdfd, pop)

    create_altair_plot_at_least_1d(vrr[D1], f"{nice} (normal)")
    create_altair_plot_at_least_1d(vr_fdf[D1], f"{nice} (FDF)")
    create_altair_plot_at_least_1d(vr_fdf_fd[D1], f"{nice} (FDF + FD)")

    # Weighted average immunity for FDF, population and death distribution weighted
    create_altair_plot_weighted_immunity(imm_w[per_pop_c], f"{nice}", f"p_{short}")
    create_altair_plot_weighted_immunity(imm_w[per_death_c], f"{nice}", f"d_{short}")

    # Vaccination progress, Total, Real, alternative FDF data
    create_altair_plot_vacc(total.cumsum(), f"{nice} Total", f"real_t_{short}")
    create_altair_plot_vacc(dfv[D1].cumsum(), f"{nice} {D1}", f"real_d1_{short}")
    create_altair_plot_vacc(dfv[D2].cumsum(), f"{nice} {D2}", f"real_d2_{short}")
    create_altair_plot_vacc(rd[D1].cumsum(), f"{nice} {D1} (FDF)", f"fdf_d1_{short}")
    create_altair_plot_vacc(rd[D2].cumsum(), f"{nice} {D2} (FDF)", f"fdf_d2_{short}")

    # plot immunity levels with matplotlib
    ax = imm_normal.plot(title=f"Immunity {nice}")
    ax.set_ylim(0, 1)
    ax2 = imm_fdf.plot(title=f"FDF Immunity {nice}")
    ax2.set_ylim(0, 1)

# %% Test stuff
create_altair_plot_vacc(rd[D2].cumsum(), f"{nice} {D2} (FDF)")
create_altair_plot_vacc(rd[D2].cumsum(), f"{nice} {D2} (FDF)")
create_altair_plot_vacc(rd[D2].cumsum(), f"{nice} {D2} (FDF)")


since_new_dosing = dfv.loc["2021-03-14":]

young, middle, old = ["25-34", "35-44", "45-54"], ["55-64", "65-74"], ["75-84", "85-99"]
yd1 = since_new_dosing[D1][young].sum().sum()
yd2 = since_new_dosing[D2][young].sum().sum()
md1 = since_new_dosing[D1][middle].sum().sum()
md2 = since_new_dosing[D2][middle].sum().sum()
od1 = since_new_dosing[D1][old].sum().sum()
od2 = since_new_dosing[D2][old].sum().sum()

print(yd1, yd2)
print(md1, md2)
print(od1, od2)

# %% Test germany
if False:
    de = get_vaccinations_de()
    guess_pop_de = pt["Österreich"].loc[0] * 10
    rde = redistribute_doses(de, guess_pop_de, distr_first=True)
    imm_de = get_avg_immunity(rde, guess_pop_de)
    plt = create_altair_plot_immunity(imm_de, "Germany (FDF)", f"fdf_{'de'}")
    display(plt)
    ws = {"Population": guess_pop_de, "Deaths": deaths_at.loc["Deaths"]}
    imm_w = calc_weighted_immunity(imm_de, ws)
    plt = create_altair_plot_weighted_immunity(imm_w, "Germany (FDF)", f"fdf_{'de'}")
    display(plt)


# %%

# %%
# create_altair_plot_weighted_immunity(imm_w[per_death_c], f"{nice}")
# %%
