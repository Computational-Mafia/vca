# %% [markdown]
# # Track Missing Data
# We need a system for efficiently identifying missing data, with our initial population being the set of all completed Mini Normal games. We also want to identify _why_ a data point is missing and, when a data point is incomplete, what is present and what isn't. 
#
# ### What kinds of missing data are there?
# We can be missing setup/slot information, phase transition information, voting data, and/or thread content. And information can be missing because it hasn't been successfully extracted yet or because it's missing from the forum (e.g. because of a site crash). Also, rather than being present or missing, information can also instead be _inaccurate_ - but solving that problem requires an entirely different approach from that of detecting missing data, so we focus on it elsewhere. And finally, data can be undesirable - either because of a broken game (e.g. modflaking) or other issues that make inclusion in analysis difficult/unreasonable.
#
# ### How will we manage the prospect of missing data?
# We'll write a script that collects a list of existing completed game threads and checks our data set for associated data, building a list marking wherever data is missing. From there, we'll maintain this list, including updating it regularly as data collection ensues and new games finish, as well as manually marking instances where data collection is impossible or undesirable.

# %% [markdown]
# ## Dependencies

# %%
# dependences
import requests
import csv
import string
from lxml import html

# needed variables
no_punctuation = str.maketrans(string.punctuation+string.ascii_letters, ' '*len(string.punctuation+string.ascii_letters))
completed_url = 'https://forum.mafiascum.net/viewforum.php?f=53&start={}'

with open('data/archive.txt') as f:
    archive = f.read()

# %% [markdown]
# ## Build List of Completed Games and Identify Those Missing from `archive.txt`
# For now we focus solely on Mini Normals. We probably don't need this cell anymore.

# %%
# start by finding number of threads in subforum
base = requests.get(completed_url.format(0)).content
topic_count = html.fromstring(base).xpath('//div[@class="pagination"]/text()')[0].strip()
topic_count = int(topic_count[:topic_count.find(' ')])

# scrape list of game urls and titles across each page of threads
game_urls, game_titles = [], []
for i in range(0, topic_count, 100):
    page = requests.get(completed_url.format(i)).content
    
    # game titles
    titles = html.fromstring(page).xpath("//div[@class='forumbg']//dt/a/text()")
    game_titles += [title.strip() for index, title in enumerate(titles) if index % 2 == 0]
    
    # game urls
    urls = html.fromstring(page).xpath("//div[@class='forumbg']//dt/a/@href")
    game_urls += [url[1:url.find('&sid')] for index, url in enumerate(urls) if index % 2 == 0]

# mark which of these aren't in archive
excluded = []
for index, url in enumerate(game_urls):
    count = archive.count(url[1:] + '\n')
    if count == 0 :
        excluded.append(index)
    
# print counts
print('Number of URLs:', len(game_urls))
print('Number of URLs Unmatched to String in Archive:', len(excluded))
print('Number of Games in Archive:', len(archive.split('\n\n\n')))
print('{} threads unaccounted for!'.format(len(game_urls) - len(excluded) - len(archive.split('\n\n\n'))))
print('Number of URLs After Excluding Duplicates:', len(list(set(game_urls))))
print()

# %% [markdown]
# ## Identify and Count Games Included in transitions.tsv
# Build a list of `games` in `archive.txt` and extract the `numbers` column from `transitions.tsv`. For each archived `game`, check if its `number` is in `numbers`. If it is, then also check if any entry in the associated row has a question mark and if the last entry is a hyphen. 
#
# From this, build lists and print counts of each archived game that 1) has a row in `transitions.tsv`, 2) has no ambiguous transition entries in their row, and/or 3) has a definitely finish entry in their row. And any other information that provides context for these counts.

# %%
# build list of games
games = archive.split('\n\n\n')

# extract game_numbers column from transitions.tsv
transitions, numbers = [], []
count = 0
with open('data/transitions.tsv') as f:
    for row in csv.reader(f, delimiter='\t'):
        transitions.append(row)
        numbers.append(row[0])

# check each game
for archive_index, game in enumerate(games):
    title = game.split('\n')[1]
    number = [i for i in title.translate(no_punctuation).split() if i.isdigit()][0]
    url = game.split('\n')[0]
    
    # check if its number is in extracted numbers
    if numbers.count(number) != 1:
        print('Data Not Found:', number, numbers.count(number), title)
        count += 1
        continue
        
    # check if an entry has question mark
    row_index = numbers.index(number)
    row = transitions[row_index]
    if '?' in '\t'.join(row) or 'missing' in '\t'.join(row).lower():
        print('Uncertainty Detected:', number, row_index+1, row)
        print(url)
        count += 1
        continue
        
    # check if an entry has completeness
    if ''.join(row).strip()[-1] != '-':
        print('Incompleteness Detected:', number, row_index+1, row)
        print(url)
        count += 1

print(count)

# %%
