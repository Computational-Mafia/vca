# # LevenshteinCounter
# A very basic votecounter that exists mainly to set a baseline for future improvements and to make sure that the surrounding framework actually works.

# +
# to detect slight misspellings
import editdistance as ed

# to help parse website content
from lxml import html

# paths useful for finding votes in posts
votepath1 = '/html/body/p/span[@class="{}"]//text()'
votepath2 = '/html/body/span[@class="{}"]//text()'
votepath3 = '/html/body/p/span/span[@class="{}"]//text()'
votepath4 = '/html/body/span/span[@class="{}"]//text()'
votepath5 = '/html/body/p/span[@class="{}"]'
votepath6 = '/html/body/span[@class="{}"]'
subpath = 'span//text()'


# -

# ### Find Votes
# The function `findVotes()` locates/returns the votes in a post w/o attempting to identify the player voted. The problem of just telling when/where someone is *trying* to make a vote is itself pretty substantive, as users have access to a variety of ways of specifying votes, can misspell "vote", accidentally use broken tags, or attempt fancy formatting of their votes besides simple `[b][/b]` or `[vote][/vote]` structures. Votes can also often be broken up into multiple lines or otherwise made remote from the naming of a vote's target.
#
# This function handles all these issues in a way that (attempts to) mimics how actual moderators have almost always behaved across the 300 Mini Normal Games studied to develop this module.

# +
def findVotes(post):
    "Returns list of votes present in the posts content"
    sel = html.fromstring('<html><body>' + post['content'] + '</body></html>')
    
    # pull out all relevant tags
    tagclass = 'noboldsig'
    boldtags = (sel.xpath(votepath1.format(tagclass)) +
                sel.xpath(votepath2.format(tagclass)) +
                sel.xpath(votepath3.format(tagclass)) +
                sel.xpath(votepath4.format(tagclass)) +
                [''.join(each.xpath(subpath)) for each 
                 in sel.xpath(votepath5.format(tagclass))] +
                [''.join(each.xpath(subpath)) for each 
                 in sel.xpath(votepath6.format(tagclass))]
               )
    tagclass = 'bbvote'
    votetags = (sel.xpath(votepath1.format(tagclass)) +
                sel.xpath(votepath2.format(tagclass)) +
                sel.xpath(votepath3.format(tagclass)) +
                sel.xpath(votepath4.format(tagclass)) +
                [''.join(each.xpath(subpath)) for each 
                 in sel.xpath(votepath5.format(tagclass))] +
                [''.join(each.xpath(subpath)) for each 
                 in sel.xpath(votepath6.format(tagclass))]
               )
    
    # first of all, though, we handle broken bold tags similarly
    # after some preprocessing, so let's add those
    for content in (sel.xpath('/html/body/text()') +
                    sel.xpath('/html/body/p/text()')):
        if content.count('[/b]') > 0:
            # up to broken tag
            tagline = content[:content.find('[/b]')].lstrip().rstrip()
            boldtags.append(tagline)
        if content.count('[b]') > 0:
            # starting at broken tag
            tagline = content[content.find('[b]')+3:].lstrip().rstrip()
            boldtags.append(tagline)
    
    #  we want votetags to have priority, so add them to the pool here
    boldtags = boldtags + votetags
    boldtags = [b.rstrip().lstrip() for b in boldtags]
    
    # they need to have 'vote' or 'veot' early in their string
    boldtags = [b for b in boldtags
                if b[:7].lower().count('vote') or b[:7].lower().count('veot') > 0 or b[:7].lower().count('vtoe') > 0 or b[:7].lower().count('ovte') > 0]
    
    # rfind 'vote' and 'unvote' (and their key mispellings) to locate vote
    for i, v in enumerate(boldtags):
        voteloc = max(v.lower().rfind('vote'), v.lower().rfind('veot'), v.lower().rfind('vtoe'), v.lower().rfind('ovte'))
        unvoteloc = max(v.lower().rfind('unvote'), v.lower().rfind('unveot'), v.lower().rfind('unvtoe'), v.lower().rfind('unovte'))
        
        # if position of unvote is position of vote - 2, 
        # then the last vote is an unvote
        if unvoteloc > -1 and unvoteloc == voteloc - 2:
            boldtags[i] = 'UNVOTE'
            
        # otherwise vote is immediately after 'vote' text and perhaps some crap
        else:
            boldtags[i] = v[voteloc+4:].replace(
                ': ', ' ').replace(':', ' ').replace('\n', ' ').rstrip().lstrip()

    votes = boldtags
    return [v for v in votes if len(v.strip()) > 0]

def includesVote(post):
    """Returns whether a vote is present in the post's content or not"""
    return len(findVotes(post)) > 0


# -

# ## The LevenshteinExtracter Class
# Initialized with a playerlist to avoid redundant processing, includes a function that uses a series of text processing tricks to match votes found with the findVotes() function to a member of said playerlist. 

class LevenshteinExtracter:
    
    def __init__(self, players):
        
        self.players = players
        self.lowplayers = {p.lower(): p for p in players}
        
    def fromPost(self, post):
        """tries to identify vote's target from the post"""
        votes = findVotes(post)
        yield from self.fromVotes(votes, post=post)

    def fromVotes(self, votes, post=None):
        """tries to identify targets from list of votes"""
        votes = [v for v in votes if len(v) > 0]

        for vote in votes:

            lowvote = vote.lower()
            distances = {self.lowplayers[p]:ed.eval(p, lowvote)
                         for p in self.lowplayers}
            yield min(distances, key=distances.get)


