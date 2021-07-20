# %% [markdown]
# ## General Analyses

# %% [markdown]
# ### Success Rates

# %% [markdown]
# #### Overall
# Hopefully these are high!

# %%
phase_successes = pd.pivot_table(votes_df, index=['thread','phase'], values=['lynch_predicted', 'transition_predicted'])

phase_successes.mean()

# %% [markdown]
# #### By Phase
# Since there are fewer voters and votes in the later phases, I suspect accuracy would increase.

# %%
phase_successes = pd.pivot_table(votes_df, index=['phase'], values=['lynch_predicted', 'transition_predicted']).reset_index()
sns.lineplot(x='phase', y='lynch_predicted', data=phase_successes, label='lynch')
sns.lineplot(x='phase', y='transition_predicted', data=phase_successes, label='transition')
plt.ylabel('Prediction Accuracy')
plt.xlabel('Game Phase')
plt.legend()
plt.show()

# %% [markdown]
# It's not at all that consistent but the general trend is there.

# %% [markdown]
# #### Any Problem Users?
# I wonder how we characterize this. For each voter or voted username, we can aggregate a mean success rate and identify the most troublesome. But I don't know what I'd do with that information

# %% [markdown]
# #### By Processing Depth
# Is outcome prediction accuracy related to how much the votecounter "struggles" to find a matching vote? Probably not since only a few votes are decisive. Would need to focus on wagons that get hammered.

# %%
phase_successes = pd.pivot_table(votes_df, index=['uncertainty'], values=['lynch_predicted', 'transition_predicted']).reset_index()

plt.figure(figsize=(15,8))
sns.set_style('whitegrid')

sns.lineplot(x='uncertainty', y='lynch_predicted', data=phase_successes, label='lynch')
#sns.lineplot(x='uncertainty', y='transition_predicted', data=phase_successes, label='transition')
plt.ylabel('Prediction Accuracy')
plt.xlabel('Vote Processing Depth')
plt.xlim([0, 50])
plt.xticks(np.arange(0, 50))
plt.legend()
sns.despine()
plt.show()

# %% [markdown]
# These results suggest that my step 14 -- where I check if vote is a two letter abbreviation of a playername that includes partial english -- precipitates a massive drop in matching accuracy. But I'm not sure how much that actually affects output since I don't have frequencies yet. How do I count those? I want to plot a proportion for each depth, binning everyting above 40. 

# %%

sns.ecdfplot(data=votes_df.loc[votes_df.lynch_predicted== True], x='uncertainty', label='Accurate Predictions')
sns.ecdfplot(data=votes_df.loc[votes_df.lynch_predicted== False], x='uncertainty', label='Inaccurate Predictions')
plt.xlabel('processing depth')
plt.ylabel('proportion of votes labeled at this depth')
plt.xticks(np.arange(30))
plt.xlim([0, 30])
plt.yticks(np.arange(1.05, step=.05))
plt.legend()

# %% [markdown]
# ### Processing Depth