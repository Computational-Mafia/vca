# -*- coding: utf-8 -*-
# # Votecounter
# Includes Psyche's version of a VoteExtracter class for extracting votes from posts, and a set of helper functions and variables used to pull that off. These are discussed in detail at their location in the notebook.
#
# Rather than being very strict about what counts as a vote (ie looking for proper vote formatting and exact target naming), this function is intended to work like human moderators do, or at least have over the D1s of ~300 Mini Normal Games studied to produce the function. The VoteExtractor class has been found to accurately predict which player a moderator assigned a lynch to across nearly all of these studied games - all without relying on any explicit database of aliases.
#
# If aliases are *totally* necessary to understand the target of a vote (for example, when someone uses a user's true first name instead of some nickname based on their username), though, VoteExtracter is a bit more likely to fail. In order to include aliases in VoteExtracter functioning, add any desired aliases to the list of players included when you initialize an instance of the class. A cleaner option, though, might be to ban votes that require such contextual knowledge to interpret their target.
#
# `votecounter.py` is produced by converting the front-facing notebook `votecounter.ipynb` using the jupyter command `jupyter nbconvert --to script votecounter.ipynb`.
#
# This notebook/script was developed in work described in `votecounterdev.ipnyb` based on Mini Normal Archive data listed in `archive.txt`. The associated archive of posts associated with the listed games is too large to be uploaded to GitHub, but may be obtainable by scraping the data or contacting Psyche.
#
# ## Setup
#
# ### Dependencies

# +
import os

# to detect slight misspellings
import editdistance as ed
    
# spellchecker to help identify english words
from spellchecker import SpellChecker
spell = SpellChecker()

# to help parse website content
from lxml import html
    
# sadly we rely on regular expressions
import re

# regex filters
regall = re.compile('[^a-zA-Z]') # any character that IS NOT a-z OR A-Z
regup = re.compile('[^A-Z]') # any character that IS NOT A-Z

# paths useful for finding votes in posts
votepath1 = '/html/body/p/span[@class="{}"]//text()'
votepath2 = '/html/body/span[@class="{}"]//text()'
votepath3 = '/html/body/p/span/span[@class="{}"]//text()'
votepath4 = '/html/body/span/span[@class="{}"]//text()'
votepath5 = '/html/body/p/span[@class="{}"]'
votepath6 = '/html/body/span[@class="{}"]'
votepath7 = '/html/body/fieldset/span[@class="{}"]//text()'
subpath = 'span//text()'


# -

# ## Helper Functions
#
# ### English Divides
# The function `englishdivides()` returns a list of ways the input playername can be divided into strings considered legal words by one of the spellchecker dictionaries, with the list sorted from least to greatest by number of divisions. The spellchecker often accepts as legal many single character and two-character strings that I wouldn't recognize as actual words, so this sorting is important. The result is a data structure helpful for predicting how users might abbreviate or otherwise fail to totally specify a player's name in their vote (eg, "FB" for "Firebringer"). 
#
# Strangely, the full list is often sufficient for predicting errors/abbreviations of usernames that aren't even straightforward compositions of 'legal' english words. Maybe our english-langauge vocabularies play a role in structuring mistaken spellings of non-english language strings.

# returns ways the string can be split into english words or letters, 
# ordered from least to most number of divisions
def englishdivides(playername):
    string = regall.sub('', playername) # filter non-letters
    passes = [[['']]]
    fulldivides = []
    while len(passes[-1]) > 0:
        passes.append([])
        for p in passes[-2]:
            for i in range(len(''.join(p))+1, len(string)+1):
                substring = string[len(''.join(p)):i]
                if (not spell.unknown([substring])):
                    passes[-1].append(p + [substring])

                    if len(''.join(p + [substring])) == len(string):
                        fulldivides.append(p + [substring])
    return fulldivides

# ### Find Votes
# The function `findVotes()` locates/returns the votes in a post w/o attempting to identify the player voted. The problem of just telling when/where someone is *trying* to make a vote is itself pretty substantive, as users have access to a variety of ways of specifying votes, can misspell "vote", accidentally use broken tags, or attempt fancy formatting of their votes besides simple `[b][/b]` or `[vote][/vote]` structures. Votes can also often be broken up into multiple lines or otherwise made remote from the naming of a vote's target.
#
# This function handles all these issues in a way that mimics how actual moderators have almost always behaved across the 300 Mini Normal Games studied to develop this module.

# locates/returns the votes in a post w/o identifying the player voted
def findVotes(post):
    "Returns list of votes present in the posts content"
    sel = html.fromstring('<html><body>' + post['content'] + '</body></html>')
    
    # pull out all relevant tags
    tagclass = 'noboldsig'
    boldtags = (sel.xpath(votepath1.format(tagclass)) +
                sel.xpath(votepath2.format(tagclass)) +
                sel.xpath(votepath3.format(tagclass)) +
                sel.xpath(votepath4.format(tagclass)) +
                sel.xpath(votepath7.format(tagclass)) +
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
                sel.xpath(votepath7.format(tagclass)) +
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

    # commas and line breaks divide bold tags
    boldtags = [line for tag in boldtags for line in tag.replace(', ', '\n').split('\n')]
    
    #  we want votetags to have priority, so add them to the pool here
    boldtags = boldtags + votetags
    boldtags = [b.rstrip().lstrip() for b in boldtags]
    

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

# ## The VoteExtracter Class
# Initialized with a playerlist to avoid redundant processing, includes a function that uses a series of text processing tricks to match votes found with the findVotes() function to a member of said playerlist. Rather than being very strict about what counts as a vote (ie looking for proper vote formatting and exact target naming), this function is intended to work like human moderators do, or at least have over the D1s of ~300 Mini Normal Games studied to produce the function. The VoteExtractor class has been found to accurately predict which player a moderator assigned a lynch to across nearly all of these studied games.

class VoteExtracter:
    def __init__(self, players, verbose=False):
        
        # make an acronym dictionary for each player
        self.playerabbrevs, self.players, self.verbose = {}, players, verbose
        self.lowplayers = {p.lower():p for p in players}
        
        self.englishdivides = {p:englishdivides(p) for p in players}
        for p in players:
            self.playerabbrevs[p] = ''.join([each[0] for each in self.englishdivides[p][0][1:]])
            
    def fromPost(self, post):
        """tries to identify vote's target from the post"""
        votes = findVotes(post)
        if self.verbose:
            print('Initially identified votes: ', votes)
        yield from self.fromVotes(votes, post=post)

    def fromVotes(self, votes, post=None):
        """tries to identify targets from list of votes"""
        
        # yield a list of votes in a post and process them all 'in order'
        # with the exception of same-line unvote-then-vote happenings
        votes = [v for v in votes]
        for vote in votes:
            if self.verbose:
                print()
                print('Processing:', vote)
            
            original_text = vote
            result_code = 0 

            while True:

                # empty votes shouldn't be processed
                if len(vote) == 0:
                    break

                # pre-computation of values i'll need repeatedly
                lowvote = vote.lower()
                distances = {self.lowplayers[p]:ed.eval(p, lowvote)
                            for p in self.lowplayers}

                if vote == 'UNVOTE':
                    yield 'UNVOTE', result_code
                    break

                # check for no lynch votes
                # set(regall.sub('', lowvote)) >= set('nolynch')
                if (
                    ed.eval(regall.sub('', lowvote), 'nolynch') < 3 
                    or ed.eval(regall.sub('', lowvote), 'nl') < 1):
                    yield "NO LYNCH", result_code
                    break

                # make sure player isn't asking for a votecount
                if (lowvote[:5] == 'count' and
                    len([p for p in self.lowplayers if p[:5]=='count'])==0):
                        break

                # make sure player isn't asking for a deadline extension
                if ed.eval(regall.sub('', lowvote), 'deadlineextension') < 2:
                        break
                result_code += 1

                # first check if vote is a 0char misspelling of a playername
                nearspellings = [d for d in distances if distances[d] < 1]
                if len(nearspellings) == 1:
                    yield nearspellings[0], result_code
                    break
                result_code += 1

                # second check if vote is a 1char misspelling of a playername
                nearspellings = [d for d in distances if distances[d] < 2 and len(d) > 2]
                if len(nearspellings) == 1:
                    yield nearspellings[0], result_code
                    break
                result_code += 1

                # third check if the acronym from the capitalizations in 
                # the vote match the same in a playername
                capmatches = [p for p in self.players if
                            ed.eval(regup.sub('', p).lower(),
                                    regall.sub('', lowvote)) < 1]
                if len(capmatches) == 1:
                    yield capmatches[0], result_code
                    break
                result_code += 1

                # fourth try to directly infer acronym from english divides
                acromatches = [p for p in self.players if 
                            ed.eval(self.playerabbrevs[p].lower(),
                                    regall.sub('', vote).lower()) < 1]
                if len(acromatches) == 1:
                    yield acromatches[0], result_code
                    break
                result_code += 1

                # fifth check if vote w/ len >=3 is substring of a playername
                suboccurrences = [p for p in self.lowplayers
                                if p.count(lowvote) > 0 and len(vote) >= 3]
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 6th check if vote is the shortest english-word acronym of a 
                # name with levenshtein distance threshold ranging up to 1;
                acromatches = [p for p in self.players if (ed.eval(
                    self.playerabbrevs[p].lower(),lowvote) < 2)  and (len(lowvote) > 2)]
                if len(acromatches) == 1:
                    yield acromatches[0], result_code
                    break
                result_code += 1

                # 7th check if vote is at all a substring of a playername, 
                # ignoring small votes
                suboccurrences = [p for p in self.lowplayers
                                if ((p.count(lowvote) > 0) and (len(lowvote) > 2))]
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 8th check if vote is two char misspelling of a playername
                nearspellings = [d for d in distances if distances[d] < 3]
                if len(nearspellings) == 1:
                    yield nearspellings[0], result_code
                    break
                result_code += 1

                # 9th check if vote has same capital letters as a playername
                # not caring about order
                capmatches = [p for p in self.players
                            if sorted(regup.sub('', p).lower())
                            == sorted(lowvote)]
                if len(capmatches) == 1:
                    yield capmatches[0], result_code
                    break
                result_code += 1

                # 10 check if vote's shortest english-word acronym of a name
                # with levenshtein distance threshold ranging up to 2
                acromatches = [p for p in self.players if ed.eval(
                    self.playerabbrevs[p].lower(),lowvote) < 3]
                if len(acromatches) == 1:
                    yield acromatches[0], result_code
                    break
                result_code += 1

                # 11 check if a player's name is a substring of the vote
                suboccurrences = [p for p in self.lowplayers
                                if ((lowvote.count(p) > 0) and len(p) > 1)]
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 12 if any splitted part of a playername are vote substring
                suboccurrences = [p for p in self.lowplayers if
                                len([s for s in p.split(' ')
                                    if (lowvote.count(s)> 0 and len(s) > 1)]) > 0]
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 13 if any length>3 english-divided parts of a player's name
                # are a vote substring
                suboccurrences = [p for p in self.players
                                if len([s for s in self.englishdivides[p][0]
                                        if (lowvote.count(s.lower())
                                            > 0 and len(s) > 3)]) > 0]
                if len(suboccurrences) == 1:
                    yield suboccurrences[0], result_code
                    break
                result_code += 1

                # 14 if vote is a two letter abbreviation of a playername
                # that includes partial english
                acromatches = [p for p in self.players
                            if ed.eval(''.join([each[0] for each in
                                    self.englishdivides[p][0][1:3]]).lower(),
                                        lowvote) < 1]
                if len(acromatches) == 1:
                    yield acromatches[0], result_code
                    break
                result_code += 1

                # 15 check if vote is the shortest english-word acronym of a 
                # name with levenshtein distance threshold ranging up to 1;
                # repeating 6 but not minding vote size
                acromatches = [p for p in self.players if (ed.eval(
                    self.playerabbrevs[p].lower(),lowvote) < 2)]
                if len(acromatches) == 1:
                    yield acromatches[0], result_code
                    break
                result_code += 1

                # 16 check if vote is at all a substring of a playername, 
                # no minding vote size but otherwise repeating 7
                suboccurrences = [p for p in self.lowplayers
                                if p.count(lowvote) > 0]
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 17 if vote is slightly misspelled substring of a playername
                threshold = 1
                suboccurrences = []
                for p in self.lowplayers:
                    if len(vote) < len(p):
                        for i in range(len(p)):
                            if (ed.eval(lowvote,
                                        p[i:min(i+len(vote)+1, len(p))])
                                <= threshold):
                                suboccurrences.append(p)
                                break
                        for i in range(1, len(vote)+1):
                            if (ed.eval(lowvote, p[:i]) <= threshold):
                                suboccurrences.append(p)
                                break
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 18 retry 16 with higher threshold
                threshold = 2
                suboccurrences = []
                for p in self.lowplayers:
                    if len(vote) < len(p):
                        for i in range(len(p)):
                            if (ed.eval(lowvote,
                                        p[i:min(i+len(vote)+1, len(p))])
                                <= threshold):
                                suboccurrences.append(p)
                                break
                        for i in range(1, len(vote)+1):
                            if (ed.eval(lowvote, p[:i]) <= threshold):
                                suboccurrences.append(p)
                                break
                if len(suboccurrences) == 1:
                    yield self.lowplayers[suboccurrences[0]], result_code
                    break
                result_code += 1

                # 19 if vote is mix of abbreviations/spaced playername parts
                suboccurrences = []
                for p in self.players:
                    broke = p.split(' ')
                    for i in range(len(broke)):
                        cand = ''.join([broke[j][0] if j != i else broke[j]
                                        for j in range(len(broke))])
                        if ed.eval(cand.lower(), lowvote) < 2:
                            suboccurrences.append(p)
                if len(suboccurrences) == 1:
                    yield suboccurrences[0], result_code
                    break
                result_code += 1

                # 20 if every char in vote is char in just one playername
                matches = [p for p in self.lowplayers 
                        if set(lowvote.replace(' ', '')) <= set(p)]
                if len(matches) == 1:
                    yield self.lowplayers[matches[0]], result_code
                    break
                result_code += 1
                
                # 21 redo the entire process but truncating the input up to the last space (or last char!)
                #if post:
                #    print('LAST RESORT', vote, min(distances, key=distances.get), post['number'], post['user'])
                #else:
                #    print('LAST RESORT', vote, min(distances, key=distances.get))
                if result_code > 200:
                    break

                elif vote.rfind(' ') > -1:
                    vote = vote[:vote.rfind(' ')]
                    
                else:
                    
                    min_player = min(distances, key=distances.get)
                    min_distance = distances[min_player]
                    gap = 10
                    for key, value in distances.items():
                        if key != min_player:
                            if value - min_distance < gap:
                                gap = value - min_distance

                    if self.verbose:
                        print('No match attained.')
                        print(distances)
                        print('Minimum LevDistance Player:', min_player, min_distance)
                        print('Final Result Code', result_code)


                    if (gap >= 2 and min_distance < 7) or gap > 2:
                        yield min_player, -1
                        break

                    break

                # 19 the last resort, the playername closest to the vote
                #print('LAST RESORT', vote)
                #yield min(distances, key=distances.get)