# %% [markdown]
# # Track Votes
#  A notebook applying a selected automatic votecounter to applicable games to build a long-form table of voting data suitable for further analysis.

# %% [markdown]
# ## Select Your Votecounter
# Modify the cell below to import the wrapper class for your VoteCounter and assign it to the variable `VoteCounter` before executing the notebook.
#

# %%
from votecounters.LevenshteinCounter import LevenshteinExtracter as VoteCounter

# %% [markdown]
# ## Other Dependencies

# %%
import json
import time
from helpers.VoteCount import VoteCount
from helpers.relevantGameInfo import relevantGameInfo
from tqdm import tqdm
import pandas as pd

# %%
# range of games in dataset to consider; leave 0 for no limit
start_index = 0
end_index = 0

# range of game days to consider; leave 0 for no limit
start_day = 1
end_day = 0

# %% [markdown]
# ## Processing

# %%
# data structures to build over vote tracking
pass

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# process votes in each game's posts until a lynch found
# track relevant data for each detected vote
for game_index, game in tqdm(enumerate(games[start_index:end_index])):

    # retrieve relevant annotations about this game
    slots, players, fates, lynched, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(game)

    # retrieve posts corresponding to this game
    with open('data/posts/{}.jsonl'.format(number)) as f:
        gameposts =  [json.loads(l) for l in f]

    # game-specific data structures to fill
    pass

    for day in range(1, len(game_transitions)):
        
        # retrieve ground truth info for votecounter evaluation
        canPredictTransition, canPredictLynch = True, True
        note_string = game[:game.find(
            '\n\n')].split('\n')[-1][len('Notes: '):].lower()

        if f'd{day} long twilight' in note_string:
            canPredictTransition = False
        if f'd{day} hammer after deadline' in note_string:
            canPredictLynch = False
        
        if f'd{day} no majority' in note_string:
            correct = None
            canPredictTransition = False
        elif f'd{day} no lynch' in note_string:
            correct = 'NO LYNCH'
        else:
            correct = lynched[day] if day in lynched else None

        # configure relevant player list and post range
        start_point = 0 if day == 1 else int(game_transitions[day-2])
        end_point = int(game_transitions[day-1])+1 if not correct else len(gameposts)
        relevant_slots = [slot for slot_index, slot in enumerate(slots) if fates[slot_index] >= day]
        relevant_players = []
        for slot in relevant_slots:
            relevant_players += slot
        votecount = VoteCount(relevant_slots, meta={'correct': correct}, lessOneForMislynch=lessOneForMislynch, doublevoters=doublevoters)
        votecounter = VoteCounter(players=relevant_players)

        # scan through this game's posts
        for post in gameposts[start_point:end_point]:
            
            # prioritize any events associated with post
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
                            
                    # if event is a vote specification, set relevant player(s) to vote
                    elif ' voted ' in event:
                        votecount.update(event.split(' voted ')[0], event.split(' voted ')[1], post['number'])

            # consider no more votes if voters have made a choice already
            elif not votecount.choice:

                # ignore posts not made by players
                if relevant_players.count(post['user']) == 0:
                    continue

                # update votecount for each vote found by votecounter
                # stop considering votes in post if votecount.choice
                for voted in votecounter.fromPost(post):
                    votecount.update(post['user'], voted, post['number'])
                    if votecount.choice:
                        break

            # keep scanning to find newest post by game mod after detectedhammer
            elif not transition_start:
                if moderators.count(post['user']) > 0:
                    transition_start = int(post['number'])
                    transition_url = post['pagelink']

            # keep scanning to find last successive post by mod after they end Day
            elif not transition_end:
                if moderators.count(post['user']) == 0:
                    transition_end = int(post['number'])

                    # track match between inferred and transcribed transition post#
                    transition_match = int(game_transitions[day-1]) in list(range(transition_start, transition_end))

            # finish if votecount.choice, transition_start, and transition_end all populated
            else:
                break

# %%
