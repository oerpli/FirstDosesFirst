import pandas as pd

from data_loading import D0, D1, D2


#%% Calculate alternative dose-distribution
# The strategy is similar to the one proposed here: https://www.bmj.com/content/372/bmj.n710/rr
# The basic idea is this: The first dose is 89% effective, the 2nd dose 95%
# COVID risks scales with age, roughly exponentially (mod preexisting conditions), therefore the best method is
# to give a vaccination to someone that is from a group that benefits most from it
# 95 - 89 = 6, i.e. 2nd dose is roughly 15x less effective
# if X has a 15x higher risk of dying from COVID than Y, it's better to give X a second dose vs Y a first dose.
def redistribute_doses(
    df, pop, *, distr_first=False, priority=None, fractional_dosing=False
) -> pd.DataFrame:
    """Distribute doses according to priority, s.t. lives saved is maximized.
    Total number of vaccinations for each day does not change (as it is assumed that this is limited by capacity/supply).

    Args:
    - df pd.DataFrame: Dataframe with index = Date and columns with number of vaccinations per day and age group.
        An example column would have the "Name" `(D1, "25-34")`. Age groups from 25-34 to 75-84 and then 85-99.
        D1 is the string "1D", for second doses D2 == "2D" must be used.
    - pop: Population of each age group from previous DataFrame.
    - distr_first: Also distribute first doses. This is likely a bad idea as at least some of the first
        doses for younger people were given to at-risk groups.
    - priority: List of columns from `df` in priority order (which group should be vaccinated first).
        Sort from low priority to high priority

    Returns:
        pd.DataFrame: Returns a DF with the same dimensions and columns as `df` but with vaccines
        redistributed for higher life-saving-potential
    """
    have_d = df.iloc[0].copy() * 0  # Have 1 or 2 doses (init with 0)

    # This ordering should optimize lives saved according to relative risk of each age group
    # releasec by the CDC
    # https://www.cdc.gov/coronavirus/2019-ncov/images/need-extra-precautions/319360-A_COVID-19_RiskForSevereDisease_Race_Age_2.18_p1.jpg
    priorities = priority or [
        (D2, "25-34"),
        (D2, "35-44"),
        (D2, "55-64"),
        (D1, "25-34"),
        (D2, "45-54"),
        (D1, "35-44"),
        (D2, "65-74"),
        (D1, "45-54"),
        (D2, "75-84"),
        (D1, "55-64"),
        (D1, "65-74"),
        (D2, "85-99"),
        (D1, "75-84"),
        (D1, "85-99"),
    ]

    fractional_doses = {
        "25-34": 0.25,
        "35-44": 0.25,
        "45-54": 0.25,
        "55-64": 0.5,
        "65-74": 0.75,
        "75-84": 1,
        "85-99": 1,
    }

    def get_remainder_d(d, group, vacc):
        # how many stay in group, how many can go to other groups (according to priority)
        unvacc = pop[group] - have_d[(d, group)]

        missing = min(vacc, unvacc)  # this many still need their d-th shot
        # this is overflow, give to (next) highest priority group
        remainder = vacc - missing
        if fractional_dosing:
            overflow = missing * (1 - fractional_doses[group])
            overflow = int(overflow)
            remainder += overflow
        return missing, remainder

    def assign_d(d, group, vacc, row):
        # update data structures with vacc new d-th dose vaccines for age group
        have_d[(d, group)] += vacc  # dose/group lvl vacc counter

        if have_d[(d, group)] >= pop[group]:
            # print(f"Finished {d} for {grp}")
            priorities.remove((d, group))
        row[(d, group)] += vacc  # modify result
        return row

    rows = []
    for date, row in df.iterrows():
        row_new = row.copy() * 0  # modifying rows would change original DF
        for (d, grp), vacc in row.items():
            # Redistribute D2 always, first only if desired
            if d == D2 or distr_first:
                d, grp = priorities[-1]  # get next group that may need something
            while vacc > 0:
                m, vacc = get_remainder_d(d, grp, vacc)  # distribute
                if m > 0:
                    row_new = assign_d(d, grp, m, row_new)  # assign
                d, grp = priorities[-1]  # get next group that may need something
        # finished updating row, save to list
        rows.append(row_new)
    return pd.DataFrame(rows, index=df.index)


# %%
