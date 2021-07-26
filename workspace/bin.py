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

# %%
