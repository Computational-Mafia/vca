# %% [markdown]
# # Final Position on Wagon
# Our initial analysis will focus on characterizing variation in the position of players on final wagons as a function of factors like their slot's faction, the current game phase, the number of players required to secure an elimination, etc. Here we hope to demo the main visual constructs that will be featured in other initial analyses.

# %%
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# load votes dataframe
votes_df = pd.read_json('data/votes.json')
votes_df['null'] = 'Data'
null_df = pd.read_pickle('data/null_hypothesis.pkl')
null_df['null'] = 'Null Hypothesis'

# %% [markdown]
# ## Initial Formatting
# We'll pick a subset of the data (terminal votes on elminated players) and create some useful indicator variables.

# %%
combined = pd.concat([votes_df, null_df], ignore_index=True)
combined = combined.loc[(combined.terminal > -1) & (combined.target_eliminated==True)]
combined = combined.loc[combined.voter_faction != 'OTHER']
combined = combined.loc[combined.voted_faction != 'OTHER']
combined['votes_to_lim'] = np.floor((combined['total_living'].values/2)+1).astype(np.int64)
combined['rem_progression'] = combined['votes_to_lim'] - combined['position']
combined['prop_progression'] = np.digitize(combined['position']/combined['votes_to_lim'], np.arange(.1, 1.1, .1))
combined['termrem_progression'] = combined['votes_to_lim'] - combined['terminal']
combined['termprop_progression'] = np.digitize(combined['terminal']/combined['votes_to_lim'], np.arange(.1, 1.1, .1))
combined['voted_mafia'] = combined.voted_faction == 'MAFIA'
combined['voter_mafia'] = combined.voter_faction == 'MAFIA'

# %% [markdown]
# ## General Plotting Function
# For all these plots, we will plot the null hypothesis with a grey line and error bars reflecting the 2.5% and 97.5% percentiles of our data. A red line will reflect the values in our actual dataset.

# %%

def true_vs_null_hypothesis(data, positional_xticks=False, **kwargs):

    # plotting the true data
    ax = plt.gca()
    sns.pointplot(data=data.loc[data.null != 'Null Hypothesis'], **kwargs)

    # compute error bars the null data
    null_subset = data.loc[data.null == 'Null Hypothesis']
    sampling_distribution = pd.pivot_table(null_subset, index='iteration', 
        columns=kwargs['x'], values=kwargs['y'])
    means = pd.pivot_table(null_subset, index=iv, values=dv).values.flatten()
    upper_error = sampling_distribution.quantile(.80).values
    lower_error = sampling_distribution.quantile(.20).values
    error = np.asarray(
        [[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(
            len(upper_error))]).T
    
    # plotting the null hypothesis
    ax.errorbar(np.arange(len(pd.unique(data[iv]))), means, error, color='gray', label='Null hypothesis')

    # adjusting xticklabels for positional analysis if specified
    ax.tick_params(labelbottom=True)
    if positional_xticks:
        xticklabels = []
        for i in sorted(pd.unique(data[iv])):
            xticklabels.append('E-{}'.format(i))
        
        ax.set_xticks(np.arange(len(pd.unique(data[iv]))))
        ax.set_xticklabels(xticklabels)

# %% [markdown]
# ## Do mafia disproportionately end phases on hammered wagons?
# Here we just track the proportion of MAFIA who show up on the wagon in the first place, faceting by the alignment of the voted player.

# %% [markdown]
# ### Overall by Phase (Including and Excluding Last Phase)

# %%

iv = 'phase'
dv = 'voter_mafia'

for just_last_phase in [False]:
    subset = combined.loc[(combined.last_phase==just_last_phase) & (combined.phase < 6)]

    sns.set_theme(style="darkgrid")
    g = sns.FacetGrid(subset, height=5)
    g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, ci=False, color='red', dashes=False)
    g.set_axis_labels("Day", "Proportion of Mafia on Hammered Wagon")
    g.set_titles(col_template="...When Eliminated Slot is {col_name}")
    g.add_legend()
    g.fig.subplots_adjust(top=.9)
    if not just_last_phase:
        g.fig.suptitle("Overall (Days 1-5, Excluding Game-Ending Phases)")

# %% [markdown]
# ### By Faction and Phase (Including and Excluding Last Phase)

# %%

iv = 'phase'
dv = 'voter_mafia'

for just_last_phase in [False, True]:
    subset = combined.loc[(combined.last_phase==just_last_phase) & (combined.phase < 6)]

    sns.set_theme(style="darkgrid")
    g = sns.FacetGrid(subset, height=5, col='voted_faction')
    g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, ci=False, color='red', dashes=False)
    g.set_axis_labels("Day", "Proportion of Mafia on Hammered Wagon")
    g.set_titles(col_template="...When Eliminated Slot is {col_name}")
    g.add_legend()
    g.fig.subplots_adjust(top=.85)
    if just_last_phase:
        g.fig.suptitle("Days 1-5, Focusing on Final Day of Each Game")

# %% [markdown]
# ## Do mafia disproportionately positition at particular points on hammered wagons?

# %% [markdown]
# ### termrem_progression, overall

# %%
iv = 'rem_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase < 6) ]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=True, ci=False, color='red', dashes=False)
g.set_axis_labels("Proximity of Vote Position to Hammer", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1-5, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### termrem_progression, D1-2

# %%
iv = 'rem_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase < 3) ]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=True, ci=False, color='red', dashes=False)
g.set_axis_labels("Proximity of Vote Position to Hammer", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1 & 2, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### termrem_progression, D 3-5

# %%
iv = 'rem_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase > 2) & (combined.phase < 6)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=True, ci=False, color='red', dashes=False)
g.set_axis_labels("Proximity of Vote Position to Hammer", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 3 & 4 & 5, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### entry position, D < 6

# %%
iv = 'position'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase < 6)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Entry Position to Hammered Wagon", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1-5, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### entry position, D 3, 4, 5

# %%
iv = 'position'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase > 2) & (combined.phase < 6)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Entry Position to Hammered Wagon", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 3-5, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### entry position, D 1, 2

# %%
iv = 'position'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase <3)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Entry Position to Hammered Wagon", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1-2, Excluding Game-Ending Phases")
g.add_legend()


# %% [markdown]
# ### percent progression, overall

# %%
iv = 'prop_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase < 6)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Positional Bin", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1-5, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### percent progression, Days 1-2

# %%
iv = 'prop_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase < 3)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Positional Bin", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 1 & 2, Excluding Game-Ending Phases")
g.add_legend()

# %% [markdown]
# ### percent progression, Days 3-5

# %%
iv = 'prop_progression'
dv = 'voter_mafia'
subset = combined.loc[(combined.last_phase==False) & (combined.phase > 2) & (combined.phase < 6)]

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')
g.map_dataframe(true_vs_null_hypothesis, x=iv, y=dv, positional_xticks=False, ci=False, color='red', dashes=False)
g.set_axis_labels("Positional Bin", "Proportion of Voters Who Are Mafia")
g.set_titles(col_template="...When Eliminated Slot is {col_name}")
g.fig.subplots_adjust(top=.85)
g.fig.suptitle("Days 3 & 4 & 5, Excluding Game-Ending Phases")
g.add_legend()

# %%
