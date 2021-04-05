
#%%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from dose_redistributing_methods import redistribute_doses
from data_loading import *
from utility import OUT_FOLDER, fix_multilevel, write_img_to_file, write_to_file

from pathlib import Path


# Some global stuff

O = "Old"
Y = "Young"
T = "Total"

plt.rcParams["figure.figsize"] = [10, 5]
sns.set_theme()
#

PLOT_FOLDER = Path("Y:/GitRepos/oerpli.github.io/fdf")
region = "Vorarlberg"
short = "vlbg"
vlbg_img = OUT_FOLDER / "img" / short
vlbg_report = OUT_FOLDER / "CaseStudyVlbg.md"
pt = pd.DataFrame(population.unstack()).T


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


# region = "Österreich"
# df = df_full[region]
# pop = pt[region].loc[0]
# dfv = df[[D1, D2]]