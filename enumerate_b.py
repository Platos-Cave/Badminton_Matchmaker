"""I begin with a list (court_1s, should be renamed) of all
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
find_best_game() returns this as best_players."""

import itertools
from itertools import combinations
import operator
import pickle
import datetime
#from b_scorer import courts
courts = 2



# The user can adjust the weightings of elements of score_courts()
try:
    score_in = open("score_pi.obj", "rb")
    scoring_vars = pickle.load(score_in)
    # replace old version
    if ('Ability Alternation', 'Default') not in scoring_vars:
        scoring_vars[('Ability Alternation', 'Default')] = 2.0
        scoring_vars[('Ability Alternation', 'Tuesday')] = 2.0
        scoring_vars[('Ability Alternation', 'Thursday')] = 2.0
        print("Ability Alternation added!")
    score_in.close()
except FileNotFoundError:
    # seems ugly, should be mapped differently
    scoring_vars = {('Balance', "Default"): 5.0,
                    ('Ability_Seg', "Default"): 2.0,
                    ('Mixing', "Default"): 1.5,
                    ('Affinity', "Default"): 4.0, ('Shuffle', "Default"): 0,
                    ('Balance', 'Tuesday'): 5.0, ('Ability_Seg',
                                                  'Tuesday'): 2.0,
                    ('Mixing', 'Tuesday'): 2.0, ('Affinity',
                                                 'Tuesday'): 4.0,
                    ('Shuffle', 'Tuesday'): 0, ('Balance', 'Thursday'):
                        6.0,
                    ('Ability_Seg', 'Thursday'): 3.0,
                    ('Mixing', 'Thursday'): 1.5,
                    ('Affinity', 'Thursday'): 5.0,
                    ('Shuffle', 'Thursday'): 1,
                    ('Female Affinity', 'Default'): 1.0,
                    ('Female Affinity', 'Tuesday'): 1.0,
                    ('Female Affinity', 'Thursday'): 1.0}
    if ('Ability Alternation', 'Default') not in scoring_vars:
        scoring_vars[('Ability Alternation', 'Default')] = 2.0
        scoring_vars[('Ability Alternation', 'Tuesday')] = 2.0
        scoring_vars[('Ability Alternation', 'Thursday')] = 2.0

# what score profile to use
day_of_week = datetime.datetime.today().weekday()
if day_of_week == 1:
    profile = "Tuesday"
elif day_of_week == 3:
    profile = "Thursday"
else:
    profile = "Default"

# Defines the multipliers for each level of affinity
level_dict = {'Low': 0.5, 'Medium': 1, 'High': 2, 'Maximum': 1000000}

# # Integers standing in for players
# players = [i for i in range(12)]
# # Will be appended until it has all possible three-court combos
# all_combos = []
# # Solely for the purpose of constructing all_combos
# tested_combos = []
# tested_combos_2 = []
#
# # all possible ways of selecting 4 integers from 12. Bad name
# court_1s = list(itertools.combinations(players, 4))
#
# '''Appends to all_combos all ~5500 possible unordered courts
# Seems very inelegant, but seems to work
# Probably should be in a function?'''
#
# for court_1 in court_1s:
#     if court_1 not in tested_combos:
#         tested_combos.append(court_1)
#     players_left = [p for p in players if p not in court_1]
#     tested_combos_2 = []
#     court_2s = list(itertools.combinations(players_left, 4))
#     for court_2 in court_2s:
#         if court_2 not in tested_combos:
#             tested_combos_2.append(court_2)
#             court_3 = tuple([p for p in players_left if p not in court_2])
#             # Surely should be able to get this on one line?
#             if court_3 not in tested_combos_2:
#                 if court_3 not in tested_combos:
#                     all_combos.append([court_1, court_2, court_3])
#
# #
# # print(all_combos[0])
# # print(all_combos[1000])
# # print(all_combos[-1])
# print(len(all_combos))

def partitions(s, r):
    """
    Generate partitions of the iterable `s` into subsets of size `r`.

    >>> list(partitions(set(range(4)), 2))
    [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    """
    s = set(s)
    assert(len(s) % r == 0)
    if len(s) == 0:
        yield ()
        return
    first = next(iter(s))
    rest = s.difference((first,))
    for c in combinations(rest, r - 1):
        first_subset = (first,) + c
        for p in partitions(rest.difference(c), r):
            yield (first_subset,) + p

players = [i for i in range(8)]
combos = list(partitions(range(8),4))
all_combos = []
for games in combos:
    all_combos.append([])
    for game in games:
        all_combos[-1].append(tuple(sorted(game)))
court_1s = list(itertools.combinations(players, 4))


''' For a given combo (e.g. [0,1,6,7], score all three distinct combos
(i.e. ((0,1),(6,7)), ((0,6),(1,7)) and ((0,7),(1,6))).
Suppose the second combo had the lowest score, and that score was 8. 
The dictionary would appended as  follows: scores_dict[0,1,6,7] = (((0,6),(1,
7)).
Now, whenever you come across [0,1,6,7], you call scores_dict[0,1,6,
7][1] to score it as 7.
Saves 70? calculations each time. Once you've found the minimum score, 
call [0] on all of them to find the right combinations.'''

# For a key of 4 players (e.g. [0,1,6,7]), returns the best game (e.g. ((0,
# 6),(1,7)))
best_combos = {}

# For a key of 4 players (e.g. [0,1,6,7]), returns the score of the game (
# e.g. 8)
scores_dict = {}

def score_court(court, trial_players, explain = False):
    ''' Returns the "score" of a game, where "trial_players" is a list of
     player objects and "court" is a pair of tuples, representing indices
     of those players'''
    score = 0
    # Create the court using the indices from "court" on "trial_players"
    # Unpacked for easier referencing
    new_court = [trial_players[court[0][0]], trial_players[court[0][1]],
                 trial_players[court[1][0]], trial_players[court[1][1]]]

    abilities = [player.ability for player in new_court]
    # The imbalance between team abilities. High imbalance = highly penalised
    score += scoring_vars[('Balance', profile)] * 5 * ((
                sum(abilities[0:2]) - sum(abilities[2:4])) ** 2)
    # It is generally better to not have strong and weak players in the same
    #  game even if balanced, so this formula penalises that.
    # Removing for now
    score += scoring_vars[('Ability_Seg', profile)] * (
                (max(abilities) - min(abilities)) ** 1.5)

    #NEW: "Hungry" weighting
    average_ability = sum(abilities)/4
    for player in new_court:
        score += scoring_vars[('Ability Alternation', profile)] * \
                 player.hunger * (player.ability - average_ability)



    # # We then want to penalise playing the same people over and over.
    #
    # # How much the discount rate for each round is for the purposes of mixing
    # # i.e. there's a larger penalty for playing someone you played in the
    # # previous round than for someone you played three games ago
    discount_rate = 0.1
    #
    # # For each player, see how many times they've played with their partner
    # # and their opponents. Larger penalty for playing someone in the same
    # # position (i.e. played against someone twice in a row, vs played with them
    # # and then against them)
    # # Also: if player has affinity for another player, subtract the affinity
    # # score from the total score.
    # # (This seems all very nested and duplicative)
    for player in new_court:
        if player is not None:
            if player in new_court[0:2]:
                partner = [i for i in new_court[0:2] if i is not player if
                           i is not None]
                opponents = [i for i in new_court[2:4] if i is not player if
                             i is not None]
            else:
                partner = [i for i in new_court[2:4] if i is not player if
                           i is not None]
                opponents = [i for i in new_court[0:2] if i is not player if
                             i is not None]

        for o_player in opponents:
            count = 1
            base_score = 0
            for i, game in enumerate(player.played_against):
                if o_player in game:
                    base_score += scoring_vars[('Mixing', profile)] * 2 * (
                    (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
                    count += 0.2
            for i, game in enumerate(player.played_with):
                if o_player in game:
                    base_score += scoring_vars[('Mixing', profile)] * (
                                1 / (1 + discount_rate) ** (
                                     player.total_games - i - 1))
                    count += 0.1
            # "Count" is a means of pseudo-exponentiation - i.e. we want it
            # to be proportionally worse to play someone three times in a row
            # than twice in a row
            score += base_score * (count)
            # Subtract affinity variable from score
            for aff in player.opponent_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

        for o_player in partner:  # there's only 1 partner, so loop seems silly?
            count = 1
            base_score = 0
            for i, game in enumerate(player.played_against):
                if o_player in game:
                    base_score += scoring_vars[('Mixing', profile)] * (
                                1 / (1 + discount_rate) ** (
                                    player.total_games - i - 1))
                    count += 0.1
            for i, game in enumerate(player.played_with):
                if o_player in game:
                    base_score += scoring_vars[('Mixing', profile)] * 3 * (
                    (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
                    count += 0.2
            score += base_score * (count)

            for aff in player.partner_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

    # Female mini-affinity:
    no_women = len([p for p in new_court if p.sex == "Female" if p])
    women_score = scoring_vars[('Female Affinity', profile)] * (no_women*(
            no_women - 1))
    score -= women_score

    if explain:
        print("There are {} women in this game, subtracting {} from the game "
              "score".format(no_women, women_score))
        print(score)

    return score


def find_combos_of_four(combo):
    '''From four numbers, return three pairs of tuples representing the unique
    match-ups.

    Could cut down on computation time (not necessary atm) if instead of testing
    all three combos, instead had some heuristics for picking it (like put
    strongest and weakest player together). '''

    every_combo = list(itertools.combinations(combo, 2))
    tested_combos = []
    unique_combos = []

    for court_1 in every_combo:
        tested_combos.append(court_1)
        court_2 = tuple([p for p in combo if p not in court_1])
        if court_2 not in tested_combos:
            unique_combos.append(((court_1), (court_2)))

    return unique_combos

def best_score(combo, trial_players):
    '''From four numbers, find the matchup with the lowest score.
    Add the combo as a key to two dictionaries: one the best combo,
    the other the score of said result'''
    scores = []
    three_combos = find_combos_of_four(combo)

    for com in three_combos: # EXCEPT RULED-OUT PINNED
        scores.append(score_court(com, trial_players))

    index, scores_dict[combo] = min(enumerate(scores),
                                    key=operator.itemgetter(1))
    best_combos[combo] = three_combos[index]


def find_best_game(trial_players):

    '''From a list of 12 player objects, return the best three games possible'''
    scores = []

    # Score all the combos

    for combo in court_1s:
        best_score(combo, trial_players)


    # Look up each combo's score, add together.
    for combo in all_combos:
        scores.append(
            [scores_dict[combo[i]] for i in range(courts)])

    index, lowest_score = min(enumerate(scores), key=operator.itemgetter(1))
    print(f'Lowest score: {lowest_score}')

    # The best combinations of players on each of the three courts (unsorted)
    best_unsorted = all_combos[index]

    # For each of the unsorted courts, find the best of the 3 combos,
    # then set that as the court.
    # Possible drawback: no tie-breaking mechanism might cause a small bias?

    best_game = [best_combos[best_unsorted[i]] for i in range(courts)]


    # Index the players to the numbers representing them.
    # Ugly, should be able to make more succinct and readable

    # best_players = (
    # ((trial_players[best_game[0][0][0]], trial_players[best_game[0][0][1]]),
    #  (trial_players[best_game[0][1][0]], trial_players[best_game[0][1][1]])),
    # ((trial_players[best_game[1][0][0]], trial_players[best_game[1][0][1]]),
    #  (trial_players[best_game[1][1][0]], trial_players[best_game[1][1][1]])),
    # ((trial_players[best_game[2][0][0]], trial_players[best_game[2][0][1]]),
    #  (trial_players[best_game[2][1][0]], trial_players[best_game[2][1][1]])))

    best_players = (
    ((trial_players[best_game[0][0][0]], trial_players[best_game[0][0][1]]),
     (trial_players[best_game[0][1][0]], trial_players[best_game[0][1][1]])),
    ((trial_players[best_game[1][0][0]], trial_players[best_game[1][0][1]]),
     (trial_players[best_game[1][1][0]], trial_players[best_game[1][1][1]])))

    print(all_combos)
    print([p.name for p in trial_players])
    print(best_combos)
    print(scores_dict)

    return best_players
