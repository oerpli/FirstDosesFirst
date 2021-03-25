#%%
from utility import *

#%%
O = "Old"
Y = "Young"
T = "Total"

df = get_eimpfpass_data()
#%%
# df["EingetrageneImpfungen"].plot()
cmp = pd.DataFrame()
for region in df.columns.levels[0]:
    x = df[region]
    for d in [D1, D2]:
        cmp[(d, O, region)] = x[d][[c for c in x[d].columns if c[0] >= "5"]].sum(axis=1)
        cmp[(d, Y, region)] = x[d][[c for c in x[d].columns if c[0] < "5"]].sum(axis=1)

    for a in [O, Y]:
        cmp[(T, a, region)] = cmp[(D1, a, region)] + cmp[(D2, a, region)]
cmp = fix_multilevel(cmp)

a = cmp[T][sorted(cmp[T].columns)].cumsum()

share_vaccine_young = a[Y] / (a[O] + a[Y])
t = "Share of vaccines going to young (<55)"
share_vaccine_young.loc["2021-01-15":].plot(title=t)
