import b_scorer
import b_sessions
import random
import datetime
from datetime import datetime

def initialise():
    random.shuffle(b_scorer.every_player)
    for player in b_scorer.every_player[0:18]:
        b_scorer.add_player(player)

def simulate():
    b_scorer.generate_new_game()
    b_scorer.confirm_game()

def simulate_session():
    initialise()
    for i in range(10):
        simulate()
    every_session.append(b_scorer.today_session)
    b_scorer.save_and_quit(pickling=False)
    # need to make this easier
    date = datetime.now().date()
    start_time = datetime.now().time()
    b_scorer.today_session = b_sessions.Session(date, start_time)
    b_scorer.empty_courts()
    b_scorer.every_player = b_scorer.bench
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
    pass

def individual_player_test():
    pass
    # for session in every_session:



every_session = []











