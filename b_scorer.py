'''Creates players and courts, has functions for selecting which
players are due on, starting and confirming games.'''

import random
import pickle
import enumerate_b
import b_sessions
import datetime

# MASTER 


class Player:

    def __init__(self, name, sex, ability):
        self.name = name
        self.sex = sex
        self.ability = ability   # An integer from 1-9 (1 being weakest)

        self.total_games = 0 
        self.penalty_games = 0   # if a player arrives late, add extra games for purposes of adding them to courts
        self.adjusted_games = 0  # will be the sum of the above two.
        self.time_since_last = 0 # the number of rounds since the player last had a game. 0 = was on last round
        self.played_with = []    # who the player's partners have been this night
        self.played_against = [] # ditto, but against
        
        # Other players this player likes to be partnered with/oppose
        self.partner_affinities = []
        self.opponent_affinities = []

        self.player_notes = ''

        self.keep_off = False   # If True, player will not be selected in automatic game

    def update_game_count(self):
        self.total_games += 1 
        self.adjusted_games += 1
        self.time_since_last = 0


class Court:

    def __init__(self):

        '''The spaces on the court where indices 0,1 is one side of the court, and 2,3 are the other.
        Seems like each side should be its own list, but that makes it annoying to unpack'''
        self.spaces = [None, None, None, None]

    def view_players(self):

        print("Side One:")
        for player in self.spaces[0:2]:
            if player is not None:
                print("{}. ({} games total)".format(player.name, player.adjusted_games))
            else: 
                print("No Player")
        print("\nSide Two:")
        for player in self.spaces[2:4]:
            if player is not None:
                print("{}. ({} games total)".format(player.name, player.adjusted_games))
            else:
                print("No Player")

    # return all players from this court to the bench
    def empty(self):
        
        bench.extend([i for i in self.spaces if i is not None])
        self.spaces = [None, None, None, None]


    def empty_unpinned(self, number):
        #Currently unused, in start_new_game() for now
        pinned_spaces = [court.spaces for court in pin_courts]


'''Creates a  Could just have the time be one argument?'''
date = datetime.datetime.now().date()
start_time = datetime.datetime.now().time()
today_session = b_sessions.Session(date, start_time)


total_rounds = 0

courts = [Court() for i in range(3)]

# when players are manually added to a court, add them here
pin_courts = [Court() for i in range(3)]

# All of these should be in a new file, with placeholder names for code review purposes
Henry = Player("Henry", "Male", 5)
David = Player("David", "Male", 5)
Kieran = Player("Kieran", "Male", 5)
Bonnie = Player("Bonnie", "Female", 7)
Kelly = Player("Kelly", "Female", 7)
Dominic = Player("Dominic", "Male", 9)
Gary = Player("Gary", "Male", 9)
Desmond = Player("Desmond", "Male", 9)
Campbell = Player("Campbell", "Male", 9)
Tallat = Player("Tallat", "Male", 4)
Jack = Player("Jack", "Male", 3)
Gabrielle = Player("Gabrielle", "Female", 2)
Ram = Player("Ram", "Male", 6)
Sonom = Player("Sonom", "Female", 2)
Marion = Player("Marion", "Female", 5)
Zahid = Player("Zahid", "Male", 5)
Muti = Player("Muti", "Male", 5)
Stewart = Player("Stewart", "Male", 9)
Suzie = Player("Suzie", "Female", 1)
Cory = Player("Cory", "Male", 7)
RJ = Player("RJ", "Male", 8)
Sundeep = Player("Sundeep", "Male", 8)
Michael = Player("Michael", "Male", 5)
Adnan = Player("Adnan", "Male", 6)
Wilma = Player("Wilma", "Female", 1)


fakeplayers = [Player(i, "Male", i) for i in range (10)] + [Player(i, "Male", i) for i in range (10)]

Latecomer = Player("Latecomer", "Male", 5)
Long = Player("PlayerWithAReallyReallyReallyLongName", "Male", 5)

Henry.partner_affinities = ["David"]
Henry.opponent_affinities = ["David", "Kieran"]

David.partner_affinities = ["Henry"]
David.opponent_affinities = ["Henry", "Kieran"]

Kieran.opponent_affinities = ["Henry", "David"]

Bonnie.partner_affinities = ["Dominic"]
Bonnie.opponent_affinities = ["Kelly"]

Kelly.partner_affinities = ["Campbell"]
Kelly.opponent_affinities = ["Bonnie"]

Campbell.partner_affinities = ["Kelly"]

Dominic.partner_affinities = ["Bonnie"]


try:
    pickle_in = open("every_player_pi_2.obj","rb")
    every_player = pickle.load(pickle_in)
    pickle_in.close()
except FileNotFoundError:
    every_player = [Henry, David, Kieran, Bonnie, Kelly, Dominic, Gary, Desmond,
         Tallat, Jack, Gabrielle, Ram, Sonom, Marion, Zahid, Muti, Stewart,
         Suzie, Cory, Campbell, RJ, Sundeep, Michael, Adnan, Wilma]

try:
    session_data = open('badminton_session_data.obj', 'rb')
    all_sessions = pickle.load(session_data)
    session_data.close()
except FileNotFoundError:
    all_sessions = b_sessions.all_sessions


        

all_current_players = []
# player not in all_current_players would duplicate it
absent_players = [player for player in every_player if player.name not in [player.name for player in all_current_players]]

#Bench starts full
bench = all_current_players[:]

# For adding test players
# for i in range(10):
#    bench.append(Player("ROBOT " + str(i), "ROBOT", "ROBOTS ARE GENDERLESS", i))

random.shuffle(bench)

# Of a selection of players, find those who have had the max games in a row off
def find_most_off(lst):
    times = [player.time_since_last for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == max(times)]

# Of a selection of players, find those who have played the least games
# References "adjusted_games", as it accounts for a lateness penalty
def find_least_games(lst):
    times = [player.adjusted_games for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == min(times)]

# Chooses 12 players from those available who are due to go on
def select_players():

    # The players who have been selected by this function to go on the board.
    trial_players = []
    players_to_pick = [player for player in bench if player.keep_off is False]
    total_court_space = 12

    # While the queue of players to go on is not full
    while len(trial_players) < total_court_space:
        # taken = slots already filled
        taken = len(trial_players)

        # the players who've been off the longest so far
        players_most_due = find_most_off(players_to_pick)

        '''If there are fewer players left who have have N games off than
        there are slots remaining, add all of them to trial_players
        e.g. if there are 2 players who've been off twice, and 3 slots left,
        add them, then go back and check for players who are most due again.'''

        if len(players_most_due) <= (total_court_space - taken):
            for player in players_most_due:                                
                trial_players.append(player) 

        else:
            ''' If there are more players who have been waiting the same number of games than slots left,
             then add the players who have played the fewest games first''' 
            
            players_with_least = find_least_games(players_most_due)
                  
            #  If players with the least number of games fill the courts, add them 
            
            if len(players_with_least) <= (total_court_space - taken):
                for player in players_with_least:                                
                    trial_players.append(player)
            else:
                # Put remaining players on at random
                random.shuffle(players_with_least)
                for i in range(total_court_space - taken):
                    trial_players.append(players_with_least[i])

        
        # The remaining players who are not yet selected
        players_to_pick = [i for i in players_to_pick if i not in trial_players]

    # Shuffling the players mitigates any possible bias from their ordering
    random.shuffle(trial_players)
    return trial_players

# To give a key for another function to sort by ability. Unnecessary?
def get_ability(player):
    return player.ability

def select_players_v2():

    # Create some new courts to make simulated games with, so the real courts can be left alone
    #trial_courts = [Court() for _ in range(3)]
    # The players who have been selected by this function to go on the board. 
    trial_players = []

    # The players manually pinned to the board
    pinned_spaces = [court.spaces for court in pin_courts]
    pinned_players = [player for court in pinned_spaces for player in court if player is not None]
 
    pinned_length = len(pinned_players)
    

    # The players who aren't yet confirmed to be on or off yet.
    # Pinned players and kept off players are removed. Later, selected players will be removed.

    # For now, ignoring pins
    #players_to_pick = [player for player in bench if player.keep_off is False]
    players_to_pick = [player for player in bench if player.keep_off is False]  #if player not in pinned_players    

    total_court_space = 12 #- pinned_length

    # While the queue of players to go on is not full
    while len(trial_players) < total_court_space:
        # taken = slots already filled
        taken = len(trial_players)

        # the indices of the players who've been off the longest so far
        players_most_due = find_most_off(players_to_pick)
        #random.shuffle(players_most_due)

        
        '''If there are fewer players left who have have N games off than
        there are slots remaining, add all of them to trial_players
        e.g. if there are 2 players who've been off twice, and 3 slots left,
        add them, then go back and check for players who are most due again.'''

        
        if len(players_most_due) <= (total_court_space - taken):
            for player in players_most_due:                                
                trial_players.append(player) 

        else:
            ''' If there are more players who have been waiting the same number of games than slots left,
             then add the players who have played the fewest games first''' 
            
            players_with_least = find_least_games(players_most_due)
                  
            #  If players with the least number of games fill the courts, add them 
            
            if len(players_with_least) <= (total_court_space - taken):
                for player in players_with_least:                                
                    trial_players.append(player)
            else:

                # To hopefully ensure tiebreaks are fair
                random.shuffle(players_with_least)
                # players sorted from worst to best ability-wsie
                ability_sorted_players = sorted(players_with_least, key = get_ability)
                
                #See if the players due on are weaker or stronger than average  
                all_abilities = sum([player.ability for player in all_current_players])/len(all_current_players)
                try:            
                    green_abilities = sum([player.ability for player in trial_players])/len(trial_players)
                except ZeroDivisionError: # If no green players, then treat it as a tie
                    green_abilities = all_abilities

                #If the players on are worse than average, put the worst players on 
                if green_abilities < all_abilities:           
                    for i in range(total_court_space - taken):
                        trial_players.append(ability_sorted_players[i])
                elif green_abilities > all_abilities: # if better, put best players on
                    for i in range(total_court_space - taken):
                        trial_players.append(ability_sorted_players[-(i+1)])
                else: # tie
                    if random.random() > 0.5:
                        for i in range(total_court_space - taken):
                            trial_players.append(ability_sorted_players[i])
                    else:
                        for i in range(total_court_space - taken):
                            trial_players.append(ability_sorted_players[-(i+1)])


        # The remaining players who are not yet selected
        players_to_pick = [i for i in players_to_pick if i not in trial_players]

    random.shuffle(trial_players)
    return trial_players


'''Gives a colour to each player: light green if they're definitely due for 
the next game, red if they're definitely *not* due, orange if they're tied
for being due. Used in the GUI for colouring the bench labels. 
Seems out of place/should be integrated into the select_players() function?'''
def colour_sorter(players):

    players_left = players
    colour_dict = {}

    # If there are 12 or fewer players, then they're all "due"

    if len(players_left) < 13:
         for player in players_left:
            colour_dict[player] = "light green"
         return colour_dict

    # players due on
    green_players = []
    # players maybe due on
    orange_players = []
    # players definitely not due on
    red_players = []

    # Much the same as select_players()
    while len(green_players + orange_players) < 12:
        most_off = find_most_off(players_left)
        if len(most_off) <= (12 - len(green_players + orange_players)):
            for player in most_off:
                green_players.append(player)
        else:
            least_off = find_least_games(most_off)
            if len(least_off) <= (12 - len(green_players + orange_players)):
                for player in least_off:
                    green_players.append(player)
            else:
                for player in least_off:
                    orange_players.append(player)

        players_left= [i for i in players_left if i not in green_players and i not in orange_players]

    red_players = players_left

    for player in green_players:
        colour_dict[player] = "light green"
    for player in orange_players:
        colour_dict[player] = "orange"
    for player in red_players:
        colour_dict[player] = "red"

    return colour_dict

def view_all_courts():
    for i, court in enumerate(courts):
        print("Court {} \n".format(i + 1))
        court.view_players()
        print('')


def view_bench():
    print("Bench \n")
    for player in bench:
        print("{}. Waiting for: {} rounds. Total games: {}.".format(player.name,
                                                            player.time_since_last,
                                                            player.adjusted_games))

def generate_new_game():

    for i, court in enumerate(courts):
        bench.extend([p for p in court.spaces if p is not None])

    if enumerate_b.scoring_vars[4] == 1:
        best_game = (enumerate_b.find_best_game(select_players_v2()))
    else:
        best_game = (enumerate_b.find_best_game(select_players()))

    for i, court in enumerate(best_game):
        for j, side in enumerate(court):
            for k, player in enumerate(side):
                if player is not None:
                    courts[i].spaces[(2*j) + k] = player
                    if player in bench:
                        bench.remove(player)

def confirm_game():

    for i, court in enumerate(courts):
        for j, player in enumerate(court.spaces):
            if player is not None:
                
                player.update_game_count()

        #Add played with/against to lists. Seems kind of suboptimal
        for player in court.spaces:
            if player is not None:
                if player in court.spaces[0:2]: #if player on side 1. Time to split list?
                    player.played_with.append([i for i in court.spaces[0:2] if i is not player])
                    player.played_against.append([i for i in court.spaces[2:4]])
                else: #if on side #2
                    if player in court.spaces[2:4]: #if player on side 1. Time to split list?
                        player.played_with.append([i for i in court.spaces[2:4] if i is not player])
                        player.played_against.append([i for i in court.spaces[0:2]])                
          

    for player in bench:
        player.time_since_last += 1

    for player in all_current_players:
        player.keep_off = False

    # not ideal to use globals, what but else should I do?    
    global total_rounds
    total_rounds += 1

    #refresh the pin-courts
    global pin_courts
    pin_courts = [Court() for i in range(3)]

    # New: trialing saving data

    today_session.games.append([courts[i].spaces for i in range(3)])

# View all the players and their (sorted) game history.
# Could probably have more sophisticated tests

def test_mixing():

    for player in all_current_players:
##        played_with = (sorted([player.name for game in player.played_with for player in game]))
##        played_against = (sorted([player.name for game in player.played_against for player in game]))
##        print(player.name)
##        print(played_with)
##        print(played_against)
        pass
          

def remove_player(court_number, index, player):
    if court_number is not None:
        player = courts[court_number].spaces[index]
    # Update lists of players

    absent_players.append(player)
    all_current_players.remove(player)
    
    if court_number is None:
    # remove player from bench             
        bench.remove(player)                
    else:
        courts[court_number].spaces[index] = None

    # Reset games. (Should it be done this game?)   

    player.total_games = 0
    player.penalty_games = 0
    player.adjusted_games = 0
    player.time_since_last = 0  
        
    # Update leaving times
    today_session.player_departures[player] = datetime.datetime.now().time()

# Add an already saved player to the game
def add_player(player):

    bench.append(player)
    absent_players.remove(player)

    if total_rounds == 0:
        average_games = 0 #avoid zero_division
        player.time_since_last = 1
    else:
        # Latecomers are counted as having the same number of games as the average player
        # This seems fair in theory, but in practice seems to be unfairly high
        average_games = sum([player.adjusted_games for player in all_current_players])/len(all_current_players)
        player.time_since_last = 1

    player.penalty_games = average_games
    player.adjusted_games += average_games
    all_current_players.append(player)
    today_session.player_arrivals[player] = datetime.datetime.now().time()

def empty_courts():
    for court in courts:
        court.empty()

    global pin_courts
    pin_courts = [Court() for i in range(3)]
    
def empty_all():

    #not ideal to use global
    global bench
    global all_current_players
    global total_rounds

    for court in courts:
        court.empty()

    for player in bench:
        absent_players.append(player)
        
    bench = []
    
    all_current_players = []

    for player in absent_players:

        player.total_games = 0
        player.time_since_last = 0
        player.played_with = []
        player.played_against = []

    total_rounds = 0

# Reset everything only when exited properly.
# Otherwise, you can reload your previous state.
def save_and_quit():

    # Reset all the players
    for player in every_player:
        player.total_games = 0
        player.penalty_games = 0
        player.adjusted_games = 0
        player.time_since_last = 0
        player.played_with = []
        player.played_against = []
        player.keep_off = False

    # Save departure times
    for player in all_current_players:
        today_session.player_arrivals[player] = datetime.datetime.now().time()

    today_session.end_time = datetime.datetime.now().time()

    all_sessions.append(today_session)

    session_data = open('badminton_session_data.obj', 'wb')
    pickle.dump(all_sessions, session_data)
    session_data.close()

    #When quitting, blank the data
    pickle_in = open('board_data.obj', 'wb')
    board_data = {}
    pickle.dump(board_data, pickle_in)
    pickle_in.close()
