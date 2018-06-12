This program automatically makes up doubles match-ups for badminton (and
potentially other sports such as tennis).


At present, it is limited to making up precisely three games of four players
each.


**User Guide**
===============================

**Creating Players**

Press the *"Create New Player"*, type in the player's name, and select their
sex and ability level.

"Affinities" are optional, and put a greater weighting on games containing
between two players as partners, as opponents, or both. To add an affinity,
press *"New"* to clear the combobox, type in an existing player's name, and
press *"Save"*.

You can also add general notes to a player in the textbox provided.

**Adding Players to the Bench**

You can select a player from the drop-down menu beneath the *"Absent Players"*
label and click *"Add Player To Bench"*. You can also add players by typing in
their name and pressing the "Enter" key, this may be faster. (Additionally, the
 latter method will immediately prompt you to create a new player if the name
 you typed in was not found).

**Automatically generating a game**

If you have at least 12 players available on the bench (and/or already on the
courts), you can press *"Generate New Board"* to put the games together
automatically. This will select the players that are most due for a game (those
 who been waiting the longest, followed by those who have played the fewest
 total games this session), then sorts those players onto the courts according
 to a number of criteria, such as game balance and player mixing.

**Manually creating/adjusting games**

You can add a player on the bench to a court by right-clicking their name,
clicking *"Pin To Court"*, then selecting the Court and space number.

You can return a player already on the court to the bench by right-clicking
their name and selecting *"Return to Bench"*.

As of the current version, you can manually adjust already-generated games, but
you cannot yet manually select a game and then automatically generate the
remaining games.

**Confirming Games**

Once you're happy with the games and confident the players will not change,
press *"Confirm Board"*. This will adjust everyone's game counts and set the
current round in stone.

**Emptying Courts**

The "Empty Courts" button will return all players on the courts to the bench.
This is useful if you want to manually create the games. However, it is not
necessary when automatically generating games.

**Player Menu Commands**

Right click on a player on the court or the bench to open the options menu.

Commands:

*View Player Stats*
Opens a pop-up menu containing user-editable statistics about the player,
including their ability and affinities.

*Return to Bench* (court only)
Returns a player on a court to the bench

*Remove from Night*
Returns the player to "absent players", removing them from this session.

*Keep Player Off Next Round*
This player will not be placed into an automatic generated game next round,
even if they would otherwise be due for one. Can be toggled off again as "Undo
Keep Player Off".


**Adjusting the Algorithm**

Press the *"Change Automatic Rules"* button to view the weightings given to
various parts of the game generation algorithm.

The algorithm gives every possible court combination of the 12 players selected
 a "score", according to how those combinations meets various criteria. The
 court combination with the *lowest* combined score is the one that is
 ultimately selected. Changing the weightings will change the way that courts
 are scored, and result in different games being produced.

**"Game Balance"** is calculated by subtracting the sum of the abilities of one
 partnership by the other, squaring this result, then multiplying this result
 by the "Game Balance Weighting", the default value of which is currently 5.

Decreasing the weighting will mean that the automatic generated games may
occasionally sacrifice a small amount of balance (usually in the form of more
games with an ability difference of 1, rarely more) in order to satisfy the
other criteria.

**"Ability Segregation"** is about creating games that group players of similar
 abilities together, recognising that a game consisting of two very strong
 players partnered with two very weak players may be balanced, but not
 necessarily desirable. This is calculated by subtracting the ability of the
 weakest player in a game from the strongest player, raising this result to the
  power of 1.5, then multiplying this result by the "Ability Segregation
  Weighting".

Lowering the ability segregation will mean more games with a mix of player
abilities, whereas raising it will mean most games have players with similar
abilities. However, high segregations may mean that players get a lot of
similar games.

**Player Mixing** is about trying to give players a good variety of partners
and opposition, and trying to avoid giving them too many games with the same
people. This is achieved by evaluating each player's history with each other
player. For each player, 2 points are added for each time that player played
one of the others in the same position they are now (that is, partner or
opponent), and 1 point for each time they played another player in a different
position. This is then discounted by 10% per game (so it is a bigger penalty to
 play someone twice in a row than once at the start of the night and once at
 the end), but then multiplied further for playing the same player multiple
 times.

Increasing the weighting will mean that players get a greater mixture of
opponents while decreasing will mean there is less emphasis on this (although
they'll likely get some natural mixing of opponents even with the weighting at
zero). As always, this might be at the expense of one of the other factors.

The **Affinity Weighting** simply describes the number of points subtracted
from a potential game (from *each* player that shares the affinity)  when it
contains players who have an affinity for each other in the position they have
an affinity for. For example, if two players with an "Opponent Affinity" are
facing each other, and the affinity weighting is 5, that game will have 5x2 =
10 points subtracted from it. If they are *partnered*, then there will be no
difference unless they had also had "Partner Affinity", in which case there
would again be a 10 point subtraction.

Increasing the affinity weighting will mean that players who share affinities
are more likely to play in games with each other. It needs to be considered in
conjunction with the *"Player Mixing Weighting"*, which players with affinities
 are still affected by. A very high affinity weighting may mean players with
 affinities *always* play each other so long as they are both available, which
 may be too much.

Finally, the last user-adjustable feature is the **Shuffle Algorithm**. This
does not affect the "score" of hypothetical games, but the way that ties are
broken when evaluating which players deserve to go on. Often, there are
numerous players who have been off the same number of times and who have been
played the same number of games.

The default *"Random"* setting picks these players (whose labels have an
*orange* background on the bench) at random.

*"Segregated"*, on the other hand, will firstly look at the players who are
definitely due on next game (those who are "green" on the bench) and evaluate
their average ability. If the average ability is *higher* than the average of
all the current players, then the "orange" players with the *highest* ability
are selected until there are 12 players. If the average ability is *lower*,
than the "orange" players with the *lowest* ability are selected. The typical
result will be the strongest players will end up in their own "flight", while
weaker players will end up in theirs, ensuring players will likely get a lot of
 games with players of similar ability. The downsides are a) they may end up
 with less variety overall and b) there may be a small overall bias towards
 players of given ability levels (either for or against players with middling
 ability).


