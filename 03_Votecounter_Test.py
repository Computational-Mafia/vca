# %% [markdown]
# # VotecounterTest
# A script for setting up and executing performance tests on votecounters.

# %% [markdown]
# ## Select Your Votecounter
# Modify the cell below to import the wrapper class for your VoteCounter and assign it to the variable `VoteCounter` before executing the notebook. When you run the notebook, your votecounter will be evaluated and various troubleshooting messages and summary statistics displayed characterizing its performance. See the README for more information or PM me or whatever.

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

# to help generate formatted output representations
from IPython.core.display import display, HTML
import markdown2 as md

def html(markdown_string):
    display(HTML(md.markdown(markdown_string)))


# %% [markdown]
# ## VotecounterTest

# %%
# range of games in dataset to test votecounter over; leave 0 for no limit
start_index = 0
end_index = 0

# range of game days to consider; leave 0 for no limit
start_day = 1
end_day = 0

# verbosity; 0 to exclude game information, 1 for just failure information, 2 for all game information
verbosity = 0

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# process votes in each game's posts until a lynch found
# then store information about votecounter's performance
vote_results, vote_success, transition_results, transition_success, t0, total = {}, 0, {}, 0, time.time(), 0
end_index = end_index if end_index else len(games)  
for game_index, game in tqdm(enumerate(games[start_index:end_index])):
    
    # extract relevant information about this game
    slots, players, fates, lynched, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(game)

    with open('data/posts/{}.jsonl'.format(number)) as f:
        gameposts =  [json.loads(l) for l in f]
        
    # prepare to collect data for this game
    transition_results[number] = []
    vote_results[number] = []
    
    for day in range(1, end_day if end_day else len(game_transitions)):
        
        # we'll remove this later; don't scan games that don't have this many games
        if len(game_transitions) < day+1:
            print('WE DO USE THIS')
            continue
    
        # identify day-specific information and set up votecounter and votecount for them
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
            
        start_point = 0 if day == 1 else int(game_transitions[day-2])
        end_point = int(game_transitions[day-1])+1 if not correct else len(gameposts)
        relevant_slots = [slot for slot_index, slot in enumerate(slots) if fates[slot_index] >= day]
        relevant_players = []
        for slot in relevant_slots:
            relevant_players += slot
        votecount = VoteCount(relevant_slots, meta={'correct': correct}, lessOneForMislynch=lessOneForMislynch, doublevoters=doublevoters)
        votecounter = VoteCounter(players=relevant_players)

        tphase, transition_start, transition_end, transition_match, transition_url = time.time(), None, None, False, None

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

        vote_success += votecount.choice == correct
        transition_success += transition_match
        transition_results[number].append([list(range(transition_start, transition_end)), transition_url] if transition_start and transition_end else "None")
        vote_results[number].append(votecount)
        total += 1
        if verbosity > 0: 
            #if not (((not canPredictLynch) or votecount.choice == correct) and ((not canPredictTransition) or           transition_match)): # 
            print(day)
            #print(game)
            print(game.split('\n\n')[0])
            print(f'\nIndex: {game_index + start_index}, Thread Number: {number}\nVote Successes: {vote_success}, Transition Successes: {transition_success}, Total Phases Considered: {total}\nVote Success Here: {votecount.choice == correct}, Transition Success Here: {transition_match}\nTime: {time.time()-tphase}')
            print('\n---\n')

print(f'Vote Success Rate: {vote_success/total}, Transition Success Rate: {transition_success/total}, Total Phases Considered: {total}, Total Time: {time.time()-t0}')

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

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  
    
# extract relevant information about this game
game = games[game_index]
slots, players, fates, lynched, number, game_transitions, moderators, events, doublevoters, lessOneForMislynch = relevantGameInfo(game)

with open('data/posts/{}.jsonl'.format(number)) as f:
    gameposts =  [json.loads(l) for l in f]

# find and display selected post along with votecounter output for it
html('# Post {}'.format(postnumber))
post = next(item for item in gameposts if item["number"] == postnumber)
print('Extracted Votes (If Relevant):', list(votecounter.fromPost(post)))
print()
print(post)
print()
display(HTML(post['content']))

# display extracted and true phase transitions
html('# Phase Transitions')
print('True Transitions:', game_transitions)
print(transition_results[number][day-1])
html('[{}]({})'.format(*transition_results[number][day-1]))

# identify day-specific information and set up votecounter and votecount for them
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

start_point = 0 if day == 1 else int(game_transitions[day-2])
end_point = int(game_transitions[day-1])+1 if not correct else len(gameposts)
relevant_slots = [slot for slot_index, slot in enumerate(slots) if fates[slot_index] >= day]
relevant_players = []
for slot in relevant_slots:
    relevant_players += slot
votecount = VoteCount(relevant_slots, meta={'correct': correct}, lessOneForMislynch=lessOneForMislynch, doublevoters=doublevoters)
votecounter = VoteCounter(players=relevant_players)

tphase, transition_start, transition_end, transition_match, transition_url = time.time(), None, None, False, None

# scan through this game's posts
for post in gameposts[start_point:int(postnumber)]:

    # prioritize any events associated with post
    if post['number'] in events:
        post_events = events[post['number']]
        for event in post_events:

            # if event is a daykill, remove the player from votecount and votecounter
            if 'killed' == event.split(' ')[-1]:

                # update relevant slots and players and make new votecounter
                killed_player = event[:event.rfind(' ')]
                print(killed_player)
                print('------------------------------------------')
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
        
# display votecount up to indicated post number
html('# Current Votecount (Up to {})'.format(postnumber))
current_votecount = votecount.todict()
for each in current_votecount:
    if current_votecount[each]:
        print(each, '-', len(current_votecount[each]))
        for voter in current_votecount[each]:
            print(voter)
        print()

# display final votecount
html('# Final Votecount')
final_votecount = vote_results[number][day-1].todict()
for each in final_votecount:
    if final_votecount[each]:
        print(each, '-', len(final_votecount[each]))
        for voter in final_votecount[each]:
            print(voter)
        print()
        
# display final votelog
html('# Vote Log')
votelog = vote_results[number][day-1].votelog.copy()
for index, each in enumerate(votelog):
    each = each.split()
    each[-1] = '[{}]({})'.format(each[-1], next(item for item in gameposts if item["number"] == each[-1])['pagelink'])
    votelog[index] = ' '.join(each)
html('  \n'.join(reversed(votelog)))

# %%
