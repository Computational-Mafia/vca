# %%
# df.loc[(df.phase < 4) & (df.votes_to_lim > 3)]
g = sns.FacetGrid(df.loc[(df.phase < 4)], col='voted_faction', row='phase', height=5)
#g.map_dataframe(sns.lineplot, 'position', 'voter_town', ci=False)
g.map_dataframe(sns.lineplot, 'position', 'voter_mafia', ci=False)
plt.subplots_adjust(hspace=0.2, wspace=0.1)

xticklabels = ['']
for i in reversed(pd.unique(df.position)):
    xticklabels.append('E-{}'.format(i))

for ax in g.axes.flatten():
        ax.tick_params(labelbottom=True)
        ax.set_xlabel('Position on Final Wagon (Last Vote First)', visible=True)
        ax.set_ylabel('Proportion of Voters Who Are Mafia')
        ax.set_xticklabels(xticklabels)
plt.show()

# %%

# load votes dataframe
df = pd.read_json('data/final_wagon_by_faction_VoteExtracter.json')
#df = df.loc[df.phase==1]
df['position'] = max(df.position.values) - df['position']
df = df.loc[df.voter_faction != 'OTHER']
df = df.loc[df.voted_faction != 'OTHER']
df['voted_town'] = df.voted_faction == 'TOWN'
df['voter_town'] = df.voter_faction == 'TOWN'
df['voted_mafia'] = df.voted_faction == 'MAFIA'
df['voter_mafia'] = df.voter_faction == 'MAFIA'
df = pd.pivot_table(df, index=['phase', 'voted_town', 'position'], values=['voter_town'], aggfunc=[np.size, np.mean, np.sum]).reset_index()
df.columns = df.columns.get_level_values(0)

# %% [markdown]
# ## Is eliminated player alignment indicative of voter alignment?

# %% [markdown]
# ### Between Phase

# %%

iv = 'terminal'
dv = 'voter_mafia'
col = 'phase'
col_limit = 5
subset = combined.loc[(combined[col] < col_limit)]

def errplot(data, x=iv, y=dv, **kwargs):

    ax = plt.gca()
    sns.lineplot(x=iv, y=dv, ax=ax, data=data.loc[data.null=='Data'], **kwargs)

    # update xticks to track E-X
    xticklabels = []
    for i in reversed(sorted(pd.unique(data[iv]))):
        xticklabels.append('E-{}'.format(i))
    xticklabels.append('E-0')

    ax.tick_params(labelbottom=True)
    ax.set_xticks(np.arange(len(pd.unique(data[iv]))+1))
    ax.set_xticklabels(xticklabels)

    # add error bars reflecting sampling distribution of the null
    sampling_distribution = pd.pivot_table(
        data.loc[data.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

    means = pd.pivot_table(data.loc[data.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
    upper_error = sampling_distribution.quantile(.8).values
    lower_error = sampling_distribution.quantile(.2).values
    error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T
    
    ax.errorbar(sorted(pd.unique(data[iv])), means, error, color='gray')

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col=col, row='voted_faction')

g.map_dataframe(errplot, x=iv, y=dv, ci=False, color='red', dashes=False)
plt.subplots_adjust(hspace=0.2, wspace=0.1)

for ax in g.axes.flatten():
    ax.tick_params(labelbottom=True)
    ax.set_xlabel('Position on Final Wagon (Last Vote First)', visible=True)
    ax.set_ylabel('P(voter_faction = MAFIA)')

plt.show()

# %% [markdown]
# ### Across Phase

# %%
subset = combined.loc[(combined.phase < 4)]
iv = 'position'
dv = 'voter_mafia'

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voted_faction')

g.map_dataframe(errplot, x=iv, y=dv, ci=False, color='red', dashes=False)
plt.subplots_adjust(hspace=0.2, wspace=0.1)

for ax in g.axes.flatten():
    ax.tick_params(labelbottom=True)
    ax.set_xlabel('Position on Final Wagon (Last Vote First)', visible=True)
    ax.set_ylabel('P(voter_faction = MAFIA)')

plt.show()

# %% [markdown]
# ## Is terminal position of scum on a wagon alignment indicative of the voted slot's faction?

# %% 
subset = combined.loc[(combined.phase < 4)]
iv = 'terminal'
dv = 'voted_mafia'

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='phase', row='voter_faction')

g.map_dataframe(errplot, x=iv, y=dv, ci=False, color='red', dashes=False)
plt.subplots_adjust(hspace=0.2, wspace=0.1)

for ax in g.axes.flatten():
    ax.tick_params(labelbottom=True)
    ax.set_xlabel('Position on Final Wagon (Last Vote First)', visible=True)
    ax.set_ylabel('P(voted_faction = MAFIA)')

# %% [markdown]
# ### Across Phase

# %%
subset = combined.loc[(combined.phase < 4)]
iv = 'position'
dv = 'voted_mafia'

sns.set_theme(style="darkgrid")
g = sns.FacetGrid(subset, height=5, col='voter_faction')

g.map_dataframe(errplot, x=iv, y=dv, ci=False, color='red', dashes=False)
plt.subplots_adjust(hspace=0.2, wspace=0.1)

for ax in g.axes.flatten():
    ax.tick_params(labelbottom=True)
    ax.set_xlabel('Position on Final Wagon (Last Vote First)', visible=True)
    ax.set_ylabel('P(voted_faction = MAFIA)')

plt.show()


# %% [markdown]
# ## Does mafia being on the wagon at all predict the faction of the eliminated player?
#
# ### Just First Three Phases

# %%
subset = combined.loc[(combined.phase < 4)]
iv = 'voter_faction'
dv = 'voted_mafia'
g = sns.catplot(x=iv, y=dv, data=subset.loc[subset.null!='Null Hypothesis'], kind='point', ci=False, order=['MAFIA', 'TOWN'], legend=False, join=True, color='red')

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

means = pd.pivot_table(subset.loc[subset.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
upper_error = sampling_distribution.quantile(.8).values
lower_error = sampling_distribution.quantile(.2).values
error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T

ax = plt.gca()
ax.errorbar(['MAFIA', 'TOWN'], means, error, color='gray', label='Null Hypothesis')
ax.set_ylabel('P(voted_faction = MAFIA)')
ax.set_xlabel('Voter Faction')
plt.legend()

# %% [markdown]
# ### All Phases

# %%

subset = combined
iv = 'voter_faction'
dv = 'voted_mafia'
g = sns.catplot(x=iv, y=dv, data=subset.loc[subset.null!='Null Hypothesis'], kind='point', ci=False, order=['MAFIA', 'TOWN'], legend=False, join=True, color='red')

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

means = pd.pivot_table(subset.loc[subset.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
upper_error = sampling_distribution.quantile(.8).values
lower_error = sampling_distribution.quantile(.2).values
error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T

ax = plt.gca()
ax.errorbar(['MAFIA', 'TOWN'], means, error, color='gray', label='Null Hypothesis')
ax.set_ylabel('P(voted_faction = MAFIA)')
ax.set_xlabel('Voter Faction')
plt.legend()

# %% [markdown]
# ### Faceted By Phase

subset = combined.loc[(combined.phase < 4)]
iv = 'voter_faction'
dv = 'voted_mafia'
g = sns.catplot(x=iv, y=dv, data=subset.loc[subset.null!='Null Hypothesis'], kind='point', ci=False, order=['MAFIA', 'TOWN'], legend=False, join=True, color='red', col='phase')

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

means = pd.pivot_table(subset.loc[subset.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
upper_error = sampling_distribution.quantile(.8).values
lower_error = sampling_distribution.quantile(.2).values
error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T

plt.show()
    
# %%


# %% [markdown]
# ### Overall, Days 1, 2, 3

subset = combined.loc[combined.phase < 4]
iv = 'voted_faction'
dv = 'voter_mafia'

sns.set_style('whitegrid')
g = sns.catplot(x=iv, y=dv, data=subset.loc[subset.null!='Null Hypothesis'], kind='point', ci=False, legend=False, 
                join=True, color='red', order=['MAFIA', 'TOWN'])

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

means = pd.pivot_table(subset.loc[subset.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
upper_error = sampling_distribution.quantile(.8).values
lower_error = sampling_distribution.quantile(.2).values
error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T

ax = plt.gca()
ax.errorbar(['MAFIA', 'TOWN'], means, error, color='gray', label='Null Hypothesis')
ax.set_ylabel('Proportion of Voters Who Were Mafia')
ax.set_xlabel('Faction of Slot Voted Out')
plt.title('Days 1, 2, 3')
plt.legend()
plt.savefig("results/Faction_of_Hammered_Slot_vs_Proportion_Mafia_D123.png")

# %% [markdown]
# ### Overall, Days 4+, Excluding Finals

subset = combined.loc[(combined.phase > 3) & (combined.last_phase == False)]
iv = 'voted_faction'
dv = 'voter_mafia'

sns.set_style('whitegrid')
g = sns.catplot(x=iv, y=dv, data=subset.loc[subset.null!='Null Hypothesis'], kind='point', ci=False, legend=False, 
                join=True, color='red', order=['MAFIA', 'TOWN'])

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

# add error bars reflecting sampling distribution of the null
sampling_distribution = pd.pivot_table(
    subset.loc[subset.null=='Null Hypothesis'], index=['iteration'], columns=iv, values=dv)

means = pd.pivot_table(subset.loc[subset.null=='Null Hypothesis'], index=iv, values=dv).values.flatten()
upper_error = sampling_distribution.quantile(.8).values
lower_error = sampling_distribution.quantile(.2).values
error = np.asarray([[means[i] - lower_error[i], upper_error[i] - means[i]] for i in range(len(upper_error))]).T

ax = plt.gca()
ax.errorbar(['MAFIA', 'TOWN'], means, error, color='gray', label='Null Hypothesis')
ax.set_ylabel('Proportion of Voters Who Were Mafia')
ax.set_xlabel('Faction of Slot Voted Out')
plt.title('Days 4+, Excluding Final Phases')
plt.legend()
plt.savefig("results/Faction_of_Hammered_Slot_vs_Proportion_Mafia_D123.png")
