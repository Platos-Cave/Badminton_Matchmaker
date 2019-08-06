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
from numpy import sign
import b_scorer


def score_court(court, trial_players, unpack=True, explain = False):
    ''' Returns the "score" of a game, where "trial_players" is a list of
     player objects and "court" is a pair of tuples, representing indices
     of those players'''

    score = 0
    # Create the court using the indices from "court" on "trial_players"
    # Unpacked for easier referencing
    if unpack:
        new_court = [trial_players[court[0][0]], trial_players[court[0][1]],
                 trial_players[court[1][0]], trial_players[court[1][1]]]
    else:
        new_court = court


    abilities = [player.ability for player in new_court]

    segregation = max(abilities) - min(abilities)
    score += scoring_vars[('Ability_Seg', profile)] * (segregation ** 1.5)

    # The imbalance between team abilities. High imbalance = highly penalised
    imbalance = (sum(abilities[0:2]) - sum(abilities[2:4]))
    # new: more segregated games care less about imbalance
    seg_change = 1 + segregation/5
    score += scoring_vars[('Balance', profile)] * 6 * ((imbalance **
                                                        2)/seg_change)

    # "Ability alternation weighting weighting
    average_ability = sum(abilities)/4
    for player in new_court:
        score += scoring_vars[('Ability Alternation', profile)] * \
                 player.hunger * (player.ability - average_ability)


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

            new_score = scoring_vars[('Mixing',
                                      profile)]*player.opp_histories[
                o_player]

            score += new_score
            # Subtract affinity variable from score
            for aff in player.opponent_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

            # if first game with newbie and newbie aff, -20 points
            if (player.affinity_for_newbies) and (o_player.first_night):
                if player.partner_histories[o_player] >0:
                    pass
                else:
                    score -= 20

        for o_player in partner:  # there's only 1 partner, so loop seems


            new_score = scoring_vars[('Mixing',
                                      profile)]*player.partner_histories[
                o_player]

            # Simple fitness hack. Might want more, so it's less complex

            if (player.fitness == 1) and (o_player.fitness == 1):
                score += 20 # basically guaranteeing they're not together


            score += new_score

            for aff in player.partner_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

            if (player.affinity_for_newbies) and (o_player.first_night):
                if player.partner_histories[o_player] >0:
                    pass
                else:
                    score -= 20

    # Female mini-affinity:
    no_women = len([p for p in new_court if p.sex == "Female" if p])

    # should be a simple formula, like 2**(x-1)
    if no_women<2:
        women_score = 0
    else:
        women_score = 2**(no_women - 1)  # (2 women->2, 3->4, 4-> 8)

    women_score = scoring_vars[('Female Affinity', profile)] * women_score
                  #old (no_women*(no_women - 1))
    score -= women_score

    return score


def find_combos_of_four(combo):
    '''From four numbers, return three pairs of tuples representing the unique
    match-ups.'''

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

    for com in three_combos:
        scores.append(score_court(com, trial_players))

    # consider frozenset(combo) for alternative method
    index, scores_dict[combo] = min(enumerate(scores),
                                    key=operator.itemgetter(1))
    # try making best_combos[frozenset(combo)]
    best_combos[combo] = three_combos[index]
    # best_combos[combo] = three_combos[index]


def find_best_game(players, courts, benched = [], scored=False, log=False):

    '''From a list of player objects, return the best three games possible'''
    scores = []

    # Score all the combos
    for combo in combos_total[courts-1][0]:
        best_score(combo, players)

    # Look up each combo's score, add together.
    for combo in combos_total[courts-1][1]:
        scores.append(sum([scores_dict[combo[i]] for i in range(courts)]))

    index, lowest_score = min(enumerate(scores), key=operator.itemgetter(1))


    # The best combinations of players on each of the three courts (unsorted)
    best_unsorted = combos_total[courts-1][1][index]

    # For each of the unsorted courts, find the best of the 3 combos,
    # then set that as the court.
    # Possible drawback: no tie-breaking mechanism might cause a small bias?
    best_game = [best_combos[best_unsorted[i]] for i in range(courts)]

    # Index the players to the numbers representing them.
    # Ugly, should be able to make more succinct and readable

    best_players = [((players[best_game[i][0][0]],
                    players[best_game[i][0][1]]),
          (players[best_game[i][1][0]],
           players[best_game[i][1][1]])) for i in range(courts)]

    tolerance_score = tolerance_cost(players)
    lowest_score += tolerance_score

    # Get a bonus for having players with an affinity be on or be off together
    if not b_scorer.final_round_boost:
        bench_score = (bench_cost(benched))*(0.5*scoring_vars[('Affinity',profile)])
        courts_score = (bench_cost(players)) * (0.3 * scoring_vars[('Affinity',
                                                               profile)])
    else:
        bench_score = final_game_cost(benched)
        courts_score = final_game_cost(players)

    lowest_score -= bench_score
    lowest_score -= courts_score


    if not scored:
        return best_players
    if scored: # for finding more
        return (best_players, lowest_score, tolerance_score, bench_score, courts_score)

def tolerance_cost(players):
    tolerance_score = 0
    for player in players:
        # games with more deserving players -> lower cost
        # tricky to come up with. Convoluted way of keeping sign.
        tolerance_score -= 10 * ((abs(player.desert) ** 1.5) * sign(
            player.desert))

        # rudimetary fitness.

        if player.fitness == 1:
            mult = 5
            exp = 2
        elif player.fitness == 3:
            mult = 5
            exp = 1.25
        else:
            mult = 5
            exp = 1.5

        tolerance_score += mult * (
                player.consecutive_games_on ** exp)

        # Keep "hungry" players on
        tolerance_score -= mult * player.hunger
    return tolerance_score

def bench_cost(benched):
    # O(n**2), can do better? Not too important for these levels of n
    cost = 0
    for player in benched:
        #partner_affs = [i[0] for i in (player.partner_affinities)]
        #opp_affs = [i[0] for i in (player.opponent_affinities)]

        for other_player in benched:
            partner_checks = {}
            for aff in player.partner_affinities:
                if other_player.name == aff[0]:
                    cost += 1 * level_dict[aff[1]]
                    partner_checks[other_player] = level_dict[aff[1]]
                    break

            for aff in player.opponent_affinities:
                if other_player.name == aff[0]:
                    try:
                        partner_cost = partner_checks[other_player]
                    except KeyError:
                        partner_cost = 0
                    if partner_cost < level_dict[aff[1]]:
                        cost += level_dict[aff[1]] - partner_cost
                    break

    return cost

def final_game_cost(players):
    cost = 0
    for player in players:
        for other_player in players:
            for aff in player.leave_affs:
                if other_player.name == aff:
                    cost += 100 # too much? too low?
    # print("Bench cost", cost)
    return cost


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
    if ('Trials', 'Default') not in scoring_vars:
        scoring_vars[('Trials', 'Default')] = 1000
        scoring_vars[('Trials', 'Tuesday')] = 1000
        scoring_vars[('Trials', 'Thursday')] = 1000
        scoring_vars[('Shuffle', 'Tuesday')] = 2
        scoring_vars[('Shuffle', 'Thursday')] = 2
        scoring_vars[('Shuffle', 'Default')] = 2


    score_in.close()
except FileNotFoundError:
    # seems ugly, should be mapped differently
    scoring_vars = {('Balance', "Default"): 5.0,
                    ('Ability_Seg', "Default"): 2.0,
                    ('Mixing', "Default"): 1.5,
                    ('Affinity', "Default"): 5.0, ('Shuffle', "Default"): 2,
                    ('Balance', 'Tuesday'): 5.0, ('Ability_Seg',
                                                  'Tuesday'): 2.0,
                    ('Mixing', 'Tuesday'): 2.0, ('Affinity',
                                                 'Tuesday'): 5.0,
                    ('Shuffle', 'Tuesday'): 2, ('Balance', 'Thursday'):
                        6.0,
                    ('Ability_Seg', 'Thursday'): 3.0,
                    ('Mixing', 'Thursday'): 1.5,
                    ('Affinity', 'Thursday'): 5.0,
                    ('Shuffle', 'Thursday'): 2,
                    ('Female Affinity', 'Default'): 1.0,
                    ('Female Affinity', 'Tuesday'): 1.0,
                    ('Female Affinity', 'Thursday'): 1.0}
    if ('Ability Alternation', 'Default') not in scoring_vars:
        scoring_vars[('Ability Alternation', 'Default')] = 2.0
        scoring_vars[('Ability Alternation', 'Tuesday')] = 2.0
        scoring_vars[('Ability Alternation', 'Thursday')] = 2.0
    if ('Trials', 'Default') not in scoring_vars:
        scoring_vars[('Trials', 'Default')] = 1000
        scoring_vars[('Trials', 'Tuesday')] = 1000
        scoring_vars[('Trials', 'Thursday')] = 1000

# what score profile to use
day_of_week = datetime.datetime.today().weekday()
if day_of_week == 1:
    profile = "Tuesday"
elif day_of_week == 3:
    profile = "Thursday"
else:
    profile = "Default"

combos_total = []

for i in range(1,4):
    players = [p for p in range(i*4)]
    combos = list(partitions(range(i*4), 4))
    all_combos = []
    # should modify 'partitions' function to do this
    for games in combos:
        all_combos.append([])
        for game in games:
            all_combos[-1].append(tuple(sorted(game)))
    court_1s = list(itertools.combinations(players, 4))
    combos_total.append((court_1s, all_combos))


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

# Defines the multipliers for each level of affinity
level_dict = {'Low': 0.5, 'Medium': 1, 'High': 2, 'Maximum': 1000000}













