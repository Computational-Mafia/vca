## What's The Gist of What I'd Need in a Vote DF?
We'll first consider each requested analysis.

### % of scum self-votes to town self-votes
Need to be tracking voter or voted faction.
Need for each vote the slot identity of the voter and the voted.

This doesn't need a raster plot per se but I might be interested in exploring the position of self-votes between conditions. What I want here is just to plot two proportions.

### a version of the self-vote analysis that excludes self-hammers
Need to also track whether a vote constitutes a hammer or not.

### % of scum first vote busses vs scum first vote town votes
Need to also track the size of the corresponding wagon upon each vote.

Raster plot for different subsets of wagons if I want. 

### % of scum L-1s that are not hammered
Have to track wagon outcome somehow - this isn't something I can do in realtime like the others.

### % of scum hammers on town
### % of scum hammers on scum
### % of town hammers on town
### % of town hammers on scum
### how often scum bus (2x)

### how often there's more than one scum on a wagon (2x)
Have to consider multiple votes simultaneously - tough one. But vote position column technically does something similar. Just maintain a count of each faction on the wagon. 

### how often scum vote right next to each other (2x)
Would need to track positions of other votes within a row - definitely a stretch. Probably will have to be a derived column that I don't include in the main df. How would I draw this? A column that tracks lag from last scum vote, for example. I'd have a function that maintains a votecount but with factional information in the list instead of slot information and then does the count on that.

### how often do scum vote someone, vote somewhere else, then return to the original vote, and how often town do it in contrast
Also clearly a derived analysis. To identify the condition would have to track for each vote the last two positions of the vote.

### what % of chronological time during a day phase someone was voting no one?
This is not actually a very interesting question.

## Plan?
For a lot of the special analysis, I'll likely end up simulating voting up to vote number (except only having to use my VoteCount.py class) and updating a list of values with the result. And that's fine. The key then is tracking the position of all applicable votes within phase and game. Indeed, every other detail is something I could technically extract separately to support a particular analysis. Should I lean that way? Well, not quite. Any game data I have that can't be grabbed from votecount simulation is also worth grabbing - for example, factional data, slot/player data, and so on. 

Still -- can't I at least assume that a developer will also have the information necessary for initializing the votecounter? Yes, I think so. Then what's necessary here? Just the votes and any available information clarifying how/why the votes were identified. That's it.

And what's that clarifying information? Prediction information. And any metadata my votecounter can share. Okay then!

Big advantage is that this frees me to focus on analysis components in scripts focused on those.

So I want a dataframe that tracks for each vote...
- voter
- voted
- post number
- phase number
- game id

And nothing else? Yeah, for a moment. I just needed an ordered sequence of votes and enough information to match them back to the appropriate phase-specific and post-specific information.

## What's a Good Opener Analysis?
I was clearly interested in raster plots before. What kind of content was I interested in?

Suppose we focus on D1 wagons that end in a hammer. I can plot a raster plot across all those D1s tracking the final position of each faction on each wagon. 

What would we observe from this? If there are any systematic patterns in factional position on these wagons, it'll be visibly obvious like the recency effect. This makes the plot a decent opener prior to more specific analyses surrounding position on a wagon. 

I guess the top priority though should be be the votecounter at this point.