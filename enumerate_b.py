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
import time
from numpy import sign
from random import shuffle


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
# print(court_1s)
# #
# # #
# # # print(all_combos[0])
# # # print(all_combos[1000])
# # # print(all_combos[-1])
# # print(len(all_combos))

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

combos_total = []

# t0 = time.time()
# sel = list(itertools.combinations([i for i in range (24)], 12))
# print(len(sel))
# print(sel[0], sel[1345], sel[66666])
#
# #for s in selections:
# #    combos = list(partitions(s, 4))
# t1 = time.time()
# print(f'{t1-t0} is the partitioning')

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

score_num = 0

def score_court(court, trial_players, explain = False):
    ''' Returns the "score" of a game, where "trial_players" is a list of
     player objects and "court" is a pair of tuples, representing indices
     of those players'''
    global score_num
    score_num +=1

    score = 0
    # Create the court using the indices from "court" on "trial_players"
    # Unpacked for easier referencing
    new_court = [trial_players[court[0][0]], trial_players[court[0][1]],
                 trial_players[court[1][0]], trial_players[court[1][1]]]

    #############################
    # for player in new_court:
    #     # games with more deserving players -> lower cost
    #     # tricky to come up with. Convoluted way of keeping sign.
    #     score -= 10 * ((abs(player.desert) ** 1.5) * sign(
    #         player.desert))
    #     # games with players on more times in a row -> higher cost
    #     # assumption that stronger players = fitter = less tired?
    #     score += ((15-player.ability)/2)*(
    #             player.consecutive_games_on**1.5)
    ###########################

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
            # count = 1
            # base_score = 0
            # for i, game in enumerate(player.played_against):
            #     if o_player in game:
            #         base_score += scoring_vars[('Mixing', profile)] * 2 * (
            #         (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
            #         count += 0.2
            # for i, game in enumerate(player.played_with):
            #     if o_player in game:
            #         base_score += scoring_vars[('Mixing', profile)] * (
            #                     1 / (1 + discount_rate) ** (
            #                          player.total_games - i - 1))
            #         count += 0.1
            # #"Count" is a means of pseudo-exponentiation - i.e. we want it
            # #to be proportionally worse to play someone three times in a row
            # # than twice in a row
            # adjusted_score = base_score * (count)

            new_score = scoring_vars[('Mixing',
                                      profile)]*player.opp_histories[
                o_player]


            if explain:
                if player.name == "Henry":
                    # print(f'(Henry score with opponent is {adjusted_score}')
                    print(f'(Henry new score with opponent is {new_score}')

            #score += adjusted_score
            score += new_score
            # Subtract affinity variable from score
            for aff in player.opponent_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

        for o_player in partner:  # there's only 1 partner, so loop seems
             # silly?
        #     count = 1
        #     base_score = 0
        #     for i, game in enumerate(player.played_against):
        #         if o_player in game:
        #             base_score += scoring_vars[('Mixing', profile)] * (
        #                         1 / (1 + discount_rate) ** (
        #                             player.total_games - i - 1))
        #             count += 0.1
        #     for i, game in enumerate(player.played_with):
        #         if o_player in game:
        #             base_score += scoring_vars[('Mixing', profile)] * 3 * (
        #             (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
        #             count += 0.2
        #
        #     adjusted_score = base_score * (count)

            new_score = scoring_vars[('Mixing',
                                      profile)]*player.partner_histories[
                o_player]

            if explain:
                if player.name == "Henry":
                    # print(f'(Henry score with partner is {adjusted_score}')
                    print(f'(Henry new score with opponent is {new_score}')
            #score += adjusted_score
            score += new_score

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

    for com in three_combos:
        scores.append(score_court(com, trial_players))

    # consider frozenset(combo) for alternative method
    index, scores_dict[combo] = min(enumerate(scores),
                                    key=operator.itemgetter(1))
    # try making best_combos[frozenset(combo)]
    best_combos[combo] = three_combos[index]
    # best_combos[combo] = three_combos[index]


def find_best_game(players, courts, benched = [], scored=False, log=False):

    t1 = time.time()

    '''From a list of 12 player objects, return the best three games possible'''
    scores = []


    # Score all the combos
    # print(combos_total[courts-1][0])

    for combo in combos_total[courts-1][0]:
        best_score(combo, players)

    t2 = time.time()

    # Look up each combo's score, add together.


    for combo in combos_total[courts-1][1]:
        scores.append(sum([scores_dict[combo[i]] for i in range(courts)]))

    t3 = time.time()

    index, lowest_score = min(enumerate(scores), key=operator.itemgetter(1))

    t4 = time.time()

    # The best combinations of players on each of the three courts (unsorted)
    best_unsorted = combos_total[courts-1][1][index]

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

    best_players = [((players[best_game[i][0][0]],
                    players[best_game[i][0][1]]),
          (players[best_game[i][1][0]],
           players[best_game[i][1][1]])) for i in range(courts)]

    # For "tolerance"
    tolerance_score = 0

    for player in players:
        # games with more deserving players -> lower cost
        # tricky to come up with. Convoluted way of keeping sign.
        tolerance_score -= 10 * ((abs(player.desert) ** 1.5) * sign(
            player.desert))
        # if player.name == "Henry":
        #     print(player.desert)
        #     print(10 * ((abs(player.desert) ** 1.5) * sign(
        #     player.desert)))


        # games with players on more times in a row -> higher cost
        # assumption that stronger players = fitter = less tired?
        tolerance_score += ((15-player.ability)/2)*(
                player.consecutive_games_on**1.5)
        # fraction ?

    lowest_score += tolerance_score

    # Get a bonus for having players with an affinity be on or be off together
    bench_score = (bench_cost(benched))*(0.5*scoring_vars[('Affinity',profile)])
    courts_score = (bench_cost(players)) * (0.3 * scoring_vars[('Affinity',
                                                           profile)])


    lowest_score -= bench_score
    lowest_score -= courts_score

    t5 = time.time()


    if log:
        print(f'{t2-t1} to score the combos')
        print(f'{t3-t2} for adding')
        print(f'{t4-t3} for finding index')
        print(f'{t5-t4} for the rest')


    if not scored:
        return best_players
    if scored: # for finding more
        return (best_players, lowest_score, tolerance_score, bench_score)

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


#############
# Testing "score all combos'


def find_best_exhaustive(players, runs, check):
    #combo_2 = [player.name for player in players]

    shuffle(players)
    t1 = time.time()
    combos = list(itertools.combinations([i for i in range(len(players))], 4))
    t2 = time.time()
    for combo in combos:
        best_score_2(combo, players)
    t3 = time.time()
    #print(f'{t2-t1} to create the combos')
    #print(f'{t3-t2} to score the combos')
    # print(scores_dict)
    k = 0
    fixed = set([players[i] for i in range(k)])
    #print(fixed)
    #print([players[i].name for i in range(k)])
    best_unsorted, cost = (greedy_solve(scores_dict, len(players), m=3,
                               extra_runs=runs,

                                        check_factor=check,
                                        required_keys=[i for i in range(k)]))

    # best_unsorted, cost = (dp_solve(scores_dict, len(players), m=3))


    best_game = [best_combos[best_unsorted[i]] for i in range(3)]

    # if not check_for_duplicates(players, best_game, fixed):
    #      return False
    # else:
    #     # pass
    #     print("Yes!")

    t4 = time.time()
    print(f'{t4-t3} to do rest')

    best_players = [((players[best_game[i][0][0]],
                    players[best_game[i][0][1]]),
          (players[best_game[i][1][0]],
           players[best_game[i][1][1]])) for i in range(3)]



    return best_players

    #
    #
    # for i, court in enumerate(best):
    #     print(f'Court {i}')
    #     for num in court:
    #         print(players[num].name)
    # t4 = time.time()
    # print(f'{t4-t3} to find the best')
def smart_shuffle_trial(players, courts, benched = [], scored=False, log=False):
    from b_scorer import select_players
    shuffle(players)
    t1 = time.time()
    combos = list(itertools.combinations([i for i in range(len(players))], 4))
    t2 = time.time()
    for combo in combos:
        best_score_2(combo, players)
    t3 = time.time()

    indices_dict = {}

    for i in range(1000):

        scores = []

        new_players = select_players("Smart", courts)
        for i, play in enumerate(new_players):
            # find the indice of the player in new players
            for j, play2 in enumerate(players):
                if play == play2:
                    indices_dict[i] = j


    # print([p.name for p in new_players])
    # print([p.name for p in players])
    # print(indices_dict)

        for combo in combos_total[courts - 1][1]:
            # translate the indices
            combo_2 = [() for i in range (3)]
            for i, game in enumerate(combo):
                combo_2[i] = [indices_dict[j] for j in game]
            #print(combo_2)

            scores.append(sum([scores_dict[combo[i]] for i in range(courts)]))


        index, lowest_score = min(enumerate(scores),
                                  key=operator.itemgetter(1))


        # The best combinations of players on each of the three courts (unsorted)
        best_unsorted = combos_total[courts - 1][1][index]

        # For each of the unsorted courts, find the best of the 3 combos,
        # then set that as the court.
        # Possible drawback: no tie-breaking mechanism might cause a small bias?

        best_game = [best_combos[best_unsorted[i]] for i in range(courts)]

        # Index the players to the numbers representing them.
        # Ugly, should be able to make more succinct and readable

        best_players = [((players[best_game[i][0][0]],
                          players[best_game[i][0][1]]),
                         (players[best_game[i][1][0]],
                          players[best_game[i][1][1]])) for i in
                        range(courts)]

    t4 = time.time()
    print(t4-t1)
    print(t4-t3)

    return best_players







def check_for_duplicates(players, game, fixed):
    board = set()
    for court in game:
        for side in court:
            for player in side:
                board.add(players[player])
    #print([player.name for player in fixed])
    #print([player.name for player in board])
    if fixed.issubset(board):
        return True
    else:
        return False

def greedy_solve(const_dict, n, m, extra_runs=10, check_factor=2,
                 required_keys = []):
    pairs = sorted(const_dict.items(), key=lambda x: x[1])

    lookup = [set([]) for _ in range(n)]
    nset = set([])

    min_sums = []
    min_key, min_val = None, None
    for i, (pkey, pval) in enumerate(pairs):
        valid = set(nset)
        for x in pkey:
            valid -= lookup[x]
            lookup[x].add(len(min_sums))

        nset.add(len(min_sums))
        min_sums.append(((pkey,), pval))

        for x in pkey:
            lookup[x].update(range(len(min_sums), len(min_sums) + len(valid)))
        for idx in valid:
            comb, val = min_sums[idx]
            for key in comb:
                for x in key:
                    lookup[x].add(len(min_sums))
            nset.add(len(min_sums))
            min_sums.append((comb + (pkey,), val + pval))
            if len(comb) == m - 1 and (not min_key or min_val > val + pval):
                min_key, min_val = min_sums[-1]

        if min_key:
            if not extra_runs: break
            extra_runs -= 1

    for pkey, pval in pairs:
        valid = set(nset)
        for x in pkey:
            valid -= lookup[x]

        for idx in valid:
            comb, val = min_sums[idx]
            if len(comb) < m - 1:
                nset.remove(idx)
            elif min_val > val + pval:
                if all(x in tuple(k for c in comb for k in c) + pkey for x in
                       required_keys):
                    min_key, min_val = comb + (pkey,), val + pval
    return min_key, min_val


# def greedy_solve(const_dict, n, m, extra_runs=10, check_factor=2,
#                  required_keys = []):
#     m = 2
#     pairs = sorted(const_dict.items(), key=lambda x: x[1])
#     print("Sorted Pairs:")
#     for item in pairs:
#         print(item)
#
#
#     lookup = [set([]) for _ in range(n)]
#     nset = set([])
#     print("Initial lookups")
#     print(lookup)
#     print("")
#
#     min_sums = []
#     min_key, min_val = None, None
#     print("Go through all pairs: \n")
#     for i, (pkey, pval) in enumerate(pairs):
#         print(f"For pair {pairs[i]}: \n")
#         print("Check for valid")
#
#         valid = set(nset)
#         print(f'Valid = {valid} \n')
#
#         for x in pkey:
#
#             print(f'For {x}')
#             #print(f'lookup[x] is originally {lookup[x]}')
#             valid -= lookup[x]
#             lookup[x].add(len(min_sums))
#             print(f'Valid becomes: {valid}')
#             print(f'len(min_sums) is {len(min_sums)}')
#             print(f'lookup[x] adds above, becoming: {lookup[x]} \n')
#
#
#
#         nset.add(len(min_sums))
#         min_sums.append(((pkey,), pval))
#         print(f'nset adds min sums, becoming {nset}')
#         print(f'min_sums appens {((pkey,), pval)}')
#
#         for x in pkey:
#             lookup[x].update(
#                 range(len(min_sums), len(min_sums) + len(valid)))
#
#         for idx in valid:
#             comb, val = min_sums[idx]
#             for key in comb:
#                 for x in key:
#                     lookup[x].add(len(min_sums))
#             nset.add(len(min_sums))
#             min_sums.append((comb + (pkey,), val + pval))
#             if len(comb) == m - 1 and (not min_key or min_val > val + pval):
#             #     if all(x in tuple(k for c in comb for k in c) + pkey for x in
#             #         required_keys):
#                 min_key, min_val = min_sums[-1]
#
#         if min_key:
#             if not extra_runs: break
#             extra_runs -= 1
#
#     for pkey, pval in pairs[:int(check_factor * i)]:
#         valid = set(nset)
#         for x in pkey:
#             valid -= lookup[x]
#
#         for idx in valid:
#             comb, val = min_sums[idx]
#             if len(comb) < m - 1:
#                 nset.remove(idx)
#             elif min_val > val + pval:
#                 # if all(x in tuple(k for c in comb for k in c) + pkey for x in
#                 #     required_keys):
#                 min_key, min_val = comb + (pkey,), val + pval
#     return min_key, min_val

def dp_solve(const_dict, n, m):

    lookup = {comb: (comb,) for comb in const_dict.keys()}

    keys = set(range(n))
    for size in range(8, 4 * m + 1, 4):
        for key_total in combinations(keys, size):
            key_set = set(key_total)
            min_keys = (key_total[:4], key_total[4:])
            min_val = const_dict[min_keys[0]] + const_dict[min_keys[1]]

            key1, key2 = min(zip(combinations(key_total, 4), reversed(
                list(combinations(key_total, size - 4)))),
                             key=lambda x: const_dict[x[0]] + const_dict[
                                 x[1]])

            k = tuple(sorted(x for x in key1 + key2))
            const_dict[k] = const_dict[key1] + const_dict[key2]
            lookup[k] = lookup[key1] + lookup[key2]

    key, val = min(((key, val) for key, val in const_dict.items() if
                    len(key) == 4 * m), key=lambda x: x[1])
    return lookup[key], val

    # courts = 3
    #
    # scores = []
    #
    # t = 0
    # for combo in combos_total[courts-1][1]:
    #     t4 = time.time()
    #     new_court = (players[combo[0][0]].name, players[combo[0][
    #         1]].name,
    #                  players[combo[1][0]].name, players[combo[1][1]].name)
    #     t5 = time.time()
    #     t += t5-t4
    #     scores.append(sum([scores_dict[frozenset(new_court)]]))
    #
    # print(f'{t} to get the player names')
    #
    # t4 = time.time()
    # print(f'{t4-t3} to add the combos')



    scores = []
    # for combo in scores_dict:
    #     #scores.append(scores_dict[combo])
    #     for other_combo in scores_dict:
    #         if other_combo.isdisjoint(combo):
    #             #scores[-1] += scores_dict[other_combo]
    #             for third_combo in scores_dict:
    #                 both = frozenset().union([combo, other_combo])
    #                 if third_combo.isdisjoint(both):
    #                     pass
    #                     #scores[-1] += scores_dict[third_combo]
    # t4 = time.time()
    # print(f'{t4-t3} to add up combos')

def best_score_3(combo, players):
    '''From four numbers, find the matchup with the lowest score.
    Add the combo as a key to two dictionaries: one the best combo,
    the other the score of said result'''
    scores = []
    three_combos = find_combos_of_four(combo)

    for com in three_combos:
        scores.append(score_court(com, players))

    new_court = (players[combo[0]].name, players[combo[1]].name,
                 players[combo[2]].name, players[combo[3]].name)

    # consider frozenset(combo) for alternative method
    # got the scores with all the names.
    index, scores_dict[frozenset(new_court)] = min(enumerate(scores),
                                    key=operator.itemgetter(1))
    # try making best_combos[frozenset(combo)]
    best_combos[combo] = three_combos[index]
    # best_combos[combo] = three_combos[index]

# def best_score_2(combo):
#     '''From four players, find the matchup with the lowest score.
#     Add the combo as a key to two dictionaries: one the best combo,
#     the other the score of said result'''
#     scores = []
#     three_combos = find_combos_of_four(combo)
#
#     for com in three_combos:
#         nums = score_court
#         scores.append(score_court_2(com))
#
#     index, scores_dict[combo] = min(enumerate(scores),
#     #                                key=operator.itemgetter(1))
#     best_combos[combo] = three_combos[index]
def best_score_2(combo, trial_players):
    '''From four numbers, find the matchup with the lowest score.
    Add the combo as a key to two dictionaries: one the best combo,
    the other the score of said result'''
    scores = []
    three_combos = find_combos_of_four(combo)

    for com in three_combos:
        scores.append(score_court_2(com, trial_players))

    # consider frozenset(combo) for alternative method
    index, scores_dict[combo] = min(enumerate(scores),
                                    key=operator.itemgetter(1))
    # try making best_combos[frozenset(combo)]
    best_combos[combo] = three_combos[index]
    # best_combos[combo] = three_combos[index]


def score_court_2(court, trial_players, explain = False):
    ''' Returns the "score" of a game, where "trial_players" is a list of
     player objects and "court" is a pair of tuples, representing indices
     of those players'''
    global score_num
    score_num +=1

    score = 0
    # Create the court using the indices from "court" on "trial_players"
    # Unpacked for easier referencing
    new_court = [trial_players[court[0][0]], trial_players[court[0][1]],
                 trial_players[court[1][0]], trial_players[court[1][1]]]

    for player in new_court:
        # games with more deserving players -> lower cost
        # tricky to come up with. Convoluted way of keeping sign.
        score -= 10 * ((abs(player.desert) ** 1.5) * sign(
            player.desert))
        # games with players on more times in a row -> higher cost
        # assumption that stronger players = fitter = less tired?
        # some kind of log is better?
        score += ((15-player.ability)/2)*(
                player.consecutive_games_on**1.5)
        # fraction ?

        #hackish ways of people players on/off. prefer alternative

        if player.keep_on:
            score -= 10**10
        elif player.keep_off:
            score += 10**10
        else:
            pass
           #score -= (1000*player.time_since_last)

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
            # count = 1
            # base_score = 0
            # for i, game in enumerate(player.played_against):
            #     if o_player in game:
            #         base_score += scoring_vars[('Mixing', profile)] * 2 * (
            #         (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
            #         count += 0.2
            # for i, game in enumerate(player.played_with):
            #     if o_player in game:
            #         base_score += scoring_vars[('Mixing', profile)] * (
            #                     1 / (1 + discount_rate) ** (
            #                          player.total_games - i - 1))
            #         count += 0.1
            # #"Count" is a means of pseudo-exponentiation - i.e. we want it
            # #to be proportionally worse to play someone three times in a row
            # # than twice in a row
            # adjusted_score = base_score * (count)

            new_score = scoring_vars[('Mixing',
                                      profile)]*player.opp_histories[
                o_player]


            if explain:
                if player.name == "Henry":
                    # print(f'(Henry score with opponent is {adjusted_score}')
                    print(f'(Henry new score with opponent is {new_score}')

            #score += adjusted_score
            score += new_score
            # Subtract affinity variable from score
            for aff in player.opponent_affinities:
                if aff[0] == o_player.name:
                    aff_multiplier = level_dict[aff[1]]
                    score -= aff_multiplier*(scoring_vars[('Affinity',
                                                           profile)])
                    break

        for o_player in partner:  # there's only 1 partner, so loop seems
             # silly?
        #     count = 1
        #     base_score = 0
        #     for i, game in enumerate(player.played_against):
        #         if o_player in game:
        #             base_score += scoring_vars[('Mixing', profile)] * (
        #                         1 / (1 + discount_rate) ** (
        #                             player.total_games - i - 1))
        #             count += 0.1
        #     for i, game in enumerate(player.played_with):
        #         if o_player in game:
        #             base_score += scoring_vars[('Mixing', profile)] * 3 * (
        #             (1 / (1 + discount_rate) ** (player.total_games - i - 1)))
        #             count += 0.2
        #
        #     adjusted_score = base_score * (count)

            new_score = scoring_vars[('Mixing',
                                      profile)]*player.partner_histories[
                o_player]

            if explain:
                if player.name == "Henry":
                    # print(f'(Henry score with partner is {adjusted_score}')
                    print(f'(Henry new score with opponent is {new_score}')
            #score += adjusted_score
            score += new_score

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












