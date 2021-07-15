# %% [markdown]
# # Clean `archive.txt`
# A notebook for systematic fixes to `archive.txt`. Functions should not do anything if fixes are already applied.
#
# ## Correct Urls
# A lot of archive urls are flat-out wrong. We have to match them to their correct url for better processing later.

# %%
# dependences
import requests
import string
from lxml import html

# translator for removing punctuation from arbitrary string
no_punctuation = str.maketrans(string.punctuation+string.ascii_letters, ' '*len(string.punctuation+string.ascii_letters))

# path for all completed games
completed_url = 'https://forum.mafiascum.net/viewforum.php?f=53&start={}'

# archive data
with open('data/archive.txt') as f:
    archive = f.read().split('\n\n\n')

# %% [markdown]
# #### Scrape Relevant URLs and Titles
# We start by finding the total number of threads in the subforum so we can guide traversal then collect on each page of the subforum relevant thread URLs (and at the moment, some irrelevant ones).

# %%
# start by finding number of threads in subforum
base_page = requests.get(completed_url.format(0)).content
topic_count = html.fromstring(base_page).xpath('//div[@class="pagination"]/text()')[0].strip()
topic_count = int(topic_count[:topic_count.find(' ')])

# scrape list of game urls and titles across each page of threads
game_urls, game_titles, game_numbers = [], [], []
for i in range(0, topic_count, 100):
    page = requests.get(completed_url.format(i)).content
    
    # game titles
    titles = html.fromstring(page).xpath("//div[@class='forumbg']//dt/a/text()")
    game_titles += [title.strip() for index, title in enumerate(titles) if index % 2 == 0]
    
    # game numbers
    for title in [title.strip() for index, title in enumerate(titles) if index % 2 == 0]:
        number = [int(i) for i in title.translate(no_punctuation).split() if i.isdigit()]
        game_numbers.append(number[0] if len(number) > 0 else [])
    
    # game urls
    urls = html.fromstring(page).xpath("//div[@class='forumbg']//dt/a/@href")
    game_urls += [url[1:url.find('&sid')] for index, url in enumerate(urls) if index % 2 == 0]

# %% [markdown]
# #### Match Each Archived Game to Scraped URL
# For each archived `game`, get its `title` and infer its associated `number`. Attempt `index` of that `number` within scraped `game_numbers`. The correct `url` for that game has the same `index` inside `game_urls`.

# %%
for archive_index, game in enumerate(archive):
    # collect game title and infer game number from it
    game = game.split('\n')
    title = game[1]
    number = [int(i) for i in title.translate(no_punctuation).split() if i.isdigit()][0]
    
    # match and replace fixed url
    scrape_index = game_numbers.index(number)
    game[0] = "https://forum.mafiascum.net" + game_urls[scrape_index]
    archive[archive_index] = "\n".join(game)

with open('data/archive.txt', 'w') as f:
    f.write('\n\n\n'.join(archive))

# %%
