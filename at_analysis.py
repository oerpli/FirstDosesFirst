#%%
from utility import *
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme()
from pathlib import Path


region = "Vorarlberg"
short = "vlbg"
vlbg_img = OUT_FOLDER / "img" / short
vlbg_report = OUT_FOLDER / "CaseStudyVlbg.md"


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
plt.rcParams["figure.figsize"] = [8, 5]

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
d1only = (d1a - d2a) / pop
ax = d1only.plot(title="Share of age group that received only 1 dose")
save_fig(ax, "D1Only")
d1only = prepare_table(x, "Only 1 dose")
save_table(d1only, "D1OnlyData")


#%% Combined table
# d1d2o1 = fix_multilevel(d1data.join(d2data).join(d1only).swaplevel(axis=1)).sort_index(
#     axis=1
# )
# save_table(d1d2o1, "CompleteTable")
#%% df[[D1,D2]].cumsum().plot()

#%% Get Data for Old and Young
cmp = pd.DataFrame()
for d in [D1, D2]:
    cmp[(d, O, region)] = df[d][[c for c in df[d].columns if c[0] >= "5"]].sum(axis=1)
    cmp[(d, Y, region)] = df[d][[c for c in df[d].columns if c[0] < "5"]].sum(axis=1)

for a in [O, Y]:
    cmp[(T, a, region)] = cmp[(D1, a, region)] + cmp[(D2, a, region)]
cmp = fix_multilevel(cmp)

a = cmp[T][sorted(cmp[T].columns)].cumsum()

share_vaccine_young = a[Y] / (a[O] + a[Y])
t = "Share of vaccines going to young (<55)"
share_vaccine_young.loc["2021-01-15":].plot(title=t)

# %%
for region in ["Vorarlberg"]:
    v = df[region]
    v_total = v[D1] + v[D2]
    # v_total["Sum"] = v_total.sum(axis=1)
    v_rel1 = v[D1] / pt[region].loc[0]
    v_rel2 = v[D2] / pt[region].loc[0]
    v_rel = v_total / pt[region].loc[0]
    v_rel1.cumsum().plot(title=region)
    v_rel2.cumsum().plot(title=region)
# %%
def calc_daily_stuff(df, pt):
    display(df)


region = "Vorarlberg"
calc_daily_stuff(df[region], pt[region])
# %%
