https://forum.mafiascum.net/viewtopic.php?f=53&t=15783
Game 1094: Mariposa Peak Mafia
Moderator: DemonHybrid
Current Update: Town Win
Notes: D1 toolfail; Blood Queen voted Reckamonic in post 10 but votecounter could not match "Dramonerx" to a player

https://forum.mafiascum.net/viewtopic.php?f=53&t=15982
Game 1107: Just a Game
Moderator: Tasky
Current Update: Town Win
Notes: D1 toolfail; ICEninja voted UNVOTE in post 18 but votecounter detected nothing

https://forum.mafiascum.net/viewtopic.php?f=53&t=16769
Game 1133: Mafia in Venice
Moderator: lewarcher82
Current Update: Mafia Win
Notes: D5 toolfail; ICEninja voted RedCoyote in post 489 but votecounter extracted no vote from "[b]Cross fingers, vote RedCoyote.[/b]"

https://forum.mafiascum.net/viewtopic.php?f=53&t=16852
Game 1140: Mafia Mishmash
Moderator: havingfitz
Current Update: Mafia Win
Notes: D2 toolfail; Haylen voted andrew94 in post 803 but typed [b]Vote Andrew[/b] within an area tag and multiline bold tag

## Offhand

### 1094 // 15783
The documented error at post 10 is real even if it didn't impact votecounter output. 

I don't think the votecounter could ever handle this issue systematically; I should add support for alias specification rather than just single-vote correction so all errors like this are properly handled.

## 1107 // 15982
Pattern starting to emerge where votes that don't start the line aren't being detected properly. Need to check processing depth.

Hmm, actually the voteextractor is detecting the vote just fine! I'm just not seeing the result in my DF! Why not? I'm not properly skipping vote notes.

## 1133 // 16769
Same pattern. Should I just jump to trying to address it? Let's try to fill the page first.

## 1140 // 16852
Same pattern! Might investigate if I find the problem one more time.