# %% [markdown]
# # Are We Sure The Null Hypothesis is Properly Specified?
# Let's do some basic tests of our assumptions about how the null hypothesis specification works:
# 1. That the probability of any given vote being by mafia or on mafia is the same as proportion of mafia slots relevant to the current phase.
# 2. That the probability of mafia appearing on any given position on a wagon is the same as proportion of mafia slots relevant to the current phase.
# 3. That this probability is only distorted in reasonable ways when faceted by voted faction's alliance.

# %%
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# load votes dataframe
votes_df = pd.read_json('data/votes.json')
null_df = pd.read_pickle('data/null_hypothesis.pkl')

# %% [markdown]
# ## Initial Formatting
# We'll pick a subset of the data (terminal votes on elminated players) and create some useful indicator variables.

# %%
df = votes_df.loc[(votes_df.terminal > -1) & (votes_df.target_eliminated==True)]
df = df.loc[df.voter_faction != 'OTHER']
df = df.loc[df.voted_faction != 'OTHER']
df['votes_to_lim'] = np.floor((df['total_living'].values/2)+1).astype(np.int64)
df['terminal'] = max(df.terminal.values) - df['terminal']
df['position'] = max(df.position.values) - df['position']
df['voted_mafia'] = df.voted_faction == 'MAFIA'
df['voter_mafia'] = df.voter_faction == 'MAFIA'
df['null'] = 'Data'

null = null_df.loc[(null_df.terminal > -1) & (null_df.target_eliminated==True)]
null = null.loc[null.voter_faction != 'OTHER']
null = null.loc[null.voted_faction != 'OTHER']
null['votes_to_lim'] = np.floor((null['total_living'].values/2)+1).astype(np.int64)
null['terminal'] = max(null.terminal.values) - null['terminal']
null['position'] = max(null.position.values) - null['position']
null['voted_mafia'] = null.voted_faction == 'MAFIA'
null['voter_mafia'] = null.voter_faction == 'MAFIA'
null['null'] = 'Null Hypothesis'

combined = pd.concat([df, null], ignore_index=True)

# %% [markdown]
# ## Are Voter and Voted Likelihoods Static Across Votes?
# If the null hypothesis is properly specified, then the probability of any given vote being should just be the proportion of TOWN slots around in the phase. We'll pick a single post, measure the rate across all iterations within null_df that the post's voter and voted are labeled MAFIA, and compare that with actual rates.
#
# In Mini Normal 1091 (thread 15787), 3 players are mafia and 9 are town. By Day 2, three town are eliminated, so the ratio is 3 to 6. Our null is good if post #14 is labeled MAFIA about 25% of the time, and post #617 is labeled MAFIA about 33%.

# %%

for post in [460, 943]:
    single = null_df.loc[(null_df.thread==15787) & (null_df.post==post)]
    print(post)
    print(np.mean(single.voter_faction=='MAFIA'))
    print(np.mean(single.voted_faction=='MAFIA'))
    print()

# %% [markdown]
# ## That the probability of mafia appearing on any given position on a wagon is on average the same as proportion of mafia slots relevant to the current phase.
# Let's go a bit further and plot for a specific phase in a specific game the ratio of mafia in each voting position.

# %%

proportions = [3/12, 3/9, 2/7, 2/6, 1/4]

for phase, proportion in enumerate(proportions):
    subset = null.loc[(null.phase==phase+1) & (null['thread'] == 15787)]
    sns.catplot(data=subset, x='terminal', y='voter_mafia', ci=False, kind='point')
    plt.axhline(y=proportion, color='red')
    plt.title(str(phase+1))
    plt.show()

# %% [markdown]
# ## That this probability is only distorted in reasonable ways when faceted by voted faction's alliance.

# %%
proportions = [3/12, 3/9, 2/7, 2/6, 1/4]
alt_proportions = [2/12, 2/9, 1/7, 1/6, 0/4]

for phase, proportion in enumerate(proportions):
    subset = null.loc[(null.phase==phase+1) & (null['thread'] == 15787)]
    sns.catplot(data=subset, x='terminal', y='voter_mafia', kind='point', hue='voted_mafia')
    plt.axhline(y=proportion, color='red')
    plt.axhline(y=alt_proportions[phase], color='yellow')
    plt.title(str(phase+1))
    plt.show()
# %%
