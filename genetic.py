'''Be smarted about selecting orange combos'''

import random
from itertools import combinations
from numpy import sign

def sort_by_deservedness(players):
    return sorted(players, key=lambda x: x.desert, reverse=True)

def desert_score(players):
    tolerance_score = 0
    for player in players:
        # games with more deserving players -> lower cost
        # tricky to come up with. Convoluted way of keeping sign.
        tolerance_score -= 10 * ((abs(player.desert) ** 1.5) * sign(
            player.desert))

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

def initialise(oranges, no_oranges, no_candidates):
    #oranges = ([p.name for p in oranges])
   #print(no_oranges)

    if len(oranges)<13:
        orange_list = list(combinations(oranges,no_oranges))
    else:
        return []

    candidates = []

    indexes = random.sample(range(len(orange_list)), no_candidates)

    for i in range(no_candidates):
        new_candidate = set()
        # stop duplicates. Could cause performance issues if scaled up?

        new_candidate.update(orange_list[indexes[i]])
            #new_candidate.update(oranges[:no_oranges])
        candidates.append(new_candidate)

    #print(candidates)
    return candidates

def initialise_deserve(oranges, no_oranges, no_candidates):
    '''Create initial candidates, sorted by most deserving'''
    candidates = []

    oranges_2 = sort_by_deservedness(oranges)
    orange_combos = list(combinations(oranges_2, no_oranges))
    sorted_oranges = sorted(orange_combos, key=desert_score)
    for i in sorted_oranges:
        print(desert_score(i))
        print('')

    print(len(sorted_oranges))
    print(no_candidates)
    # If only a few combos
    if len(sorted_oranges) <= no_candidates:
        for cand in sorted_oranges:
            candidates.append(set(cand))
        print("Too few!")
        print(candidates)
        return candidates

    half_list = range(int(len(sorted_oranges) / 2))
    indexes = random.sample(half_list, no_candidates)
    print(indexes)
    #@todo make sample work for indexes

    for i in range(no_candidates):
        new_candidate = set()
        new_candidate.update(sorted_oranges[indexes[i]])
            #new_candidate.update(oranges[:no_oranges])
        candidates.append(new_candidate)
    # # print(candidates)
    # return candidates
    for c in candidates:
        print([p.desert for p in c])


def mutate(candidate, oranges, mutationRate):

    remaining = set(oranges).difference(set(candidate))
    new_candidate = set()
    mutated = False
    for player in candidate:
        if random.random() < mutationRate:
            added_player = random.sample(remaining,1)[0]
            remaining.remove(added_player)
            new_candidate.add(added_player)
            mutated = True
        else:
            new_candidate.add(player)
            #print("Not mutated!")
    if mutated:
        return frozenset(new_candidate)
    else:
        return False





