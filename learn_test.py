from numpy import random
from math import log

def learn(i, const=15,var=8):
    return const+(var*log(i))

def new_learn(ability, margin, games_played, const, var):
    return ability + (margin/learn(games_played, const, var))

def simulate_new_player(ability, const, var):

    margins = []

    a = ability
    old_a = a
    #print("Starting:", a)

    for i in range(70):

        margin = round((5-old_a)*4 + 4*random.normal(0))
        old_a = a
        margins.append(abs(margin))

        while abs(margin) < 2.0:
            if random.random() >0.5:
                margin += 1
            else:
                margin -= 1

        a = new_learn(a, margin, i + 1, const, var)
        #print(f"Round {i + 1}. Margin was {margin}")
        #print(f'Ability updated to {a} \n')
        #a += random.normal(0)/20 # random change in ability

    return sum(margins)/len(margins)
    #return margins[1]

def simulate_diff_const(const, var):
    meta_margins = []
    for i in range(30000):
        meta_margins.append(simulate_new_player(5 + random.normal(0),
                                                const, var))

    return sum(meta_margins)/len(meta_margins)

# cost_dict = {}
#
#
# for const in range(12,13):
#     for var in range(6,13):
#         result = simulate_diff_const(const, var)
#         cost_dict[(const,var)] = result
#         print(f'Const: {const}. Var {var}. Result: {result}')
#
# print(sorted(cost_dict, key=cost_dict.get))
#
#
#
# #simulate_new_player(5,15,8)
#
n




