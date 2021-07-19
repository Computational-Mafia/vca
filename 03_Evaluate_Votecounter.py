# %% [markdown]
# # Evaluate Votecounter
# A script for characterizing the performance of a votecounter.

# %% [markdown]
# ## Select Your Votecounter
# Modify the cell below to import the wrapper class for your VoteCounter and assign it to the variable `VoteCounter` before executing the notebook. Also identify the location of your corresponding `votes_df`. When you run the notebook, your votecounter will be evaluated and various troubleshooting messages and summary statistics displayed characterizing its performance. 

# %%
from LevenshteinCounter import LevenshteinExtracter as VoteCounter
import pandas as pd

votes_df = pd.read_json('data/votes_VoteExtracter_18_07_2021_0.json')

votes_df.head()

# %% [markdown]
# ## Other Dependencies

# %%

from IPython.core.display import display, HTML
import markdown2 as md
import seaborn as sns
import matplotlib.pyplot as plt

def html(markdown_string):
    display(HTML(md.markdown(markdown_string)))

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

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
sns.lineplot(x='uncertainty', y='lynch_predicted', data=phase_successes, label='lynch')
sns.lineplot(x='uncertainty', y='transition_predicted', data=phase_successes, label='transition')
plt.ylabel('Prediction Accuracy')
plt.xlabel('Vote Uncertainty')
plt.legend()
plt.show()

# %% [markdown]
# ## Single Game Troubleshooting
# Pick a game_index, day, and post number to simulate and display:
# - Predicted Votecount Up to Indicated Post Number
# - Predicted Final Votecount for this Day
# - Recorded Log of Votes Up to Final Votecount

# %%
game_index = 0
day = 1
postnumber = 17

# %%
postnumber = str(postnumber)
print('Game Index:', game_index)
print('Day', day)
    
# extract relevant information about this game
game = games[game_index]
slots, players, fates, lynched, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(game)

# also load posts for this game
with open('data/posts/{}.jsonl'.format(number)) as f:
    gameposts =  [json.loads(l) for l in f]

# find and display selected post
html('# Post {}'.format(postnumber))
post = next(item for item in gameposts if item["number"] == postnumber)
print()
print(post)
print()
display(HTML(post['content']))