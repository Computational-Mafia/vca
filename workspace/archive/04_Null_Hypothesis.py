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

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# load votes dataframe
votes_df = pd.read_json('data/votes.json')
alt_votes_df = []

# range of game days to consider; leave 0 for no limit
end_day = 0
iteration_total = 3




# %%

def profile_this():
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

        # also load posts for this game
        with open('data/posts/{}.jsonl'.format(number)) as f:
            gameposts =  [json.loads(l) for l in f]

        for iteration in trange(iteration_total, desc='iteration_loop', leave=False):
            for day in range(1, end_day if end_day else len(game_transitions)):

                # considered games should have at least 1 full phase cycle
                if len(game_transitions) < day+1:
                    continue

                # configure extra day-specific information
                ## what makes a correct phase prediction?
                if 'd{day} no lynch' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
                    correct = 'NO LYNCH'
                else:
                    correct = lynched[day] if day in lynched else None

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
                lynch_predicted = phase_df['lynch_predicted'].values[0]
                transition_predicted = phase_df['transition_predicted'].values[0]

                # collector for our votes in this phase and iteration
                shuffling = list(range((len(relevant_slots))))
                random.shuffle(shuffling)
                alt_phase_df = []

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

                                slot_index = relevant_slots.index(killed_slot)
                                del relevant_slots[slot_index]
                                relevant_players = []
                                for slot in relevant_slots:
                                    relevant_players += slot

                                # update shuffling vector too
                                shuffled_index = shuffling[slot_index]
                                del shuffling[slot_index]
                                for i in range(len(shuffling)):
                                    if shuffling[i] > shuffled_index:
                                        shuffling[i] -= 1
                                    
                                votecount.killplayer(killed_player, post['number'])

                            # if event is a vote reset, set relevant player(s) to not voting
                            elif 'reset' == event.split(' ')[1]:
                                reset_players = ([s[0] for s in relevant_slots] 
                                                if event.split(' ')[0].lower() == 'votecount'
                                                else [event.split(' ')[0]])
                                for reset_player in reset_players:
                                    votecount.update(reset_player, 'UNVOTE', post['number'])

                                    # configure df based on shuffling
                                    slot_index = next(relevant_slots.index(s) for s in relevant_slots
                                                    if s.count(reset_player) > 0)
                                    reset_player = relevant_slots[shuffling[slot_index]][0]

                                    alt_phase_df.append(
                                        [reset_player, 'UNVOTE', post['number'], day, int(number)*iteration_total+iteration, False, 0.0, lynch_predicted, transition_predicted])

                            # if event is a vote specification set relevant player(s) to vote
                            elif ' voted ' in event:
                                votecount.update(event.split(' voted ')[0], event.split(' voted ')[1], post['number'])

                                # configure df based on shuffling
                                p1 = event.split(' voted ')[0]
                                p2 = event.split(' voted ')[1]
                                p1_slot_index = next(relevant_slots.index(s) for s in relevant_slots
                                                if s.count(p1) > 0)
                                p2_slot_index = next(relevant_slots.index(s) for s in relevant_slots
                                                if s.count(p2) > 0)
                                p1 = relevant_slots[shuffling[p1_slot_index]][0]
                                p2 = relevant_slots[shuffling[p2_slot_index]][0]

                                alt_phase_df.append(
                                    [p1, p2, post['number'], day, int(number)*iteration_total+iteration, 
                                    True, 0.0, lynch_predicted, transition_predicted])

                    # consider votes until voters have made a choice already
                    elif not votecount.choice:

                        # ignore posts not made by players
                        if relevant_players.count(post['user']) == 0:
                            continue

                        # update votecount for each vote found by votecounter
                        # stop considering votes in post if votecount.choice
                        for index, row in phase_df.loc[phase_df.post==int(post['number'])].iterrows():
                            votecount.update(row['voter'], row['voted'], row['post'])

                            # configure df based on shuffling
                            p1 = row['voter']
                            p2 = row['voted']
                            p1_slot_index = next(relevant_slots.index(s) for s in relevant_slots
                                                if s.count(p1) > 0)
                            p1 = relevant_slots[shuffling[p1_slot_index]][0]

                            if p2 != 'UNVOTE' and p2 != 'NO LYNCH':
                                p2_slot_index = next(relevant_slots.index(s) for s in relevant_slots
                                                    if s.count(p2) > 0)
                                p2 = relevant_slots[shuffling[p2_slot_index]][0]

                            alt_phase_df.append(
                                [p1, p2, post['number'], day, int(number)*iteration_total+iteration, 
                                False, row['uncertainty'], lynch_predicted, transition_predicted])

                            if votecount.choice:
                                break
                    
                    # finish if votecount.choice
                    else:
                        break

                #alt_phase_df = pd.DataFrame(alt_phase_df, 
                #    columns=['voter', 'voted', 'post', 'phase', 'thread', 'manual', 'uncertainty', #'lynch_predicted', 'transition_predicted'])
                alt_votes_df.append(alt_phase_df)
        break

#!%timeit profile_this()

# %%
#!%load_ext line_profiler
#!%lprun -f profile_this profile_this()

# %%

#now = datetime.now()
#results_df = pd.concat(alt_votes_df, ignore_index=True)
#results_df.to_json('data/null_hypothesis_{}.json'.format( now.strftime("%d_%m_%Y")))

# %%
