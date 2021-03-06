import b_scorer
import b_sessions
import random
import datetime
import csv
import time
import numpy as np
import pickle

# import pandas as pd
from datetime import datetime, timedelta

import player_probs as pp


def black_test():

    for i in range(4):
        print("hello, world")


def initialise():

    # for player in b_scorer.absent_players:
    for player in b_scorer.every_player:
        try:
            if random.random() < pp.arrival_probs[player.name]:
                b_scorer.add_player(player)
        except KeyError:
            continue
    # print(len(b_scorer.all_current_players))
    if len(b_scorer.all_current_players) < 4 * len(b_scorer.courts):
        # print("Less than 12!")
        random.shuffle(b_scorer.absent_players)
        # print(len(b_scorer.absent_players))
        count = 0
        while len(b_scorer.all_current_players) < 4 * len(b_scorer.courts):
            # print(f'Now {len(b_scorer.all_current_players)} players!')
            try:
                player = b_scorer.absent_players[count]
                if random.random() < pp.arrival_probs[player.name]:
                    b_scorer.add_player(player)
                    # print(f'Added {player.name}!')
                    # print(f'Now {len(b_scorer.all_current_players)}!')
            except KeyError:
                pass
            if count > len(b_scorer.absent_players):
                count = 0
                print("Needed the count!")
            else:
                count += 1
    #
    #     #print(f"Now {len(b_scorer.all_current_players)}!")
    # print(len(b_scorer.all_current_players))


def initialise_2(max):
    while len(b_scorer.all_current_players) < max:
        add_players_by_arrival(max)

def initialise_3(num):
    b_scorer.init_fake_players(num)
    for player in b_scorer.every_player:
        b_scorer.add_player(player)


def add_players_by_arrival(max):
    random.shuffle(b_scorer.absent_players)
    for player in b_scorer.absent_players:
        try:
            if random.random() < pp.arrival_probs[player.name]:
                b_scorer.add_player(player)
        except KeyError:
            pass
        if len(b_scorer.all_current_players) >= max:
            break

def get_ability_stats(game):
    diff, seg = b_scorer.get_game_stats(game)
    ability_diffs.append(diff)
    ability_segs.append(seg)


def simulate():

    cost = b_scorer.generate_new_game()

    for game in b_scorer.courts:
        get_ability_stats(game)

    # every_cost.append(cost)
    b_scorer.confirm_game()
    b_scorer.update_desert()
    return cost


def simulate_session(trials):
    # print("Start session, before init")
    # print(len(b_scorer.every_player))
    # print(len(b_scorer.absent_players))
    # print(len(b_scorer.bench))
    initialise_2(18)
    #initialise_3()
    # print("Start session, after init")
    # print(len(b_scorer.every_player))
    # print(len(b_scorer.absent_players))
    # print(len(b_scorer.bench))


    costs = []
    for i in range(trials):
        cost = simulate()
        costs.append(cost)


    every_session.append(b_scorer.today_session)
    # need to make this easier

    date = datetime.now().date()
    start_time = datetime.now().time()
    b_scorer.today_session = b_sessions.Session(date, start_time)
    b_scorer.empty_courts()
    b_scorer.total_rounds = 0

    b_scorer.all_current_players = []
    # player not in all_current_players would duplicate it
    b_scorer.absent_players = [player for player in b_scorer.every_player]
    b_scorer.bench = b_scorer.all_current_players[:]


    b_scorer.save_and_quit(pickling=False)

    #
    # print("End of session")
    # print(len(b_scorer.every_player))
    # print(len(b_scorer.absent_players))
    # print(len(b_scorer.bench))

    return costs


# How often is a game balanced?
def balance_test():
    balances = []

    for session in every_session:
        for round in session.games:
            for court in round:
                abilities = [player.ability for player in court]
                balance = abs(sum(abilities[0:2]) - sum(abilities[2:4]))
                balances.append(balance)

    print(balances.count(0))
    print(balances.count(1))
    print(balances.count(2))
    print(balances.count(3))


# How ability segregated?
def ability_seg_test():
    pass


# How often does a player get a game stronger than another?
def alternation_test():
    pass


def mixing_test():
    for session in every_session:
        for round in session.games:
            for court in round:
                pass


def individual_player_test():
    pass
    # for session in every_session:


def export_game_data():

    game_file = open("{}.csv".format("Smart Shuffle 10"), "w", newline="")

    with game_file:
        writer = csv.writer(game_file)

        writer.writerow(["Date", "Round No", "Court No", "Space No", "Name", "Ability"])

        for i, session in enumerate(every_session):
            if len(session.games) > 0:
                for j, game in enumerate(session.games):
                    for k in range(len(b_scorer.courts)):
                        for l in range(4):
                            try:
                                writer.writerow(
                                    [
                                        session.date + timedelta(days=i),
                                        j + 1,
                                        k + 1,
                                        l + 1,
                                        game[k][l].name,
                                        game[k][l].ability,
                                    ]
                                )
                            except AttributeError:
                                writer.writerow(
                                    [session.date, j + 1, k + 1, l + 1, "NONE", 0]
                                )


every_session = []
every_cost = []
ability_diffs = []
ability_segs = []

print("Started!")
t1 = time.time()

for player in b_scorer.every_player:
    player.desert = 0

trials = 100
for i in range(trials):
    print(f"{i*(100/trials)}% finished!")
    # if i % 2 == 0:
    cost = simulate_session(10)
    # else:
    #     cost = simulate_session(9)
    # print(cost)
    every_cost.append(cost)
    # total = sum(every_cost[-1])
    # len = len(every_cost[-1])
    # print(total / len)
    # print(sum(every_cost[-1]))/len(every_cost[-1])

    # print(sum(every_cost[-1])
    # (len(every_cost[-1]))
#all_costs = []
\
# for cost in every_cost:
#     for a in cost:
#         print(a)


# for cost in every_cost:
#     all_costs.append((sum(cost) / len(cost)))
#     print(sum(cost) / len(cost))
# print(f"Average cost: {sum(all_costs)/len(all_costs)}")

print(f'Ability diffs: {ability_diffs}')
print(f'Ability segs: {ability_segs}')


print(f'Mean of ability diffs: {sum(ability_diffs)/len(ability_diffs)}')
a = np.array(ability_diffs)
print(f'95th percentile of ability diffs: {np.percentile(a,95)}')
print(f'Max of ability diffs: {max(ability_diffs)}')
print('')

print(f'Mean of ability segs: {sum(ability_segs)/len(ability_segs)}')
b =np.array(ability_segs)
print(f'95th percentile of ability segs: {np.percentile(b,95)}')
print(f'Max of ability segs: {max(ability_segs)}')


# b_scorer.print_desert()
# print(sum(every_cost[])/len(every_cost))

# for player in b_scorer.every_player:
#    print((player.court_2_attr / 0.3))

#export_game_data()

t2 = time.time()
print(f"Took {round(t2-t1)} seconds!")

# print(every_cost)
cost_pickle = open('cost_pickle.obj', 'wb')
pickle.dump(every_cost, cost_pickle)
cost_pickle.close()

print("Pickled!")

# pickle_in = open("cost_pickle.obj","rb")
# c = pickle.load(pickle_in)
# print(c)
