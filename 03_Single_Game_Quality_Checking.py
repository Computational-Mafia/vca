# %% [markdown]
# # Single Game Quality Checking
# Pick a votes_df, votecounter, thread number, day, and post number to simulate and display:
# - Predicted Votecount Up to Indicated Post Number
# - Predicted Final Votecount for this Day
# - Recorded Log of Votes Up to Final Votecount

# %%
from VoteCounter import VoteExtracter as VoteCounter
import pandas as pd

votes_df = pd.read_json('data/votes_VoteExtracter_21_07_2021.json')
thread_number = 69502
day = 3
postnumber = 1807

votes_df.head()

# %% [markdown]
# ## Other Dependencies

# %%

from IPython.core.display import display, HTML
import markdown2 as md
from copy import deepcopy
import json
from helpers.VoteCount import VoteCount
from helpers.relevantGameInfo import relevantGameInfo

def html(markdown_string):
    display(HTML(md.markdown(markdown_string)))

# open game archive, separate by game
with open('data/archive.txt', encoding='utf-8') as f:
    games = f.read().split('\n\n\n')  

# %% [markdown]
# ## Processing

# %%
postnumber = str(postnumber)
print('Game Thread Number:', thread_number)
print('Day', day)
    
# extract relevant information about this game
for index, game in enumerate(games):
    link = game[:game.find('\n')]
    number = (link[link.find('&t=')+3:] if link.count('&')==1 
                      else link[link.find('&t=')+3:link.rfind('&')])
    if int(number) == thread_number:
        print('Game Index:', index)
        break

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
votecounter = VoteCounter(players=relevant_players, verbose=True)
phase_df = votes_df.loc[(votes_df.phase==int(day)) & (votes_df.thread==int(number))]
post_votecount = None

# also initialize for phase-specific transition prediction
transition_start, transition_end = None, None
transition_match, transition_url = False, None

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
                print('event, killed player:', killed_player)
                print('------------------------------------------')
                killed_slot = next(s for s in relevant_slots if s.count(killed_player) > 0)
                del relevant_slots[relevant_slots.index(killed_slot)]
                relevant_players = []
                for slot in relevant_slots:
                    relevant_players += slot
                votecounter = VoteCounter(players=relevant_players)
                votecount.killplayer(killed_player, post['number'])

    # consider votes until voters have made a choice already
    elif not votecount.choice:
        # ignore posts not made by players
        if relevant_players.count(post['user']) == 0:
            if post_index == int(postnumber):
                post_votecount = deepcopy(votecount)
                html('# Extracted Votes (If Relevant)')
                print(list(votecounter.fromPost(post)))
            continue

        # update votecount for each vote found by votecounter
        # stop considering votes in post if votecount.choice
        for index, row in phase_df.loc[phase_df.post==int(post['number'])].iterrows():
            votecount.update(row['voter'], row['voted'], row['post'])
            if votecount.choice:
                if post_index == int(postnumber):
                    post_votecount = deepcopy(votecount)
                    html('# Extracted Votes (If Relevant)')
                    print(list(votecounter.fromPost(post)))
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
            transition_match = int(game_transitions[day-1]) in list(range(transition_start, transition_end))

    # finish if votecount.choice, transition_start, and transition_end all populated
    else:
        if post_index == int(postnumber):
            post_votecount = deepcopy(votecount)
            html('# Extracted Votes (If Relevant)')
            print(list(votecounter.fromPost(post)))
        break
    if post_index == int(postnumber):
            post_votecount = deepcopy(votecount)
            html('# Extracted Votes (If Relevant)')
            print(list(votecounter.fromPost(post)))

# display extracted and true phase transitions
html('# Phase Transitions')
print('True Transitions:', game_transitions)
print('Predicted Transition:', [list(range(transition_start, transition_end)), transition_url] if (
                transition_start and transition_end) else "None")

html('[{}]({})'.format(*[list(range(transition_start, transition_end)), transition_url] if (
                transition_start and transition_end) else "None"))

# display votecount up to indicated post number
if post_votecount:
    html('# Current Votecount (Up to {})'.format(postnumber))
    current_votecount = post_votecount.todict()
    for each in current_votecount:
        if current_votecount[each]:
            print(each, '-', len(current_votecount[each]))
            for voter in current_votecount[each]:
                print(voter)
            print()

# display final votecount
html('# Final Votecount')
final_votecount = votecount.todict()
for each in final_votecount:
    if final_votecount[each]:
        print(each, '-', len(final_votecount[each]))
        for voter in final_votecount[each]:
            print(voter)
        print()

# display final votelog
html('# Vote Log')
votelog = votecount.votelog.copy()
for index, each in enumerate(votelog):
    each = each.split()
    each[-1] = '[{}]({})'.format(each[-1], next(item for item in gameposts if item["number"] == each[-1])['pagelink'])
    votelog[index] = ' '.join(each)
html('  \n'.join(reversed(votelog)))

# also track prediction outcomes across phases for spot-checking
prediction_outcomes = pd.pivot_table(data=votes_df, index=['thread', 'phase'], values=['lynch_predicted', 'transition_predicted']).reset_index()
errors = prediction_outcomes.loc[(prediction_outcomes.lynch_predicted == False)|(prediction_outcomes.transition_predicted == False)]

# %%
