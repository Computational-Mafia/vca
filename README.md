# The Great Vote Count Analysis
a dataset and codebase for research exploring voting patterns by players at MafiaScum

## VotecounterTest
If you've coded up a tool for automatically tracking votes made in games on MafiaScum, you may be looking for a straightforward way to test if it's any good, if it really can handle the various ways people abbreviate, misspell, misformat, or otherwise convey votes in a manner that deviates from the standard convention of enclosing a player's username in a `[vote]` tag.

A really burdensome but thorough way to test this might be to pick a large number of games, go through each one to hand-label each vote and its target plus relevant metadata like each game's playerlist and when each person died, and then run your votecounter over each game to test how often it identifies the votes you labeled. 

Another approach that requires considerably less hand-labeling is to focus tool evaluation on the more distant consequences of voting: lynches, and the other ways a Day can end. In other words, if you know who got lynched on a given Day in a given game, you can test your automatic votecounter by simulating it over all the posts in that Day of that game and checking what it "thinks" was the outcome of that Day, calling it a win if the prediction matches the known outcome. Since figuring out who got lynched each Day across a large pool of games is less work than hand-coding all the votes in those games, this works out to a significantly more efficient approach to systematic votecounter evalation. This project includes for a large and growing pool of games all the data necessary for evaluating automatic votecounter with this approach. But that's not all!

This process also includes for most of these games the post numbers of important phase transitions throughout these games. This enables the above outlined approach to be extended in two ways. First, it enables you to use phases beyond D1 across your games to test your votecounter. Without knowing exactly when D2 starts, it's much harder for an automatic votecounter to predict lynches accurately, even if it can identify votes in posts pretty accurately, since votes from the previous Day might be included, or from the current Day excluded. Second, it enables you to further evaluate your votecounter by having it try to predict not just the outcome of a Day (who got lynched) but also the number of the post ending that Day and then comparing against a ground truth. This prediction can be heuristically made by finding the first moderator post after a detected hammer vote. 

So altogether VoteCounterTest can test, over a dataset of finished games:
1. Whether your automatic votecounter can tell who got lynched on each Day of each game,
2. Whether your automatic votecounter can identify the post number upon which that person got lynched

### Usage
To use VotecounterTest, you'll need a wrapper Python class around your votecounter that:
1. Accepts a list of player usernames as an argument upon initialization (you can do whatever you want with it, including ignore it if that's what you prefer), and 
2. A `fromPost` function that takes the HTML of a game post as an argument and returns a list of player usernames corresponding to its predictions about who, if anyone, was voted for in that post. The list should be empty if no votes are detected.

You'll also need a scraped dataset of all posts corresponding to each game in the dataset; these posts are not maintained within this repository. Running `00_Scrape_Archive.ipynb` notebook located at the root of this project though should carry out the web scraping of posts from relevant games for you. Corresponding `01_Clean_Archive.ipynb` and `02_Track_Missing_Data.ipynb` notebooks should also be fully executed to ensure your scraped dataset is complete and includes no duplicate posts or other issues.

From there, just modify the top cell in the VotecounterTest notebook to import the wrapper class for your VoteCounter and assign it to the variable `VoteCounter` before executing the notebook. When you run the notebook, your votecounter will be evaluated and various troubleshooting messages and summary statistics displayed characterizing its performance.

From there, you can hopefully 'debug' your votecounter and rerun the notebook again, repeating this iteration until you're satisfied with or give up on your code.