import string

# for simplifying text to just numbers
no_punctuation = str.maketrans(string.punctuation+string.ascii_letters, ' '*len(string.punctuation+string.ascii_letters))


# open transitions archive, convert into dictionary of lists
with open('data/transitions.tsv') as f:
    transitions = f.read()
transitions = transitions.split('\n')[3:]
transitions = {line.split(
    '\t')[0]:line.strip().split('\t')[1:] for line in transitions if len(line.strip().split('\t')[1:]) > 0}


def relevantGameInfo(game, include_factions=False):
    
    # link
    link = game[:game.find('\n')]
    
    # thread number
    number = (link[link.find('&t=')+3:] if link.count('&')==1 
                      else link[link.find('&t=')+3:link.rfind('&')])

    # special events
    lessOneForMislynch, events, notes = False, {}, game[:game.find('\n\n')].split('\n')[-1][len("Notes: "):]
    for note in notes.split('; '):
        note = note.replace(' in post ', ' on post ')
        if ' on post ' in note:
            postnumber = note.split(' on post ')[1].replace(';', '')
            postnumber = postnumber[:postnumber.find(' but')] if 'but' in postnumber else postnumber
            if postnumber in events:
                events[postnumber].append(note.split(' on post ')[0])
            else:
                events[postnumber] = [note.split(' on post ')[0]]
        elif 'one less for no lynch' in note.lower():
            lessOneForMislynch = True
    
    # game title and number
    title = game.split('\n')[1]
    title_number = [i for i in title.translate(no_punctuation).split() if i.isdigit()][0]
    
    # moderator(s)
    moderators = game.split('\n')[2][len('Moderator: '):].split(', ')
    
    # living slots/players for each Day
    doublevoters = []
    slots, players, fates, lynched, factions = [], [], [], {}, {}
    for line in game[game.find('\nPlayers\n')+9:].split('\n'):
        line = line.split(', ')
        
        # build list of players and slots
        players += line[0].split(' replaced ')
        slots.append(line[0].split(' replaced ')) 
        
        # extract role and check for doublevoter
        if 'double voter' in line[1].lower() or 'doublevoter' in line[1].lower():
            doublevoters.append(line[0].split(' replaced '))

        # 
        if 'town' in line[1].lower():
            factions[str(slots[-1])] = 'TOWN'
        elif 'serial' in line[1].lower() or 'third party' in line[1].lower():
            factions[str(slots[-1])] = 'OTHER'
        elif 'werewolf' in line[1].lower() or 'mafia' in line[1].lower():
            factions[str(slots[-1])] = 'MAFIA'
        else:
            print(line[1].lower())
        
        # extract last phase slot's vote helped decide Day
        # it's the phase they died, minus one if they were day-killed (not lynched)
        if 'survived' in line[-1].lower() or 'endgamed' in line[-1].lower():
            fates.append(float('inf'))
        else:
            phase = int(line[-1][line[-1].rfind(' ')+1:])
            #fate_modifier = 'killed day' in line[-1][:line[-1].rfind(' ')].lower() 
            fates.append(max(0, phase))
        
        # sort any detected lynches into `lynched` array
        if 'lynched' in line[-1].lower():
            lynched[phase] = slots[-1]
    if not include_factions:
        return slots, players, fates, lynched, number, transitions[title_number], moderators, events, doublevoters, lessOneForMislynch
    else:
        return slots, players, fates, lynched, factions, number, transitions[title_number], moderators, events, doublevoters, lessOneForMislynch