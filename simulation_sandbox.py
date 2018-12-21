import b_scorer
import b_sessions
import random
import datetime
import csv
import time
#import pandas as pd
from datetime import datetime, timedelta
import player_probs as pp



def initialise():
    for player in b_scorer.absent_players:
        try:
            if random.random() < pp.arrival_probs[player.name]:
                b_scorer.add_player(player)
        except KeyError:
            continue
    #print(len(b_scorer.all_current_players))
    if (len(b_scorer.all_current_players)) <12:
        #print("Less than 12!")
        random.shuffle(b_scorer.absent_players)
        #print(len(b_scorer.absent_players))
        count = 0
        while len(b_scorer.all_current_players) <12:
            #print(f'Now {len(b_scorer.all_current_players)} players!')
            try:
                player = b_scorer.absent_players[count]
                if random.random() < pp.arrival_probs[
                    player.name]:
                    b_scorer.add_player(player)
                    #print(f'Added {player.name}!')
                    #print(f'Now {len(b_scorer.all_current_players)}!')
            except KeyError:
                pass
            if count > len(b_scorer.absent_players):
                count = 0
                print("Needed the count!")
            else:
                count +=1

        #print(f"Now {len(b_scorer.all_current_players)}!")



def simulate():
    b_scorer.generate_new_game()
    b_scorer.confirm_game()

def simulate_session(trials):
    initialise()
    for i in range(trials):
        simulate()
    every_session.append(b_scorer.today_session)
    b_scorer.save_and_quit(pickling=False)
    # need to make this easier
    date = datetime.now().date()
    start_time = datetime.now().time()
    b_scorer.today_session = b_sessions.Session(date, start_time)
    b_scorer.empty_courts()
    b_scorer.every_player = b_scorer.bench + b_scorer.absent_players
    b_scorer.absent_players = b_scorer.every_player
    b_scorer.bench = []
    b_scorer.all_current_players = []
    b_scorer.total_rounds = 0

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

    game_file = open('{}.csv'.format("simulate_csv"), 'w', newline='')

    with game_file:
        writer = csv.writer(game_file)

        writer.writerow(['Date', "Round No", "Court No", "Space No", "Name",
                         "Ability"])

        for i, session in enumerate(every_session):
            if len(session.games) > 0:
                for j, game in enumerate(session.games):
                    for k in range(3):
                        for l in range(4):
                            try:
                                writer.writerow([session.date + timedelta(
                                    days=i), j+1, k+1, l+1,
                                             game[k][l].name, game[k][
                                    l].ability])
                            except AttributeError:
                                writer.writerow([session.date, j + 1, k+1,
                                                 l + 1,
                                                 "NONE", 0])

every_session = []

print("Started!")
t1 = time.time()

for i in range(1000):
    if i%100 == 0:
        print(f'{i/100}% finished!')
    simulate_session(10)

export_game_data()

t2 = time.time()
print(f'Took {t2-t1}!')














