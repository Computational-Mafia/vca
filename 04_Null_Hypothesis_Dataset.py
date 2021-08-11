# %% [markdown]
# # Null Hypothesis
# To help keep track across our analyses of the null hypothesis that there are not factional differences in how people vote, we'll generate a `data/votes_null_hypothesis` that contains 1000 iterations of shuffling within-phase the identities of voters but otherwise preserving their sequences of votes. Derived analyses we might apply to the normal dataset should be just as applicable to the current dataset.

# %%
import pandas as pd
from tqdm.notebook import trange
from helpers.relevantGameInfo import relevantGameInfo
from helpers.VoteCount import VoteCount
from datetime import datetime
import json
import random

# %%
# load votes dataframe
votes_df = pd.read_json('data/votes.json')
votes_df['iteration'] = 0
columns = votes_df.columns.to_list()

# range of game days to consider; leave 0 for no limit
end_day = 0
iteration_total = 1000

# %%

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')

null_df = []

# loop through archived games
for game_index in trange(len(games), desc='game loop'):

    game = games[game_index]

    # extract relevant information about this game
    slots, players, fates, lynched, factions, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(
        game, include_factions=True)
    
    for day in range(1, end_day if end_day else len(game_transitions)):

        # considered games should have at least 1 full phase cycle
        if len(game_transitions) < day+1:
            continue

        relevant_slots = [slot for slot_index, slot in enumerate(slots) if fates[slot_index] >= day]
        relevant_players = []
        for slot in relevant_slots:
            relevant_players += slot

        shuffling = list(range((len(relevant_slots))))
        phase_df = votes_df.loc[(
            votes_df.phase==int(day)) & (votes_df.thread==int(number))].to_numpy()
        voter = phase_df[:, columns.index('voter')].copy()
        voted = phase_df[:, columns.index('voted')].copy()

        for iteration in trange(iteration_total, desc='iteration_loop', leave=False):
            
            # collector for our votes in this phase and iteration
            random.shuffle(shuffling)
            phase_df[:, columns.index('iteration')] = iteration
            
            # voter, voted, voter_faction, and voted_faction 
            # must all be reassigned based shuffle
            for slot_index, slot in enumerate(relevant_slots):
                for player in slot:
                    new_slot = relevant_slots[shuffling[slot_index]][0]
                    phase_df[voter==player, columns.index('voter')] = new_slot
                    phase_df[voter==player, columns.index('voter_faction')] = factions[str(
                        relevant_slots[shuffling[slot_index]])]
                    phase_df[voted==player, columns.index('voted')] = new_slot
                    phase_df[voted==player, columns.index('voted_faction')] = factions[str(
                        relevant_slots[shuffling[slot_index]])]

            null_df.append(pd.DataFrame(phase_df, columns=columns))

# %%

results_df = pd.concat(null_df, ignore_index=True)
results_df.to_pickle('data/null_hypothesis.pkl')

# %%
#results_df.to_json('data/null_hypothesis.json')
#now = datetime.now()