# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # VoteCount
# A class for representing and manipulating votecounts.

class VoteCount:
    
    def __init__(self, slots, meta={}):
        # each slot is assigned an index in range(len(slots)), 
        # with len(slots) equivalent to voting "UNVOTE", 
        # and len(slots)+1 equivalent to "NO LYNCH"
        # start votecount with everyone voting no one
        self.slots, self.votesByVoter, self.votesByVoted = slots, {}, {}
        for i in range(len(slots)):
            self.votesByVoter[i] = len(slots)
            self.votesByVoted[i] = []
        self.votesByVoted[len(slots)] = list(range(len(slots)))
        self.choice, self.votelog, self.meta = None, [], meta
        
    def __str__(self):
        string = ''
        for i in self.votesByVoted.keys():
            voters = [self.slots[voter] for voter in self.votesByVoted[i]]
            voted = ('Not Voting' if i == len(self.slots) else
                     ('No Lynch' if i > len(self.slots) else
                      self.slots[i]))
            string += voted + '-' + str(len(voters)) + 'votes:\n'
            for each in voters:
                string += each + '\n'
            string += '\n'
        return string[:-1]
    
    def todict(self):
        output = {}
        for i in self.votesByVoted.keys():
            voters = [self.slots[voter] for voter in self.votesByVoted[i]]
            voted = ('Not Voting' if i == len(self.slots) else
                     ('No Lynch' if i > len(self.slots) else
                      self.slots[i]))
            output[voted] = voters
        return output
        
    def update(self, voter, voted, postnumber=None):
        self.votelog.append(
            '{} voted {} in post {}'.format(voter,voted,str(postnumber)))
        
        # get voterslot and votedslot
        voterslot = next(self.slots.index(s) for s in self.slots
                         if s.count(voter) > 0)
        votedslot = (len(self.slots) if voted == 'UNVOTE' else
                     (len(self.slots)+1 if voted == 'NO LYNCH' else
                      next(self.slots.index(s) for s in self.slots
                           if s.count(voted) > 0)))
        
         # update votesByVoter, temporarily track the old vote
        oldvoted = self.votesByVoter[voterslot]
        self.votesByVoter[voterslot] = votedslot

        # update votesByVoted
        oldvoteindex = self.votesByVoted[oldvoted].index(voterslot)
        del self.votesByVoted[oldvoted][oldvoteindex]
        self.votesByVoted[votedslot].append(voterslot)
        
        # if voted has a majority of votes, mark as voters' choice
        if votedslot < len(self.slots) or votedslot == len(self.slots)+1:
            if len(self.votesByVoted[votedslot]) > len(self.slots)/2.0:
                self.choice = (self.slots[votedslot]
                               if votedslot < len(self.slots)
                               else 'NO LYNCH')
