# %% [markdown]
# # Final Position on Wagon
# Our initial analysis will focus on characterizing variation in the position of players on final wagons as a function of factors like their slot's faction, the current game phase, the number of players required to secure an elimination, etc. Here we hope to demo the main visual constructs that will be featured in other initial analyses.

# %%

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
votes_df = pd.read_json('data/votes.json')
null_df = pd.read_json('data/null_hypothesis.json')

# track prediction success rates for each game; we'll want 1 for both lynch and transition
prediction_rates = pd.pivot_table(
    data=votes_df, index=['thread'], values=['lynch_predicted', 'transition_predicted']).reset_index()

# range of game days to consider; leave 0 for no limit
end_day = 0

# %% [markdown]
# ## Data Selection

# %%

results = []
wagon_index = 0

# loop through archived games
for game_index in trange(len(games), desc='game loop'):

    game = games[game_index]

    # extract relevant information about this game
    slots, players, fates, lynched, factions, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(
        game, include_factions=True)

    # remove manually set vote modifying events if we want to exclude those
    for key in list(events.keys()):
        clean_entries = []
        for entry in events[key]:
            if ' voted ' not in entry:
                if 'did not vote ' not in entry:
                    clean_entries.append(entry)
        if clean_entries:
            events[key] = clean_entries.copy()
        else:
            del events[key]

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

                    # if event is a vote reset, set relevant player(s) to not voting
                    elif 'reset' == event.split(' ')[1]:
                        reset_players = ([s[0] for s in relevant_slots] 
                                        if event.split(' ')[0].lower() == 'votecount'
                                         else [event.split(' ')[0]])
                        for reset_player in reset_players:
                            votecount.update(reset_player, 'UNVOTE', post['number'])

                    # if event is a vote specification set relevant player(s) to vote
                    elif ' voted ' in event:-
                        votecount.update(event.split(' voted ')[0], event.split(' voted ')[1], post['number'])

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
                        [int(number), day, wagon_index, len(final_votes) - position - 1, len(final_votes), voted_faction, factions[str(vote)]]
                        )

                wagon_index += 1
                break

results_df = pd.DataFrame(
    results, columns=['thread', 'phase', 'wagon', 'position', 'votes_to_lim', 'voted_faction', 'voter_faction'])

now = datetime.now()
results_df.to_json('data/final_wagon_by_faction_{}.json'.format(VoteCounter.__name__))

# %% [markdown]
# ## Analysis-Specific DF Configuration

# load votes dataframe and derive relevant indicator variables
df = pd.read_json('data/final_wagon_by_faction_VoteExtracter.json')
df = df.loc[df.phase == 1]
df['position'] = max(df.position.values) - df['position']
df = df.loc[df.voter_faction != 'OTHER']
df = df.loc[df.voted_faction != 'OTHER']
df['voted_town'] = df.voted_faction == 'TOWN'
df['voter_town'] = df.voter_faction == 'TOWN'
df['voted_mafia'] = df.voted_faction == 'MAFIA'
df['voter_mafia'] = df.voter_faction == 'MAFIA'

# %% [markdown]
# ### Sample Size Plotting Demo

# %%
# initialize plot
g = sns.catplot(x="voter_faction", y="voted_town", data=df, kind='bar')

# build df to help label sample sizes
# we need for each x position the relevant y position and text value
size_df = pd.pivot_table(df, index='voter_faction', values='voted_mafia', aggfunc=[np.mean, np.size]).reset_index()
size_df.columns = size_df.columns.get_level_values(0)

# then we plot the text at each point (though i decided to just put N at bottom instead of at y)
for line in range(0,size_df.shape[0]):
    plt.text(np.where(pd.unique(df.voter_faction) == size_df.voter_faction[line])[0][0], 
    0.01, 'N={}'.format(size_df['size'][line]), horizontalalignment='center', size='large', color='black')

# %% 
