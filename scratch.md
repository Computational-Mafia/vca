# New Issues
- ?? explore rejecting at final step by some threshold
- ?? explore search for votes in longer lines - perhaps in first several words
- ?? explore snipping long votes or otherwise inferring votes on basis of initial text
- Accept nested urls/votes
- Reject bold votes in weird colors
- accept nested fieldtags/votes
- support nickname notes
- individually investigate every acronym/subset/nearspelling error individually
- note support for replacements

## Patterns in Votecounter Errors
### Potentially too aggressive at assigning votes (Fake votes and/or for non-near players not sorted as those)
In general, I'd rather votes be assigned to the closest guy even if there is no near match. But there are some cases w/ broad import that I can explicitly handle. I will reject votes w/o content. And I will explore the possibility of rejecting "far" matches. Perhaps include an confidence metric in votecounter? That'd handle deliberate ambiguity, too. It's not designed to work that way though...

#### Voting the moderator
https://forum.mafiascum.net/viewtopic.php?f=53&t=15982
Game 1107: Just a Game
Moderator: Tasky
Current Update: Town Win
Notes: D1; ICEninja voted UNVOTE in post 18 but also did a fakevote "[b]Vote Tasky[/b]"for moderator that got interpreted as one for Riceballtail; D3 no lynch; one less for NO LYNCH; 

#### Voting dead slots
I have to exclude dead slots (and ambivalently wish I could exclude replaced slots) for votecounter to have increased accuracy as games proceed.

https://forum.mafiascum.net/viewtopic.php?f=53&t=15828
Game 1098: The Mafia Experiment!
Moderator: el simo
Current Update: Town Win
Notes: D3 toolfail; Shattered Viewpoint tried to vote Scott Brosius in post 602 but Scott Brosius was dead so my votecounter interpreted "[b]Vote: ScottBro[/b]" a vote for Amor

https://forum.mafiascum.net/viewtopic.php?f=53&t=25357
Game 1414: Mafia and Werewolves
Moderator: rapidcanyon
Current Update: Town Win
Notes: D5; toolfail; JacobSavage did not vote on post 772 but votecounter interpreted "[vote]Revenus[/vote]" (a dead slot) as for YOLO

https://forum.mafiascum.net/viewtopic.php?f=53&t=15787
Game 1091: Mafia Mania
Moderator: Nobody Special
Current Update: Mafia Win
Notes: D2 toolfail; boberz did not vote boberz in post 484 but votecounter interpreted vote for dead player "[b]vote beefster[/b]" as vote for SOMEONE_ELSE

#### Fake votes and Catastrophic Failures
The problem with being aggressive is that fake votes will be assigned to faraway players and distort everything. Can I set some sort of threshold? How are these votes being assigned?

https://forum.mafiascum.net/viewtopic.php?f=53&t=18412
Game 1207: LIPD Mafia
Moderator: AurorusVox
Current Update: Town Win
Notes: D5; Slaxx did not vote in post 1117 but moderator was being silly; Hoppster did not vote in post 1118 but moderator was being silly; Hinduragi did not vote in post 1165 but moderator was being silly; 

https://forum.mafiascum.net/viewtopic.php?f=53&t=18952
Game 1234: Masquerade Mafia
Moderator: Mute
Current Update: Mafia Win
Notes: D3 toolfail; Whiskers did not vote in post 1164 but my votecounter interpreted "Vote: Mi--" in pink font as a vote for ['Mist Beauty', 'Guthrie']; D4 toolfail; Whiskers did not vote in post 1602 but my votecounter interpreted "Vote: Friendship" in bold/purple font as a vote for GLaDOS; Whiskers voted Charlie in post 1614 but votecounter interpreted "[b]Mein Vӧttenhammer: Charlie[/b]" as not a vote at all

https://forum.mafiascum.net/viewtopic.php?f=53&t=69859
Mini 1866: Landmark Mafia
Moderator: BigYoshiFan
Current Update: Mafia Win
Notes: D3; Pepchoninga voted Pepchoninga in post 3154 but votecounter interpreted "[vote]THE ALL MIGHTY GOD OF GODS (me)[/vote]" as for Elena Fisher; toolfail

#### Deliberate Ambiguity
This seems rare enough that I'll be fine - but it's definitely a problem for the votecounter. If evidence for two players are equal, a mod will reject it and I should reject it. But when it is ever really equal? Rarely, I bet.

https://forum.mafiascum.net/viewtopic.php?f=53&t=62909
Mini 1705
Moderator: Not_Mafia
Current Update: Mafia Win
Notes: D3; toolfail; SamX did not vote in post 1218 but "[vote]KLINGAMENCE[/vote]" and "[vote]SALONCELT[/vote]" were interpreted as votes for Klingoncelt and Salamence20

https://forum.mafiascum.net/viewtopic.php?f=53&t=37632
Mini 1544: Dry, Bland and Tasteless
Moderator: caledfwitch
Current Update: Town Win
Notes: D2 toolfail; Zekrom tried to vote "[b]Vote: Rainbowdash / or / Nikanor[/b]" in post 362 but the moderator did not count it and my votecounter extracted a vote for Rainbowdash

### Mods are at least occasionally more conservative than votecounter
Do they have a point? It's a tough thing to test. But this kind of reaches back to whether I want the votecounter to be maximally aggressive or not. I want the limit to be "This is definitely an attempt at a vote". These "errors" are cases where the mod rejected an obvious vote attempt because rules. We'll track attempts and mod rejections when they result in votecountertest failures or we come across them by chance.

#### Many Examples
https://forum.mafiascum.net/viewtopic.php?f=53&t=17276
Game 1157: Witch-Hunt Nightless
Moderator: Ythan
Current Update: Town Win
Notes: D2 No Majority; D8 Slaxx tried to vote Slaxx in post 1150 but while voteextractor interpreted "[b]vote:slaxx[\b]" correctly the mod rejected its formatting; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=17606
Game 1177: Normal Game
Moderator: Bunnylover
Current Update: Town Win
Notes: D1; LittleGrey voted jilynne1991 in post 597 but LittleGrey mistakenly typed "Jelly" (indicating petroleumjelly) and corrected it in their successive post; toolfail; Slaxx tried to vote E_Lou_Sive in post 586 but moderator rejected "[b] vote elusive[\b]" as a valid vote

https://forum.mafiascum.net/viewtopic.php?f=53&t=21340
Game 1317
Moderator: kdowns
Current Update: Mafia Win
Notes: D2; hokorippoi tried to vote thezmon221 in post 637 but moderator did not accept it as the format did not follow rules; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=27042
Game 1440: Unoriginal Mafia
Moderator: Phenenas
Current Update: Town Win
Notes: D3; toolfail; Bomberman tried to vote Nero in post 705 but because he voted 3 other slots first the moderator did not count the vote even though votecounter interpreted each vote as valid

https://forum.mafiascum.net/viewtopic.php?f=53&t=31972
Game 1505: N is for Normal
Moderator: N
Current Update: Mafia Win
Notes: D4 no lynch; D5; Garmr tried to vote Garmr in post 1304 but since it was not on its own line the mod discounted it;

https://forum.mafiascum.net/viewtopic.php?f=53&t=66258
Mini 1787: Peruvian Nightclub Mafia
Moderator: Zulfy
Current Update: Town Win
Notes: D2; toolfail; Zachstralkita tried to vote Floof in post 1523 but moderator refused to count the vote as the player had been replaced; Desmond_13 tried to vote zakk in post 1439 but the mod refused to count the vote as the player had been replaced

https://forum.mafiascum.net/viewtopic.php?f=53&t=66300
Mini 1789: Puppy Mafia!
Moderator: UpTooLate
Current Update: Mafia Win
Notes: D1; Trivium tried to vote Zulfy in post 691 but the moderator did not count it as it did not occur on its own line; toolfail

### Including a comment inside vote can prevent vote detection
Searching for votes far from the start of a line is risky and could reduce performance. However, it should be explored, sure.

It's hard to think of a smart way to handle long comments that doesn't have bad side effects, too. I can see if there's a cost to just snipping everything after some limit - as well as if that actually fixes the problem.

#### No vote detected
https://forum.mafiascum.net/viewtopic.php?f=53&t=16769
Game 1133: Mafia in Venice
Moderator: lewarcher82
Current Update: Mafia Win
Notes: D5; ICEninja voted RedCoyote in post 489 but votecounter extracted no vote from "[b]Cross fingers, vote RedCoyote.[/b]"; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=61419
mini 1662: Paint the village red
Moderator: kelbris, N
Current Update: Town Win
Notes: D4; PeaceBringer voted Unlynchable in post 1019 but votecounter interpreted "[b]Hammer vote unlynchable....[/b]" as not a vote; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=67069
Mini 1805
Moderator: Sméagol
Current Update: Mafia Win
Notes: D2; Eggman voted MarioManiac4 in post 1426 but votecounter did not interpret "[b]FoS: Dragon, Vote: MM4[/b]" as a vote

#### Difficulty identifying target
https://forum.mafiascum.net/viewtopic.php?f=53&t=22206
Game 1341
Moderator: Jackal711
Current Update: Mafia Win
Notes: Shattered Viewpoint is a doublevoter but allowed to distribute just one vote; D2; toolfail; Shattered Viewpoint voted Pine in post 429 but "[b]Vote: Pine -- Mod, please note this is only one vote, thanks.[/b]" was detected as a vote for Junpei; transition prediction failure due to unpredictable distribution

https://forum.mafiascum.net/viewtopic.php?f=53&t=31636
Game 1501: We're On A Boat
Moderator: pitoli
Current Update: Serial Killer Win
Notes: D2; toolfail; notscience voted SleepyKrew in post 1219 but votecounter extracted "[vote]SKs slot because I can't check OP atm[/vote]" as for notscience

### Inconsistent handling of nested tags
We should accept votes within fieldset tags and that overlap with URLs. But by my intuition, if the font is a different color bold text shouldn't be a vote. How much do I gain from working on this?

#### Examples
https://forum.mafiascum.net/viewtopic.php?f=53&t=16852
Game 1140: Mafia Mishmash
Moderator: havingfitz
Current Update: Mafia Win
Notes: D2 toolfail; Haylen voted andrew94 in post 803 but typed [b]Vote Andrew[/b] within a fieldset tag

https://forum.mafiascum.net/viewtopic.php?f=53&t=18952
Game 1234: Masquerade Mafia
Moderator: Mute
Current Update: Mafia Win
Notes: D3 toolfail; Whiskers did not vote in post 1164 but my votecounter interpreted "Vote: Mi--" in pink font as a vote for ['Mist Beauty', 'Guthrie']; D4 toolfail; Whiskers did not vote in post 1602 but my votecounter interpreted "Vote: Friendship" in bold/purple font as a vote for GLaDOS; Whiskers voted Charlie in post 1614 but votecounter interpreted "[b]Mein Vӧttenhammer: Charlie[/b]" as not a vote at all

https://forum.mafiascum.net/viewtopic.php?f=53&t=24645
Game 1407
Moderator: Cheery Dog
Current Update: Mafia Win
Notes: D4; havingfitz voted projectmatt in post 1008 but used vote tag and url tag at the same time so votecounter disregarded it; toolfail;

LAST RESORT s on totally separate lines from now on. SodaSpirit17 26 yabbaguy
LAST RESORT s on totally separate lines from now SodaSpirit17
LAST RESORT s on totally separate lines from SodaSpirit17
LAST RESORT s on totally separate lines SodaSpirit17
LAST RESORT s on totally separate SodaSpirit17
LAST RESORT s on totally Konowa
LAST RESORT s on RXK
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=22625
Game 1354: Vedere le Viste!
Moderator: Phillammon
Current Update: Town Win

### Idiosyncracies Potentially Beyond Capacity of Votecounter to Handle
Some of these I just can't handle broadly. But I might benefit from a broader NOTE strategy - nickname assignment instead of just post-by-post vote assignment. Gotta be careful not to let that get used to paper over bad votecounter code, though.

#### Nicknames
https://forum.mafiascum.net/viewtopic.php?f=53&t=69937
Mini 1870
Moderator: Sickofit1138
Current Update: Town Win
Notes: D2 toolfail; D2 players voting "Mudkip" to indicate XnadrojX based on his avatar in post 2259 for example

https://forum.mafiascum.net/viewtopic.php?f=53&t=64070
Mini 1735: Radjarok 2
Moderator: Radja
Current Update: Mafia Win
Notes: D1 toolfail; pisskop voted BlockyMan in post 129 but my votecounter detects "vote rikky6" as a vote for pisskop; D2 toolfail; RadiantCowbells voted TheCow in post 351 but votecounter interpreted "[vote]Cow[/vote]" as for ceasor; Frozen Angel voted TheCow in post 355 but votecounter interpreted "[vote]Cow[/vote]" as for ceasor

#### Probably Not a Nickname
https://forum.mafiascum.net/viewtopic.php?f=53&t=69859
Mini 1866: Landmark Mafia
Moderator: BigYoshiFan
Current Update: Mafia Win
Notes: D3; Pepchoninga voted Pepchoninga in post 3154 but votecounter interpreted "[vote]THE ALL MIGHTY GOD OF GODS (me)[/vote]" as for Elena Fisher; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=23772
Game 1390
Moderator: nhammen
Current Update: Town Win
Notes: D2; toolfail; JacobSavage voted Kinetic in post 1217 but my votecounter extracted "[vote]VOTE: (mv^2)/2[/vote]" as a vote for Thor665

https://forum.mafiascum.net/viewtopic.php?f=53&t=61070
Mini 1655: Delicious Mafia
Moderator: Aeronaut
Current Update: Mafia Win
Notes: D2; House voted tn5421 in post 2479 but typed "[vote]zipcode[/vote]" which my votecounter interpreted as a vote for T S O; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=62781
Mini 1701 - Modified Werewolf 13er
Moderator: Shinobi
Current Update: Werewolf Win
Notes: D6 no lynch; toolfail; Doctor Who voted NO LYNCH in post 1663 but votecounter interpreted "[vote]pass[/vote]" as a vote for redFF;

https://forum.mafiascum.net/viewtopic.php?f=53&t=72397
Mini Normal 1923
Moderator: Boonskiies
Current Update: Town Win
Notes: D3; Fykus voted ThinkBig in post 2940 but votecounter interpreted "[vote]teebs[/vote]" as for Assemblerotws

#### Quirky Vote Assignment
https://forum.mafiascum.net/viewtopic.php?f=53&t=17606
Game 1177: Normal Game
Moderator: Bunnylover
Current Update: Town Win
Notes: D1; LittleGrey voted jilynne1991 in post 597 but LittleGrey mistakenly typed "Jelly" (indicating petroleumjelly) and corrected it in their successive post; toolfail; Slaxx tried to vote E_Lou_Sive in post 586 but moderator rejected "[b] vote elusive[\b]" as a valid vote

https://forum.mafiascum.net/viewtopic.php?f=53&t=18952
Game 1234: Masquerade Mafia
Moderator: Mute
Current Update: Mafia Win
Notes: D3 toolfail; Whiskers did not vote in post 1164 but my votecounter interpreted "Vote: Mi--" in pink font as a vote for ['Mist Beauty', 'Guthrie']; D4 toolfail; Whiskers did not vote in post 1602 but my votecounter interpreted "Vote: Friendship" in bold/purple font as a vote for GLaDOS; Whiskers voted Charlie in post 1614 but votecounter interpreted "[b]Mein Vӧttenhammer: Charlie[/b]" as not a vote at all

https://forum.mafiascum.net/viewtopic.php?f=53&t=48071
Mini 1569: The Golden Cookie Heist!
Moderator: Kalimar
Current Update: Town Win
Notes: D1; kushm4sta voted vonflare in post 306 but he typed "whateverthisdudesnameis" in a post quoting vonflare and my votecounter failed; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=22900
Game 1361: Rainy Days Mafia
Moderator: Midnight's Sorrow
Current Update: Town Win
Notes: D2; charter did not vote yabbaguy in post 560 but my votecounter extracted it from "[b]VigVote Yabba[/b]"; toolfail; charter voted deadjoker in post 560 but the above note negates it on its own;

#### Strange Setup Choices
https://forum.mafiascum.net/viewtopic.php?f=53&t=63492
MINI 1721
Moderator: Marquis
Current Update: Mafia Win
Notes: Two players are lynched per Day

https://forum.mafiascum.net/viewtopic.php?f=53&t=18683
Game 1216: S.M.H. (A.S.N.P.T.) Mafia
Moderator: Ant_to_the_max
Current Update: Mafia Win
Notes: D4; (6 + 0(odd: false)) / 2 = 3 rule for hammers; 

### Doublevoters with flexible assignment
I will probably just filter out games with doublevoters.

#### Examples
https://forum.mafiascum.net/viewtopic.php?f=53&t=18920
Game 1230: Xylbot is Normal I Swear
Moderator: Cojin
Current Update: Mafia Win
Notes: Missing Posts; D1; Jackal711 is a doublevoter who can put votes on different people

https://forum.mafiascum.net/viewtopic.php?f=53&t=22206
Game 1341
Moderator: Jackal711
Current Update: Mafia Win
Notes: Shattered Viewpoint is a doublevoter but allowed to distribute just one vote; D2; toolfail; Shattered Viewpoint voted Pine in post 429 but "[b]Vote: Pine -- Mod, please note this is only one vote, thanks.[/b]" was detected as a vote for Junpei; transition prediction failure due to unpredictable distribution

https://forum.mafiascum.net/viewtopic.php?f=53&t=58162
Mini 1582: Formerfish's First Foray
Moderator: Formerfish
Current Update: Town Win
Notes: D2; doublevoter controls each vote individually;

### Extremely Bad/Nonexistent Tags
If I were the mod, I wouldn't accept any of these votes. I'll just use NOTES for these. The case of borked quote tags is troublesome, but that's uncommon enough that I doubt I need special code for that either.

#### Notes
https://forum.mafiascum.net/viewtopic.php?f=53&t=28250
Game 1449: Ordinary Town
Moderator: qwints
Current Update: Town Win
Notes: D1; Dessx voted UNVOTE in post 567 but he did not bold the tag and my votecounter did not detect it; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=33249
Mini 1517 - The Sun Sets on Duskville
Moderator: Alduskkel
Current Update: Mafia Win
Notes: D2; Sir Bastion did not vote Haschel Cedricson in post 1565 but my votecounter detected "[b]Unvote, vote HC[b][/quote" as a vote for Haschel Cedricson; toolfail

https://forum.mafiascum.net/viewtopic.php?f=53&t=58383
Mini 1589: The Train of Death
Moderator: Aronis
Current Update: Mafia Win
Notes: D1; votecount reset on post 82; xfdagentx42 killed on post 82; TheNoggyOne voted Espressojet on post 205 but did not include tags and mod counted it anyway;

### Bad Abbreviation Handling
Each of these will have to be investigated carefully.

#### Acronyms
https://forum.mafiascum.net/viewtopic.php?f=53&t=72324
Mini Normal 1921
Moderator: Alchemist21
Current Update: Town Win
Notes: D6; Creature voted projectmatt in post 4763 but votecounter interpreted "[vote]pjm[/vote]" as a vote for pamda

https://forum.mafiascum.net/viewtopic.php?f=53&t=28649
Game 1456: Revenge
Moderator: SoraAdvent, Rob14
Current Update: Mafia Win
Notes: D2 no majority; D5; toolfail; Majiffy voted mario and lugi in post 1111 but votecounter interpreted "[vote]M&L[/vote]" as for Elyse

https://forum.mafiascum.net/viewtopic.php?f=53&t=66377
Mini 1791: Mildly Dangerous Mafia
Moderator: Postie
Current Update: Town Win
Notes: D1 toolfail; Asphodel voted heuristically_alone in post 1268 but "ha" was detected as Bellaphant instead of heuristically_alone; Dwlee99 voted heuristically_alone in post 1266 but "Ha" was detected as Bellaphant instead of heuristically_alone; RadiantCowbells voted heuristically_alone in post 1263 but "ha" was detected as Bellaphant instead of heuristically_alone; Bellaphant voted heuristically_alone in post 1257 but "ha" was detected as Bellaphant instead of heuristically_alone; 

https://forum.mafiascum.net/viewtopic.php?f=53&t=68980
Mini Normal 1848
Moderator: keyenpeydee
Current Update: Town Win
Notes: D3 toolfail; MortFeld voted Road Kamelot in post 2920 but votecounter interpreted "[vote]RK[/vote]" as vote for rb; Shadow_step voted Road Kamelot in post 2916 but votecounter interpreted "[vote]RK[/vote]" as vote for rb; Naomi-Tan voted Road Kamelot in post 2899 but votecounter interpreted "[vote]RK[/vote]" as vote for rb; D4 toolfail; Naomi-Tan did not vote DeathByWobbuffet in post 3012 but "[b]Vote: To have nights end as soon as all active abilities have been submitted or two days have past[/b]" got interpreted as one; rb voted Nero Cain in post 3188 but only because moderator miscounted or posts are missing;

#### Subset
https://forum.mafiascum.net/viewtopic.php?f=53&t=64070
Mini 1735: Radjarok 2
Moderator: Radja
Current Update: Mafia Win
Notes: D1 toolfail; pisskop voted BlockyMan in post 129 but my votecounter detects "vote rikky6" as a vote for pisskop; D2 toolfail; RadiantCowbells voted TheCow in post 351 but votecounter interpreted "[vote]Cow[/vote]" as for ceasor; Frozen Angel voted TheCow in post 355 but votecounter interpreted "[vote]Cow[/vote]" as for ceasor

https://forum.mafiascum.net/viewtopic.php?f=53&t=64784
Mini 1752: Back to December
Moderator: Equinox
Current Update: Town Win
Notes: D2 toolfail; curiouskarmadog voted Aj The Epic in post 530 but votecounter interpreted "[b]vote AJ[/b]" as for Alchemist21; Xtoxm voted Aj The Epic in post 447 but votecounter interpreted "[b]vote Aj[/b]" as for Alchemist21; Raskolnikov voted Aj The Epic in post 434 but votecounter interpreted "[vote]AJ[/vote]" as for Alchemist21; 

https://forum.mafiascum.net/viewtopic.php?f=53&t=69244
Mini 1854
Moderator: Dierfire
Current Update: Town Win
Notes: D3 toolfail; Aj The Epic; D4 toolfail; Lil Uzi Vert didn't vote Joshz in post 2436 but votecounter extracted a vote for Joshz from "[vote][/vote]"

https://forum.mafiascum.net/viewtopic.php?f=53&t=69502
Mini 1861: Musical Mafia
Moderator: Gamma Emerald, mhsmith0
Current Update: Town Win
Notes: D3; Aj the Epic

### Bad Nearspelling Handling
Each of these will have to be investigated carefully.

#### Examples
https://forum.mafiascum.net/viewtopic.php?f=53&t=32114
Mini 1509 - Marriage in Mafiatown
Moderator: Tierce, notscience
Current Update: Mafia Win
Notes: D3; toolfail; JKLM voted redtail896 in post 969 but votecounter interpreted "[vote]red tail[/vote]" as a vote for I Am Innocent; D5 no lynch; one less for no lynch

https://forum.mafiascum.net/viewtopic.php?f=53&t=68519
Mini 1836: Space Mafia
Moderator: Something_Smart, Aristophanes
Current Update: Town Win
Notes: D1 no majority; D2 no majority; D5; TwoFace voted Xkfyu in post 3231 but votecounter interpreted "[vote]xf[/vote]" as for TwoFace

https://forum.mafiascum.net/viewtopic.php?f=53&t=39665
Mini 1556: Greetings Without Spain
Moderator: Bicephalous Bob
Current Update: Mafia Win
Notes: D3; Rubicon voted evilpacman18 in post 893 but my votecounter detected "[vote]epicpacman[/vote]" as a vote for N

https://forum.mafiascum.net/viewtopic.php?f=53&t=57502
Mini 1579: The Great Flavor Caper
Moderator: phokdapolees
Current Update: Mafia Win
Notes: D1 long twilight; votecount reset on post 1250; D2; Sharpest-knife-on-tree voted Slandaar in post 1375 but votecounter interpreted "[b]vote saalndar[/b]" as vote for T S O; D3; T S O killed on post 1534;

https://forum.mafiascum.net/viewtopic.php?f=53&t=62181
Mini 1687: Refraction Mafia
Moderator: Aeronaut
Current Update: Werewolf Win
Notes: D2; toolfail; Lapsa voted RadiantCowbells in post 1931 but votecounter interpreted "[vote]DullBellcows[/vote]" as a vote for toolenduso

### Difficult Ambiguity Due to Player Replacement
This issue seems isolated to one game, but it might ruin processing of that game. Handling it easy in principle (NOTE REPLACEMENTS!) but potentially not worth it.

https://forum.mafiascum.net/viewtopic.php?f=53&t=41311
Mini 1560 - Reck's Walk of Shame
Moderator: xRECKONERx
Current Update: Town Win
Notes: D1; Slandaar voted CooLDoG in post 730 but my votecounter assigned "[vote]CD[/vote]" to ChannelDelibird (who had been replaced); toolfail

## LAST RESORT ERRORS

### VOTE FOR DEAD PLAYER (MORE EXAMPLES ABOVE)
LAST RESORT Maxwell monk 969 tarsonisocelot
LAST RESORT Maxwel monk
LAST RESORT Maxwe monk
LAST RESORT Maxw monk
LAST RESORT Max monk
LAST RESORT Ma monk
2
https://forum.mafiascum.net/viewtopic.php?f=53&t=18952
Game 1234: Masquerade Mafia
Moderator: Mute
Current Update: Mafia Win
Notes: D3 toolfail; Whiskers did not vote in post 1164 but my votecounter interpreted "Vote: Mi--" in pink font as a vote for ['Mist Beauty', 'Guthrie']; D4 toolfail; Whiskers did not vote in post 1602 but my votecounter interpreted "Vote: Friendship" in bold/purple font as a vote for GLaDOS; Whiskers voted Charlie in post 1614 but votecounter interpreted "[b]Mein Vӧttenhammer: Charlie[/b]" as not a vote at all

LAST RESORT TheTrollie Maestro 1141 havingfitz
LAST RESORT TheTrolli Maestro
LAST RESORT TheTroll Maestro
LAST RESORT TheTrol Maestro
LAST RESORT TheTro Maestro
LAST RESORT TheTr Kimor
LAST RESORT TheT Pine
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=23438
Game 1379
Moderator: MattP
Current Update: Mafia Win

### VOTE FOR MOD
https://forum.mafiascum.net/viewtopic.php?f=53&t=16263
Game 1121: Nexusville Mafia
Moderator: Nexus
Current Update: Mafia Win

https://forum.mafiascum.net/viewtopic.php?f=53&t=16813
Game 1137: Long Overdue Mafia
Moderator: Rhinox
Current Update: Mafia win

LAST RESORT ythan Kise 116 Kise
LAST RESORT ytha Kise
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17276
Game 1157: Witch-Hunt Nightless
Moderator: Ythan
Current Update: Town Win
Notes: D2 No Majority; D8 Slaxx tried to vote Slaxx in post 1150 but while voteextractor interpreted "[b] vote:slaxx[\b]" correctly the mod rejected its formatting; toolfail

### VOTE "ANALYSIS"
Game 1122

### Fuck RVS?
LAST RESORT Fuck RVS Beck 21 chkflip
LAST RESORT Bezu/Jily Bezukhov 451 Internet Stranger
LAST RESORT Bezu/Jil Bezukhov
LAST RESORT Bezu/Ji Bezukhov
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17606
Game 1177: Normal Game
Moderator: Bunnylover
Current Update: Town Win
Notes: D1; LittleGrey voted jilynne1991 in post 597 but LittleGrey mistakenly typed "Jelly" (indicating petroleumjelly) and corrected it in their successive post; toolfail; Slaxx tried to vote E_Lou_Sive in post 586 but moderator rejected "[b] vote elusive[\b]" as a valid vote

### HAPPILY EVER AFTER
LAST RESORT happily ever after The Rufflig 891 Occult
LAST RESORT happily ever Hero764
LAST RESORT happily Hero764
LAST RESORT happil Hero764
LAST RESORT happi Hero764
LAST RESORT happ Hero764
LAST RESORT hap Hero764
5
https://forum.mafiascum.net/viewtopic.php?f=53&t=17173
Game 1152
Moderator: Me=Weird
Current Update: Draw
Notes: D3 no majority; D5 no lynch; Occult tried to vote NO LYNCH in post 889 but moderator ignored it; D6 no lynch; one less for no lynch

### ABANDON GAME
LAST RESORT abandon game RandomActs 521 bionicchop2
LAST RESORT abandon benoni
2
https://forum.mafiascum.net/viewtopic.php?f=53&t=18920
Game 1230: Xylbot is Normal I Swear
Moderator: Cojin
Current Update: Mafia Win
Notes: Missing Posts; D1; Jackal711 is a doublevoter who can put votes on different people

### OLD METHOD WORKED (UNSURE IF NEW METHOD FAILED)
LAST RESORT BGGscum bgg1996 693 CryMeARiver
LAST RESORT BGGscu bgg1996
2
https://forum.mafiascum.net/viewtopic.php?f=53&t=16852
Game 1140: Mafia Mishmash
Moderator: havingfitz
Current Update: Mafia Win
Notes: D2 toolfail; Haylen voted andrew94 in post 803 but typed [b]Vote Andrew[/b] within a fieldset tag

LAST RESORT StrangerouCancergeron. Surprise_Carcinogen 41 populartajo
LAST RESORT StrangerouCancergeron Surprise_Carcinogen
LAST RESORT StrangerouCancergero Surprise_Carcinogen
LAST RESORT StrangerouCancerger Surprise_Carcinogen
LAST RESORT StrangerouCancerge Surprise_Carcinogen
LAST RESORT StrangerouCancerg DeathRowKitty
LAST RESORT StrangerouCancer DeathRowKitty
LAST RESORT StrangerouCance DeathRowKitty
LAST RESORT StrangerouCanc Parama
LAST RESORT StrangerouCan Parama
LAST RESORT StrangerouCa Parama
LAST RESORT StrangerouC Pine
LAST RESORT Strangerou Pine
LAST RESORT Strangero Pine
LAST RESORT Stranger Pine
LAST RESORT Strange Pine
LAST RESORT Strang Parama
LAST RESORT Stran GMan
LAST RESORT Stra Pine
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=16918
Game 1142: Quintessentially English Mafia
Moderator: ChannelDelibird
Current Update: Town Win

LAST RESORT [L] (L-1) -L- 287 imaginality
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17289
Game 1159: Powerrox93's Mini Normal I
Moderator: Powerrox93
Current Update: Town Win

LAST RESORT Hopitty Hoppster 420 SleepyKrew
LAST RESORT Hopitt Thomith
LAST RESORT Hopit Thomith
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17792
Game 1190: A Day in the Life
Moderator: Twistedspoon
Current Update: Town Win
Notes: D2 no majority

LAST RESORT ice ice baby ICEninja 1494 Beck
4
https://forum.mafiascum.net/viewtopic.php?f=53&t=17864
Game 1195: The Beehive Mystery
Moderator: Klazam
Current Update: Mafia Win
Notes: D5 no lynch; toolfail; Scott Brosius voted NO LYNCH in post 1503 but votecounter interpreted "[b]Vote: No-lynch.[/b]" as vote for Sotty7

LAST RESORT Malps malpascp 200 Swiftstrike
LAST RESORT Malps malpascp 204 smallpeoples343
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17940
Game 1199: Plissken's Pit
Moderator: SnakePlissken
Current Update: Mafia Win
Notes: D3 no majority

LAST RESORT hitogashi hitogoroshi 191 killerX029
LAST RESORT hitogash hitogoroshi
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=18983
Game 1236: Classic Mafia
Moderator: wierdalexv
Current Update: Mafia Win

LAST RESORT abstaaaa absta101 143 Peabody
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=22900
Game 1361: Rainy Days Mafia
Moderator: Midnight's Sorrow
Current Update: Town Win
Notes: D2; charter did not vote yabbaguy in post 560 but my votecounter extracted it from "[b]VigVote Yabba[/b]"; toolfail; charter voted deadjoker in post 560 but the above note negates it on its own;

LAST RESORT Stephan StefanB 599 Zoroaster
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=23503
Game 1382: The Mystery at Village Lake
Moderator: Zar
Current Update: Town Win

LAST RESORT sland /[b] Slandaar 1579 kwll
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=23772
Game 1390
Moderator: nhammen
Current Update: Town Win
Notes: D2; toolfail; JacobSavage voted Kinetic in post 1217 but my votecounter extracted "[vote]VOTE: (mv^2)/2[/vote]" as a vote for Thor665


LAST RESORT They May Take Our Lives But They Will Never Take Our Freedom TMTOLBTWNTOF 20 BROseidon
LAST RESORT They May Take Our Lives But They Will Never Take Our TMTOLBTWNTOF
LAST RESORT They May Take Our Lives But They Will Never Take TMTOLBTWNTOF
LAST RESORT They May Take Our Lives But They Will Never TMTOLBTWNTOF
LAST RESORT They May Take Our Lives But They Will TMTOLBTWNTOF
LAST RESORT They May Take Our Lives But They TMTOLBTWNTOF
LAST RESORT They May Take Our Lives But RadiantCowbells
LAST RESORT They May Take Our Lives RadiantCowbells
LAST RESORT They May Take Our Does Bo Know
LAST RESORT They May Take ThAdmiral
LAST RESORT They May ThAdmiral
LAST RESORT They Yates
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=28480
Game 1452: Inevitable Mafia
Moderator: Kitoari
Current Update: Town Win

### OLD METHOD INSUFFICIENT?
LAST RESORT ICEpick Beck 1264 Whiskers
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=17864
Game 1195: The Beehive Mystery
Moderator: Klazam
Current Update: Mafia Win
Notes: D5 no lynch; toolfail; Scott Brosius voted NO LYNCH in post 1503 but votecounter interpreted "[b]Vote: No-lynch.[/b]" as vote for Sotty7

LAST RESORT DBK/b] baboon 451 baboon
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=18287
Game 1204: Generic Mafia
Moderator: theplague42
Current Update: Mafia Win
Notes: D3 long twilight

LAST RESORT LLD--that's a hammer AlmasterGM 201 mastin2
LAST RESORT LLD--that's a AlmasterGM
LAST RESORT LLD--that's AlmasterGM
LAST RESORT LLD--that' AlmasterGM
LAST RESORT LLD--that mastin2
LAST RESORT LLD--tha Riddick
LAST RESORT LLD--th Riddick
LAST RESORT LLD--t Slaxx
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=18412
Game 1207: LIPD Mafia
Moderator: AurorusVox
Current Update: Town Win
Notes: D5; Slaxx did not vote in post 1117 but moderator was being silly; Hoppster did not vote in post 1118 but moderator was being silly; Hinduragi did not vote in post 1165 but moderator was being silly; 

LAST RESORT IS hiplop 95 Bub Bidderskins
2
https://forum.mafiascum.net/viewtopic.php?f=53&t=21350
Game 1318: This Little Town
Moderator: Oversoul
Current Update: Mafia Win


### NEW METHOD FKED COMPARED TO OLD
LAST RESORT SleepyKrew WormyKrew 70 Gerhard Krause
LAST RESORT SleepyKre WormyKrew
LAST RESORT SleepyKr Soben
LAST RESORT SleepyK Soben
LAST RESORT Sleepy Soben
LAST RESORT Sleep Soben
LAST RESORT Slee Soben
LAST RESORT Sle Soben
LAST RESORT Sl Soben
LAST RESORT S Soben
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17645
Game 1180
Moderator: Substrike22
Current Update: Town Win
Notes: D1; jilynne1991 tried to UNVOTE in post 729 but the moderator ignored it(???)

LAST RESORT Hopitty Hoppster 420 SleepyKrew
LAST RESORT Hopitt Thomith
LAST RESORT Hopit Thomith
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=17792
Game 1190: A Day in the Life
Moderator: Twistedspoon
Current Update: Town Win
Notes: D2 no majority

LAST RESORT marble Llamarble 1024 Beck
LAST RESORT marbl Llamarble
LAST RESORT marb Beck
LAST RESORT marble Llamarble 1077 Beck
LAST RESORT marbl Llamarble
LAST RESORT marb Beck
2
https://forum.mafiascum.net/viewtopic.php?f=53&t=17864
Game 1195: The Beehive Mystery
Moderator: Klazam
Current Update: Mafia Win
Notes: D5 no lynch; toolfail; Scott Brosius voted NO LYNCH in post 1503 but votecounter interpreted "[b]Vote: No-lynch.[/b]" as vote for Sotty7

LAST RESORT killer killerX029 3 Parama
LAST RESORT kille killerX029
LAST RESORT kill Beck
LAST RESORT kil Beck
LAST RESORT ki Beck
LAST RESORT k Beck
LAST RESORT Killer killerX029 23 Grimmjow
LAST RESORT Kille killerX029
LAST RESORT Kill Beck
LAST RESORT Kil Beck
LAST RESORT Ki Beck
LAST RESORT K Beck
LAST RESORT killer killerX029 66 Supreme Overlord
LAST RESORT kille killerX029
LAST RESORT kill Beck
LAST RESORT kil Beck
LAST RESORT ki Beck
LAST RESORT k Beck
LAST RESORT Killer killerX029 121 charter
LAST RESORT Kille killerX029
LAST RESORT Kill Beck
LAST RESORT Kil Beck
LAST RESORT Ki Beck
LAST RESORT K Beck
LAST RESORT Killer killerX029 156 David Xanatos
LAST RESORT Kille killerX029
LAST RESORT Kill Beck
LAST RESORT Kil Beck
LAST RESORT Ki Beck
LAST RESORT K Beck
LAST RESORT Killer killerX029 165 Grimmjow
LAST RESORT Kille killerX029
LAST RESORT Kill Beck
LAST RESORT Kil Beck
LAST RESORT Ki Beck
LAST RESORT K Beck
LAST RESORT killer killerX029 173 Parama
LAST RESORT kille killerX029
LAST RESORT kill Beck
LAST RESORT kil Beck
LAST RESORT ki Beck
LAST RESORT k Beck
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=18910
Game 1227: Small Town Scumbags
Moderator: Papa Zito
Current Update: Town Win
Notes: D3 no majority; D6 no lynch

### Couldn't Investigate Yet
https://forum.mafiascum.net/viewtopic.php?f=53&t=22206
Game 1341
Moderator: Jackal711
Current Update: Mafia Win
Notes: Shattered Viewpoint is a doublevoter but allowed to distribute just one vote; D2; toolfail; Shattered Viewpoint voted Pine in post 429 but "[b]Vote: Pine -- Mod, please note this is only one vote, thanks.[/b]" was detected as a vote for Junpei; transition prediction failure due to unpredictable distribution

5
https://forum.mafiascum.net/viewtopic.php?f=53&t=25357
Game 1414: Mafia and Werewolves
Moderator: rapidcanyon
Current Update: Town Win
Notes: D5; toolfail; JacobSavage did not vote on post 772 but votecounter interpreted "[vote]Revenus[/vote]" as for YOLO


### ???
LAST RESORT ; Hi Mute 756 Empking
LAST RESORT ; Mute
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=18987
Game 1238: One After the Other
Moderator: Meransiel, Papa Zito
Current Update: Town Win
Notes: Missing Posts

LAST RESORT goddamnit monk 132 Whiskers
LAST RESORT goddamni monk
LAST RESORT goddamn monk
LAST RESORT goddam monk
LAST RESORT godda monk
LAST RESORT godd monk
LAST RESORT god monk
LAST RESORT go monk
1
https://forum.mafiascum.net/viewtopic.php?f=53&t=18987
Game 1238: One After the Other
Moderator: Meransiel, Papa Zito
Current Update: Town Win
Notes: Missing Posts

LAST RESORT ATOLAEXSTAXOSEEETETETETXEOE] Slaxx 1135 Parama
LAST RESORT ATOLAEXSTAXOSEEETETETETXEOE Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETETETXEO Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETETETXE Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETETETX Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETETET Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETETE Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETET Slaxx
LAST RESORT ATOLAEXSTAXOSEEETETE Slaxx
LAST RESORT ATOLAEXSTAXOSEEETET Slaxx
LAST RESORT ATOLAEXSTAXOSEEETE Slaxx
LAST RESORT ATOLAEXSTAXOSEEET Slaxx
LAST RESORT ATOLAEXSTAXOSEEE Slaxx
LAST RESORT ATOLAEXSTAXOSEE Slaxx
LAST RESORT ATOLAEXSTAXOSE Slaxx
LAST RESORT ATOLAEXSTAXOS Slaxx
LAST RESORT ATOLAEXSTAXO Slaxx
LAST RESORT ATOLAEXSTAX Slaxx
LAST RESORT ATOLAEXSTA Slaxx
LAST RESORT ATOLAEXST Slaxx
LAST RESORT ATOLAEXS Slaxx
LAST RESORT ATOLAEX Slaxx
LAST RESORT ATOLAE Slaxx
LAST RESORT ATOLA Parama
LAST RESORT ATOL Slaxx
LAST RESORT ATO Slaxx
8
https://forum.mafiascum.net/viewtopic.php?f=53&t=17276
Game 1157: Witch-Hunt Nightless
Moderator: Ythan
Current Update: Town Win
Notes: D2 No Majority; D8 Slaxx tried to vote Slaxx in post 1150 but while voteextractor interpreted "[b] vote:slaxx[\b]" correctly the mod rejected its formatting; toolfail

LAST RESORT no kill CF Riot 763 theamatuer
5
https://forum.mafiascum.net/viewtopic.php?f=53&t=22792
Game 1359: A Death Already Died
Moderator: UberNinja
Current Update: Mafia Win
Notes: D5 no lynch

LAST RESORT guy who scumclaimed projectmatt 870 Hibiki
LAST RESORT guy who crypto
LAST RESORT guy Sach
LAST RESORT gu Sach
3
https://forum.mafiascum.net/viewtopic.php?f=53&t=23221
Game 1373: Oh My!
Moderator: Empking
Current Update: Town Win

