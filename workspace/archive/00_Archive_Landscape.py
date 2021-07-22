# %% [markdown]
# # Archive Landscape
# I'm interested in mapping out the landscape of the full Completed Games Archive that I can readily or not so readily include in an automated vote count analysis. This information can help organize further archival work as well as downstream analyses.

# %% [markdown]
# ## Context

# %% [markdown]
# I want to convince actual or potential volunteers maintaining the MafiaScum Completed Games archive to:
# - track a broader range of information, particularly identifiers of important game events
# - take measures to validate their records, especially player and outcome information, and
# - integrate computational tools into their workflow to help achieve this at scale
#
# To achieve this, I need to:
# - Hand them tools that make the task dramatically more easy and are easy to start using
# - Outline a format for data that helps them understand what would be the intermediate product of their work
# - Demo some analysis outputs over a hypothetically enhanced archive to help them understand the potential final stage product of their work
#
# In other words, I need concrete visualizations and examples to show these guys that these efforts would mean something and that I'm committed to helping them realize their fullest potential.

# %% [markdown]
# ## Relevant Variables

# %% [markdown]
# - **Game types**. There are Newbie Games, Large Normals, Mini Normals, Mini Themes, Large Themes, Opens, Micros, and Team Mafia games.
# - **Game years**. Games completed at different times, and conventions around voting, setup, and other game features vary with respect to time. We are especially interested in analysis of more recent games.
# - **Game moderators**. Different people ran the games.
# - **Game players**. Players are grouped into slots, which each have a role, faction, and fate.
# - **Game outcomes**. It's useful to know who won or lost. Some games were abandoned or otherwise interrupted.
# - **Record completeness**. Some game threads are missing posts. There's no apparent way to infer this feature automatically though.
# - **Game name**. Games have names identifying them.
# - **List mods**. List mods tend to ocassionally post in games especially with a bookend post before archiving them.
# - **Extraneous posters**. Sometimes someone posts in a game thread even though they're not involved in it. Normally this is because the game is over.

# %% [markdown]
# ## Approach
# Across cases I'll try to:
# 1. Assess across games how parseable the main records are
# 2. Check among parseable records for straightforward evidence of invalid records (e.g. username conflicts)
# 3. Visualize high-level summaries of the distributions of these inconsistencies across known game features
# 4. Develop interpretable visualizations tracking these apparent inconsistencies
# 5. Pair these visualizations with an interface to help streamline repair of inconsistencies
# 6. Relate these efforts to my VotecounterTest framework for identifying inconsistencies in archival data by comparing them against patterns identified using an automatic votecounter.

# %% [markdown]
# ## Case Study: Mini Normals
# To help build familiarity with the problem, I'll start with the most familiar archive (Mini Normals), and branch out. I'll keep the other archives in mind though as I try to keep my codebase applicable across archiving approaches. 
#
# The Mini Normal Archive is located across two threads, one [here](https://forum.mafiascum.net/viewtopic.php?f=53&t=29549) and one [here](https://forum.mafiascum.net/viewtopic.php?f=53&t=15732). The threads are chronological such that all the games mentioned in one thread were completed after all the games in another. I can start by identifying each game thread mentioned in these archives, attempting to match them to a URL in the Complete Mini Normal Archive, and measuring any discrepancies.

# %%
from donbot import Donbot

second_thread = 'https://forum.mafiascum.net/viewtopic.php?f=53&t=29549'
first_thread = 'https://forum.mafiascum.net/viewtopic.php?f=53&t=15732'

bot = Donbot(username='Psyche', password=input())

# %%
from lxml import html

# content of a post
contentpath = ".//div[@class='content']/text()"

bot.getPosts(first_thread)[0]['content']

# %%
doc = html.fromstring(bot.getPosts(first_thread)[0]['content'].replace('<br>', '\n<br>'))
    
print(doc.text_content())

# %%
