# %% [markdown]
# # Track Votes
# Don't overcomplicate this at first. I literally just want something that loads the votecounter, loads the archive + relevant posts, and builds a df reflecting votecounter output. 

# %%

# main dependencies
from helpers.VoteCount import VoteCount
from helpers.relevantGameInfo import relevantGameInfo

# helpers for tracking processing progress
import json
import pandas as pd
import time
from datetime import datetime
from tqdm.notebook import trange
import numpy as np

# %% [markdown]
# ## Parameters

# %%

# votecounter to use
from VoteCounter import VoteExtracter as VoteCounter

# range of games in dataset to test votecounter over; leave 0 for no limit
start_index = 0
end_index = 0

# range of game days to consider; leave 0 for no limit
end_day = 0

# verbosity; 0 to exclude game information, 1 for just failure information, 2 for all game information
verbosity = 0

# whether apply hand-made vote labels encoded in data/archive.txt
include_hand_labels = False

# %%

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# process votes in each game's posts until a lynch found
# then store information about votecounter's performance
vote_results, vote_success, transition_results, transition_success, t0, total = {}, 0, {}, 0, time.time(), 0
votes_df = []
end_index = end_index if end_index else len(games)  

# loop through archived games
for game_index in trange(start_index, end_index, desc='game loop'):
    game = games[game_index]

    # extract relevant information about this game
    slots, players, fates, lynched, factions, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(
        game, include_factions=True)

    # remove manually set vote modifying events if we want to exclude those
    if not include_hand_labels:
        
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

    with open('data/posts/{}.jsonl'.format(number)) as f:
        gameposts =  [json.loads(l) for l in f]

    # prepare to collect data for this game
    transition_results[number] = []
    vote_results[number] = []

    for day in trange(1, end_day if end_day else len(game_transitions), desc='phase loop', leave=False):

        # considered games should have at least 1 full phase cycle
        if len(game_transitions) < day+1:
            continue

        # configure extra day-specific information
        ## what makes a correct phase prediction?
        canPredictTransition, canPredictLynch = True, True
        if f'd{day} long twilight' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            canPredictTransition = False
        if f'd{day} hammer after deadline' in game[:game.find(
            '\n\n')].split('\n')[-1][len("Notes: "):].lower():
            canPredictLynch = False
        if f'd{day} no majority' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            correct = []
            canPredictTransition = False
        elif f'd{day} no lynch' in game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):].lower():
            correct = 'NO LYNCH'
        else:
            correct = lynched[day] if day in lynched else []
        
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
        votecounter = VoteCounter(players=relevant_players)
        phase_df = []
        last_vote = {str(slot): 0 for slot in relevant_slots}

        # also initialize for phase-specific transition prediction
        tphase, transition_start, transition_end = time.time(), None, None
        transition_match, transition_url = False, None

        # scan through this game's posts
        for post_index in range(start_point, end_point):#, desc='post loop', leave=False):
            post = gameposts[post_index]

            # first process special events tracked in game notes 
            # (e.g. day kills, votecount resets, missed votes)
            if post['number'] in events:
                post_events = events[post['number']]
                for event in post_events:

                    # if event is a daykill, remove the player from votecount and votecounter
                    if 'killed' == event.split(' ')[-1]:
                        
                        # update relevant slots and players and make new votecounter
                        killed_player = event[:event.rfind(' ')]
                        killed_slot = next(s for s in relevant_slots if s.count(killed_player) > 0)
                        del relevant_slots[relevant_slots.index(killed_slot)]
                        relevant_players = []
                        for slot in relevant_slots:
                            relevant_players += slot
                        votecounter = VoteCounter(players=relevant_players)
                        votecount.killplayer(killed_player, post['number'])
                        
                    # if event is a vote reset, set relevant player(s) to not voting
                    elif 'reset' == event.split(' ')[1]:
                        reset_players = ([s[0] for s in relevant_slots] 
                                        if event.split(' ')[0].lower() == 'votecount'
                                         else [event.split(' ')[0]])
                                         
                        for reset_player in reset_players:
                            votecount.update(reset_player, 'UNVOTE', post['number'])
                            
                            wagon = votecount.todict()['Not Voting']
                            last_vote[str(wagon[-1])] = len(phase_df)
                            phase_df.append(
                                [reset_player, 'UNVOTE', post['number'], day, number, False, 0.0, 0, len(relevant_slots), np.nan, factions[str(wagon[-1])], False, False])
                            
                    # if event is a vote specification set relevant player(s) to vote
                    elif ' voted ' in event:
                        votecount.update(
                            event.split(' voted ')[0], event.split(' voted ')[1], post['number'])

                        voted = event.split(' voted ')[1]
                        if voted == 'UNVOTE':

                            voted_slot = 'Not Voting'
                            voted_faction = np.nan
                        elif voted == 'NO LYNCH':
                            voted_slot = 'No Lynch'
                            voted_faction = np.nan
                        else:
                            voted_slot = str(next(s for s in relevant_slots if s.count(voted) > 0))
                            voted_faction = factions[str(voted_slot)]

                        wagon = votecount.todict()[voted_slot]
                        last_vote[str(wagon[-1])] = len(phase_df)
                        vote_position = len(wagon)

                        phase_df.append(
                            [event.split(' voted ')[0], voted, post['number'], 
                            day, number, True, 0.0, vote_position, len(relevant_slots), 
                            voted_faction, factions[str(wagon[-1])], False, voted in correct])

            # consider votes until voters have made a choice already
            elif not votecount.choice:

                # ignore posts not made by players
                if relevant_players.count(post['user']) == 0:
                    continue

                # update votecount for each vote found by votecounter
                # stop considering votes in post if votecount.choice
                for voted, uncertainty in votecounter.fromPost(post):
                    votecount.update(post['user'], voted, post['number'])

                    if voted == 'UNVOTE':
                        voted_slot = 'Not Voting'
                        voted_faction = np.nan
                    elif voted == 'NO LYNCH':
                        voted_slot = 'No Lynch'
                        voted_faction = np.nan
                    else:
                        voted_slot = str(next(s for s in relevant_slots if s.count(voted) > 0))
                        voted_faction = factions[str(voted_slot)]

                    wagon = votecount.todict()[voted_slot]
                    last_vote[str(wagon[-1])] = len(phase_df)
                    vote_position = len(wagon)

                    phase_df.append(
                        [post['user'], voted, post['number'], day, number, False, uncertainty, vote_position, len(relevant_slots), voted_faction, factions[str(wagon[-1])], False, voted in correct])
                    if votecount.choice:
                        break

            # keep scanning to find newest post by game mod after detected hammer
            elif not transition_start:
                if moderators.count(post['user']) > 0:
                    transition_start = int(post['number'])
                    transition_url = post['pagelink']

            # keep scanning to find last successive post by mod after they end Day
            elif not transition_end:
                if moderators.count(post['user']) == 0:
                    transition_end = int(post['number'])

                    # track match between inferred and transcribed transition post#
                    transition_match = int(
                        game_transitions[day-1]) in list(range(transition_start, transition_end))

            # finish if votecount.choice, transition_start, and transition_end all populated
            else:
                break
    
        phase_df = pd.DataFrame(
            phase_df, 
            columns=['voter', 'voted', 'post', 'phase', 'thread', 'manual', 'uncertainty', 'position', 'total_living', 'voted_faction', 'voter_faction', 'terminal', 'target_eliminated'])
        phase_df.iloc[[last_vote[key] for key in last_vote], phase_df.columns.get_loc('terminal')] = True
        phase_df['lynch_predicted'] = (votecount.choice == correct) if canPredictLynch else True
        phase_df['transition_predicted'] = transition_match if canPredictTransition else True
        votes_df.append(phase_df)
        vote_success += votecount.choice == correct
        transition_success += transition_match
        transition_results[number].append(
            [list(range(transition_start, transition_end)), transition_url] if (
                transition_start and transition_end) else "None")
        vote_results[number].append(votecount)
        total += 1
        if verbosity > 0: 
            #if not (((not canPredictLynch) or votecount.choice == correct) and ((not canPredictTransition) or           transition_match)): # 
            print(day)
            #print(game)
            print(game.split('\n\n')[0])
            print(f'\nIndex: {game_index + start_index}, Thread Number: {number}\nVote Successes: {vote_success}, Transition Successes: {transition_success}, Total Phases Considered: {total}\nVote Success Here: {votecount.choice == correct}, Transition Success Here: {transition_match}\nTime: {time.time()-tphase}')
            print('\n---\n')

print()
print(f'Vote Success Rate: {vote_success/total}, Transition Success Rate: {transition_success/total}, Total Phases Considered: {total}, Total Time: {time.time()-t0}')
votes_df = pd.concat(votes_df, ignore_index=True)

# %%

now = datetime.now()
votes_df.to_json('data/votes_{}_{}.json'.format(VoteCounter.__name__, now.strftime("%d_%m_%Y")))

# %%
