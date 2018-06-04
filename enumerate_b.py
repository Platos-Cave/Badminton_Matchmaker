'''I begin with a list (court_1s, should be renamed) of all
495 combinations of selecting 4 of the integers 0-11.
 From this I (somewhat clumsily) produce a list (all_combos) of all the
distinct ways of sorting the integers 0-11 into three unordered tuples.
e.g. one them will be [(0,1,6,7), (2,3,4,10), (5,8,9,11)]

Calling find_best_game() does the following:

For each combination in court_1s, I find all three pairing combos
e.g. (0,1,6,7) produces ((0,1),(6,7)),((0,6),(1,7)),((0,7),(1,6)))
through find_combos_of_four.

Each of these combos is passed into "score_courts()", which also takes
a list of players. Each integer represents a list index. So e.g.
((0,6),(1,7) represents the 0th and 6th indexed player on the list
playing against the 1st and 7th indexed player. The "score" of a game
is the summation of a number of factors I subjectively consider to
make for a good or poor matchup, such as differences in ability.

The lowest (i.e. best) score of the three combos is saved to the
scores_dict dictionary, and the combo itself to best_combos dict.
The original unordered combo is the key in both cases.

Then, for each element in all_combos (i.e. all possible distinct court
combinations), the scores of the courts are summed (via calls to
scores_dict). The element with the lowest score is the best possible
game according to the scoring rules. Each subsidiary combo is
translated to a game by first calling best_combos, then using
those numbers as indexes in the list of players. Finally,
find_best_game() returns this as best_players.
'''

import itertools
import operator
import random
import pickle

import time

# The user can adjust the weightings of elements of score_courts()
try:
    score_in = open("score_pi.obj","rb")
    scoring_vars = pickle.load(score_in)
    if len(scoring_vars) != 5:  # because of old version
        scoring_vars = [5.0, 2.0, 1.0, 4.0, 0]
    score_in.close()
except FileNotFoundError:
    scoring_vars = [5.0, 2.0, 1.0, 6.0, 0]

# Integers standing in for players
players = [i for i in range(12)]
# Will be appended until it has all possible three-court combos
all_combos = []
# Solely for the purpose of constructing all_combos
tested_combos = []
tested_combos_2 = []

# all possible ways of selecting 4 integers from 12
court_1s = list(itertools.combinations(players,4))

# Appends to all_combos all ~5500 possible unordered courts
# Seems very inelegant, but seems to work

for court_1 in court_1s:
    if court_1 not in tested_combos:
        tested_combos.append(court_1)
    players_left = [p for p in players if p not in court_1]
    tested_combos_2 = []    
    court_2s = list(itertools.combinations(players_left, 4))
    for court_2 in court_2s:
        if court_2 not in tested_combos:
            tested_combos_2.append(court_2)
            court_3 = tuple([p for p in players_left if p not in court_2])
            if court_3 not in tested_combos_2:
                if court_3 not in tested_combos: # Surely should be able to get this on one line?               
                    all_combos.append([court_1, court_2, court_3])


''' For a given combo (e.g. [0,1,6,7], score all three distinct combos
(i.e. ((0,1),(6,7)), ((0,6),(1,7)) and ((0,7),(1,6))).
Suppose the second combo had the lowest score, and that score was 8. 
The dictionary would appended as follows: scores_dict[0,1,6,7] = (((0,6),(1,7)), 7)
Now, whenever you come across [0,1,6,7], you call scores_dict[0,1,6,7][1] to score it as 7.
Saves 70? calculations each time.  Once you've found the minimum score, call [0] on all of them
to find the right combinations.'''

# For a key of 4 players (e.g. [0,1,6,7]), returns the best game (e.g. ((0,6),(1,7)))
best_combos = {}

# For a key of 4 players (e.g. [0,1,6,7]), returns the score of the game (e.g. 8)
scores_dict = {}

''' Returns the "score" of a game, where "trial_players" is a list of
 player objects and "court" is a pair of tuples, representing indices
 of those players'''
def score_court(court, trial_players):
    score = 0
    # Create the court using the indices from "court" on "trial_players"
    # Unpacked for easier referencing
    new_court = [trial_players[court[0][0]], trial_players[court[0][1]],
                 trial_players[court[1][0]], trial_players[court[1][1]]]

    abilities = [player.ability for player in new_court]
    # The imbalance between team abilities. High imbalance = highly penalised
    score += ((scoring_vars[0]*(sum(abilities[0:2]) - sum(abilities[2:4]))) ** 2)
    # It is generally better to not have strong and weak players in the same
    #  game even if balanced, so this formula penalises that.
    score += scoring_vars[1]*((max(abilities) - min(abilities))**1.5)

    # We then want to penalise playing the same people over and over.

    # How much the discount rate for each round is for the purposes of mixing
    # i.e. there's a larger penalty for playing someone you played in the
    # previous round than for someone you played three games ago
    discount_rate = 0.1

    # For each player, see how many times they've played with their partner
    # and their opponents. Larger penalty for playing someone in the same
    # position (i.e. played against someone twice in a row, vs played with them
    # and then against them)
    # Also: if player has affinity for another player, subtract the affinity score
    # from the total score.
    # This seems all very nested and duplicative
    for player in new_court:
        if player is not None:
            if player in new_court[0:2]:
                partner = [i for i in new_court[0:2] if i is not player if i is not None]
                opponents = [i for i in new_court[2:4] if i is not player if i is not None]
            else:
                partner = [i for i in new_court[2:4] if i is not player if i is not None]
                opponents = [i for i in new_court[0:2] if i is not player if i is not None]
              
        for o_player in opponents:
            count = 1
            base_score = 0
            for i, game in enumerate(player.played_against):
                if o_player in game:
                    base_score += scoring_vars[2]*2*((1/(1 + discount_rate)**(player.total_games - i -1)))
                    count += 0.2
            for i, game in enumerate(player.played_with):
                if o_player in game:
                    base_score =+ scoring_vars[2]*(1/(1+discount_rate)**(player.total_games - i -1))
                    count += 0.1
            #"Count" is a means of pseudo-exponentiation - i.e. we want it to be
            # proportionally worse to play someone three times row than twice
            score += base_score*(count)
            # Subtract affinity variable from score
            if o_player.name in player.opponent_affinities:
                   score -= scoring_vars[3]

        for o_player in partner:
            count = 1
            base_score = 0
            for i, game in enumerate(player.played_against):
                if o_player in game:
                    base_score += scoring_vars[2]*(1/(1+ discount_rate)**(player.total_games - i - 1))
                    count += 0.1
            for i, game in enumerate(player.played_with):
                if o_player in game:
                    base_score += scoring_vars[2]*2*((1/(1+discount_rate)**(player.total_games - i -1)))
                    count += 0.2
            score += base_score*(count)
            if o_player.name in player.partner_affinities:
                   score -= scoring_vars[3]
       
    return score

'''From four numbers, return three pairs of tuples representing the unique matchups

Need to: find a way to avoid putting pinned players on opposite sides

Could cut down on computation time (not necessary atm) if instead of testing
all three combos, instead had some heuristics for picking it (like put strongest
and weakest player together).
'''
def find_combos_of_four(combo):

    every_combo = list(itertools.combinations(combo,2))
    tested_combos = []
    unique_combos = []

    for court_1 in every_combo:
        tested_combos.append(court_1)
        court_2 = tuple([p for p in combo if p not in court_1])
        if court_2 not in tested_combos:
            unique_combos.append(((court_1),(court_2)))
            
    return unique_combos

# From four numbers, find the matchup with the lowest score.
# Add the combo as a key to two dictionaries: one the best combo, the other the score of said result

def best_score(combo, trial_players):
    scores = []
    three_combos = find_combos_of_four(combo)

    for com in three_combos:
        scores.append(score_court(com, trial_players))

    index, scores_dict[combo] = min(enumerate(scores), key=operator.itemgetter(1))
    best_combos[combo] = three_combos[index]

# From a list of 12 player objects, return the  best three games possible
def find_best_game(trial_players):

    scores = []

    # Score all the combos
    for combo in court_1s:
        best_score(combo, trial_players)

    # Look up each combo's score, add together.
    for combo in all_combos:
        scores.append(scores_dict[combo[0]] + scores_dict[combo[1]] + scores_dict[combo[2]])

    index, lowest_score = min(enumerate(scores), key=operator.itemgetter(1))

    # The best combinations of players on each of the three courts (unsorted)
    best_unsorted = all_combos[index]
    
    # For each of the unsorted courts, find the best of the 3 combos,
    # then set that as the court.
    # Possible drawback: no tiebreaking mechanism might cause a small bias,

    best_game = [best_combos[best_unsorted[i]] for i in range (3)]

    # Index the players to the numbers representing them.
    # Ugly, should be able to make more succinct and readable
    
    best_players = (((trial_players[best_game[0][0][0]], trial_players[best_game[0][0][1]]),
                    (trial_players[best_game[0][1][0]], trial_players[best_game[0][1][1]])),
                    ((trial_players[best_game[1][0][0]], trial_players[best_game[1][0][1]]),
                    (trial_players[best_game[1][1][0]], trial_players[best_game[1][1][1]])),
                     ((trial_players[best_game[2][0][0]], trial_players[best_game[2][0][1]]),
                    (trial_players[best_game[2][1][0]], trial_players[best_game[2][1][1]])))

    return best_players