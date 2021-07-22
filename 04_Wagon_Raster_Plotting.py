# %% [markdown]
# # Wagon Raster Plotting
# Here we want to demo a potential way to streamline visualization of many game wagons: a raster plot of a subset of wagons hued based on the faction of the person making the vote. With that foundation we might be set up to work on more complex visualizations (e.g. tracking changes in wagon sizes across a phase) or to perform contrastive statistical tests.

# %% [markdown]
# ## Setup
# For each D1 the votecounter successfully predicts w/o help (and a lynch has happened), simulate votecounter until a hammer is detected. match each vote to a faction. The sequence is what we want in our DF. The raster plot is effectively a scatter plot tracking 3 variables. I need in my df for each vote a wagon index, a position on wagon, and a faction. Since the number of votes required to achieve a lynch can vary, I may be interested in aligning position indices such that hammer votes all have the same x-position rather than such that initial votes all have the same x-position.

# %%

import markdown2 as md
import seaborn as sns
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime
from helpers.VoteCount import VoteCount
from helpers.relevantGameInfo import relevantGameInfo
from VoteCounter import VoteExtracter as VoteCounter
import pandas as pd
from tqdm.notebook import trange

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# load votes dataframe
votes_df = pd.read_json('data/votes_VoteExtracter_21_07_2021.json')

# track prediction success rates for each game; we'll want 1 for both lynch and transition
prediction_rates = pd.pivot_table(data=votes_df, index=['thread'], values=['lynch_predicted', 'transition_predicted']).reset_index()

# range of game days to consider; leave 0 for no limit
end_day = 2

# %%

results = []
wagon_index = 0

# loop through archived games
for game_index in trange(len(games), desc='game loop'):

    game = games[game_index]

    # extract relevant information about this game
    slots, players, fates, lynched, factions, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(
        game, include_factions=True)

    # ditch game if lynch and transition prediction rate below 1
    game_prediction_rates = prediction_rates.loc[prediction_rates.thread==int(number)]
    if np.any(game_prediction_rates.to_numpy().flatten()[1:] < 1):
        continue

    # also load posts for this game
    with open('data/posts/{}.jsonl'.format(number)) as f:
        gameposts =  [json.loads(l) for l in f]

    for day in range(1, end_day if end_day else len(game_transitions)):

        # considered games should have at least 1 full phase cycle
        if len(game_transitions) < day+1:
            continue

        # configure extra day-specific information
        ## what makes a correct phase prediction?
        canPredictTransition, canPredictLynch = True, True
        if f'd{day} long twilight' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            canPredictTransition = False
        if f'd{day} hammer after deadline' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            canPredictLynch = False
        if f'd{day} no majority' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            correct = None
            canPredictTransition = False
        elif f'd{day} no lynch' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            correct = 'NO LYNCH'
        else:
            correct = lynched[day] if day in lynched else None

        # ignore phases that end in NO LYNCH or cannot be predicted
        if (not canPredictTransition) or (
            not canPredictLynch) or (correct == 'NO LYNCH') or (correct == None):
            continue

        ## initialize for phase-specific posts, players, slots, votecount, votecounter
        start_point = 0 if day == 1 else int(game_transitions[day-2])
        end_point = int(game_transitions[day-1])+1 if not correct else len(gameposts)
        relevant_slots = [slot for slot_index, slot in enumerate(slots) if fates[slot_index] >= day]
        relevant_players = []
        for slot in relevant_slots:
            relevant_players += slot
        votecount = VoteCount(
            relevant_slots, meta={'correct': correct}, 
            lessOneForMislynch=lessOneForMislynch, doublevoters=doublevoters)
        phase_df = votes_df.loc[(votes_df.phase==int(day)) & (votes_df.thread==int(number))]

        # scan through this game's posts
        for post_index in range(start_point, end_point):#, desc='post loop', leave=False):
            post = gameposts[post_index]

            # first process special events tracked in game notes (e.g. day kills, votecount resets, missed votes)
            if post['number'] in events:
                post_events = events[post['number']]
                for event in post_events:

                    # if event is a daykill, remove the player from votecount and votecounter
                    if 'killed' == event.split(' ')[-1]:

                        # update relevant slots and players and make new votecounter
                        killed_player = event[:event.rfind(' ')]
                        killed_slot = next(
                            s for s in relevant_slots if s.count(killed_player) > 0)
                        del relevant_slots[relevant_slots.index(killed_slot)]
                        relevant_players = []
                        for slot in relevant_slots:
                            relevant_players += slot
                        votecount.killplayer(killed_player, post['number'])

            # consider votes until voters have made a choice already
            elif not votecount.choice:

                # ignore posts not made by players
                if relevant_players.count(post['user']) == 0:
                    continue

                # update votecount for each vote found by votecounter
                # stop considering votes in post if votecount.choice
                for index, row in phase_df.loc[phase_df.post==int(post['number'])].iterrows():
                    votecount.update(row['voter'], row['voted'], row['post'])
                    if votecount.choice:
                        break
            
            # finish if votecount.choice
            else:
                
                # track for each vote a wagon index, wagon position, faction
                # build list of slots on final wagon
                final_votes = votecount.todict()[str(correct)]
                
                # track faction of voted slot
                voted_faction = factions[str(correct)]

                # track faction of each voting slot
                for position, vote in enumerate(final_votes):
                    results.append(
                        [int(number), day, wagon_index, position, 
                        voted_faction, factions[str(vote)]]
                        )

                wagon_index += 1
                break

results_df = pd.DataFrame(results, columns=['thread', 'phase', 'wagon', 'position', 'voted_faction', 'voter_faction'])

now = datetime.now()
results_df.to_json('data/final_wagon_by_faction_{}.json'.format(VoteCounter.__name__))

# %%

# load votes dataframe
df = pd.read_json('data/final_wagon_by_faction_VoteExtracter.json')
df = df.loc[(df.phase == 1)]
df.head()

# %%

length = 10
n_item = int(df['position'].max())
n_list = int(df['wagon'].max())
list_lim = (0, n_list + 1)
item_lim = (0, n_item + 1)
x_var, y_var = 'wagon', 'position'
x_lim, y_lim = list_lim, item_lim
x_label, y_label = 'Wagon', 'Vote Position'
def_aspect = n_list / n_item
height = length / def_aspect

g = sns.FacetGrid(
        data=df, dropna=False, height=8, col='voted_faction')
g.map_dataframe(
        sns.scatterplot,
        x=y_var,
        y=x_var,
        marker='s',
        hue='voter_faction',
        legend='auto',
    )

#g.set_xlabels(x_label)
#g.set_ylabels(y_label)
#g.set(xlim=x_lim, ylim=y_lim)

# %%
