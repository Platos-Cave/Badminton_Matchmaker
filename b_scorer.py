'''Creates players and courts, has functions for selecting which
players are due on, starting and confirming games.'''

import random
import pickle
import enumerate_b
import b_sessions
import datetime

# PYBRANCH

class Player:
    def __init__(self, name, sex, ability,
                 partner_affinities=[], opponent_affinities=[]):
        self.name = name
        self.sex = sex
        self.ability = ability  # An integer from 1-9 (1 being weakest)

        # Other players this player likes to be partnered with/oppose
        self.partner_affinities = partner_affinities
        self.opponent_affinities = opponent_affinities

        self.total_games = 0
        # if a player arrives late, add extra games for game priority purposes
        self.penalty_games = 0
        # will be the sum of the above two.
        self.adjusted_games = 0
        # No. of rounds since the player last had a game. 0 = was on last round
        self.time_since_last = 0
        # who this player's partners have been this night
        self.played_with = []
        # who this player's opponents have been this night
        self.played_against = []

        # user modifiable notes
        self.player_notes = ''

        # If True, player will not be selected in automatic game
        self.keep_off = False

    def update_game_count(self):
        self.total_games += 1
        self.adjusted_games += 1
        self.time_since_last = 0


class Court:
    def __init__(self):

        '''The spaces on the court where indices 0,1 is one side of the
        court, and 2,3 are the other.
        Seems like each side should be its own list?  But that makes it
        annoying to unpack'''
        self.spaces = [None, None, None, None]

    def view_players(self):

        print("Side One:")
        for player in self.spaces[0:2]:
            if player is not None:
                print("{}. ({} games total)".format(player.name,
                                                    player.adjusted_games))
            else:
                print("No Player")
        print("\nSide Two:")
        for player in self.spaces[2:4]:
            if player is not None:
                print("{}. ({} games total)".format(player.name,
                                                    player.adjusted_games))
            else:
                print("No Player")

    # return all players from this court to the bench
    def empty(self):

        bench.extend([i for i in self.spaces if i is not None])
        self.spaces = [None, None, None, None]

def find_most_off(lst):
    """Of a list of players, find those who have had the max games in a row
    off"""
    times = [player.time_since_last for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == max(times)]


def find_least_games(lst):
    """"Of a selection of players, find those who have played the least games.
    References "adjusted_games", as it accounts for a lateness penalty"""
    times = [player.adjusted_games for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == min(times)]

def get_ability(player):
    """To give a key for the next function to sort by ability. Unnecessary?
    Could use lambda?"""
    return player.ability

def select_players(shuffle_version):
    """ Starting with a blank list (trial_players), append players to this list
    until there are 12.

    Start with the players (players_most_due) who have had the
    most consecutive rounds off. If the combined length of them + trial_players
    is less than 12, append them to trial_players and repeat with with the
    remaining players.

    If it would exceed 12, then find the players from players_most_due who
    have had the least number of games through find_least_games. Repeat until
    the length of trial_players is exactly 12, or there are more players tied
    to be due on there are spaces.

    If there is a tie, there are two tie-breaking procedures, based on the
    shuffle_version. First, shuffle the due players. If shuffle_version is
    "Random", add them from the start of the list until there are 12, (soit's
    random). If shuffle_version is "Segregated", instead check if the players
    due on are stronger or weaker than the mean ability of all players.
    If they're stronger, then tie-break in order of descending ability from the
    strongest down. If they're weaker, tie-break in order of ascending
    ability from the weakest up.
    """

    # The players who have been selected by this function to go on the board.
    trial_players = []

    players_to_pick = [player for player in all_current_players if
                       player.keep_off is False]

    total_court_space = 12

    # While the queue of players to go on is not full
    while len(trial_players) < total_court_space:
        # taken = slots already filled
        taken = len(trial_players)

        # the indices of the players who've been off the longest so far
        players_most_due = find_most_off(players_to_pick)

        # If there are fewer players left who have have N games off than
        # there are slots remaining, add all of them to trial_players
        # e.g. if there are 2 players who've been off twice, and 3 slots left,
        # add them, then go back and check for players who are most due
        # again.'''

        if len(players_most_due) <= (total_court_space - taken):
            for player in players_most_due:
                trial_players.append(player)

        else:
            # If there are more players who have been waiting the same
            # number of games than slots left,
            # then add the players who have played the fewest games first

            players_with_least = find_least_games(players_most_due)

            #  If players with the least number of games fill the courts,
            # add them
            if len(players_with_least) <= (total_court_space - taken):
                for player in players_with_least:
                    trial_players.append(player)
            else:

                # To hopefully ensure tiebreaks are fair
                random.shuffle(players_with_least)

                if shuffle_version == "Random":
                    for i in range(total_court_space - taken):
                        trial_players.append(players_with_least[i])
                elif shuffle_version == "Segregated":
                    # players sorted from worst to best ability-wise
                    ability_sorted_players = sorted(players_with_least,
                                                    key=get_ability)

                    # See if the players due on are weaker/stronger than average
                    all_abilities = sum([player.ability for player in
                                         all_current_players]) / len(
                        all_current_players)
                    orange_abilities = sum([player.ability for player in
                                            players_with_least])
                    green_abilities = sum([player.ability for player in
                                           trial_players])

                    # A fairly inelegant test for whether the current people on
                    # are stronger or weaker than average
                    try:
                        if len(all_current_players) < 24:
                            test_abilities = green_abilities / len(
                                trial_players)
                        else:  # what the hell is this formatting?
                            test_abilities = (
                                                     orange_abilities + green_abilities) / (
                                                     len(trial_players) + len(
                                                 players_with_least))
                    # If no green players, then treat it as a tie
                    except ZeroDivisionError:
                        test_abilities = all_abilities

                    # If the players on are  worse than average, put the
                    # worst players on
                    if test_abilities < all_abilities:
                        for i in range(total_court_space - taken):
                            trial_players.append(ability_sorted_players[i])
                    elif test_abilities > all_abilities:  # if better, put best
                        # players on
                        for i in range(total_court_space - taken):
                            trial_players.append(
                                ability_sorted_players[-(i + 1)])
                    else:  # tie
                        if random.random() > 0.5:
                            for i in range(total_court_space - taken):
                                trial_players.append(ability_sorted_players[i])
                        else:
                            for i in range(total_court_space - taken):
                                trial_players.append(
                                    ability_sorted_players[-(i + 1)])

        # The remaining players who are not yet selected
        players_to_pick = [i for i in players_to_pick if i not in trial_players]

    random.shuffle(trial_players)
    return trial_players


def colour_sorter(players):
    """Gives a colour to each player: light green if they're definitely due for
    the next game, red if they're definitely *not* due, orange if they're tied
    for being due. Used in the GUI for colouring the bench labels.
    Seems out of place/should be integrated into the select_players()
    function?"""
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

        players_left = [i for i in players_left if
                        i not in green_players and i not in orange_players]

    red_players = players_left

    for player in green_players:
        colour_dict[player] = "light green"
    for player in orange_players:
        colour_dict[player] = "orange"
    for player in red_players:
        colour_dict[player] = "red"

    return colour_dict

# Not needed in the GUI
def view_all_courts():
    for i, court in enumerate(courts):
        print("Court {} \n".format(i + 1))
        court.view_players()
        print('')

# Not needed in the GUI
def view_bench():
    print("Bench \n")
    for player in bench:
        print("{}. Waiting for: {} rounds. Total games: {}.".format(player.name,
                                                                    player.time_since_last,
                                                                    player.adjusted_games))

def generate_new_game():
    """Find the best game possible, then add those players to the courts"""

    if enumerate_b.scoring_vars['Shuffle'] == 1:
        best_game = (enumerate_b.find_best_game(select_players("Segregated")))
    else:
        best_game = (enumerate_b.find_best_game(select_players("Random")))

    empty_courts()

    for i, court in enumerate(best_game):
        for j, side in enumerate(court):
            for k, player in enumerate(side):
                if player is not None:
                    courts[i].spaces[(2 * j) + k] = player
                    if player in bench:
                        bench.remove(player)

def confirm_game():
    '''Update game counts, game history, save data'''
    for i, court in enumerate(courts):
        for j, player in enumerate(court.spaces):
            if player is not None:
                player.update_game_count()

        # Add played with/against to lists. Seems kind of suboptimal
        for player in court.spaces:
            if player is not None:
                if player in court.spaces[
                             0:2]:  # if player on side 1. Time to split list?
                    player.played_with.append(
                        [i for i in court.spaces[0:2] if i is not player])
                    player.played_against.append([i for i in court.spaces[2:4]])
                else:  # if on side #2
                    if player in court.spaces[
                                 2:4]:
                        player.played_with.append(
                            [i for i in court.spaces[2:4] if i is not player])
                        player.played_against.append(
                            [i for i in court.spaces[0:2]])

    for player in bench:
        player.time_since_last += 1

    for player in all_current_players:
        player.keep_off = False

    # not ideal to use globals, what but else should I do?    
    global total_rounds
    total_rounds += 1

    # New: trialing saving data
    today_session.games.append([courts[i].spaces for i in range(3)])

def test_mixing():
    '''View all the players and their (sorted) game history.
    Currently not usable in the GUI'''
    for player in all_current_players:
        played_with = (sorted(
            [player.name for game in player.played_with for player in game]))
        played_against = (sorted(
            [player.name for game in player.played_against for player in game]))
        print(player.name)
        print(played_with)
        print(played_against)


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

    # Reset games
    player.total_games = 0
    player.penalty_games = 0
    player.adjusted_games = 0
    player.time_since_last = 0

    # Update leaving times
    today_session.player_departures[player] = datetime.datetime.now().time()

def add_player(player):
    '''Add an already saved player to the game'''
    bench.append(player)
    absent_players.remove(player)

    if total_rounds == 0:
        average_games = 0  # avoid zero_division
        player.time_since_last = 1
    else:
        # Latecomers are counted as  having the same number of games as the
        # average player.
        # This seems fair in theory, but in practice seems to be unfairly high?
        average_games = sum(
            [player.adjusted_games for player in all_current_players]) / len(
            all_current_players)
        player.time_since_last = 1

    player.penalty_games = average_games
    player.adjusted_games += average_games
    all_current_players.append(player)
    today_session.player_arrivals[player] = datetime.datetime.now().time()


def empty_courts():
    for court in courts:
        court.empty()

def save_and_quit():
    """Reset everything only when exited properly.
    Otherwise, you can reload your previous state."""

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

    # When quitting, blank the data
    pickle_in = open('board_data.obj', 'wb')
    board_data = {}
    pickle.dump(board_data, pickle_in)
    pickle_in.close()


'''Creates an object for storing data about today's session.
 Could just have the time be one argument?'''
date = datetime.datetime.now().date()
start_time = datetime.datetime.now().time()
today_session = b_sessions.Session(date, start_time)

total_rounds = 0

courts = [Court() for i in range(3)]

"""36 sample players, four of each ability level from 1-9. The first letter 
of their names correspond to their numerical ability, in order to make 
ability differences more visualisable.

I've got a feeling it's not a good practice to initialise players like this. 
Maybe they should be in another file? Or initialised with a function?  
"""

Aaron = Player("Aaron", "Male", 1)
Andrew = Player("Andrew", "Male", 1)
Amanda = Player("Amanda", "Female", 1)
Anna = Player("Anna", "Female", 1)
Barry = Player("Barry", "Male", 2)
Bill = Player("Bill", "Male", 2)
Beth = Player("Beth", "Female", 2)
Bob = Player("Bob", "Male", 2)
Caleb = Player("Caleb", "Male", 3)
Calvin = Player("Calvin", "Male", 3)
Cindy = Player("Cindy", "Female", 3, partner_affinities=["Charles"])
Charles = Player("Charles", "Male", 3, partner_affinities=["Cindy"],
                 opponent_affinities=["David", "Edward"])
David = Player("David", "Male", 4, opponent_affinities=["Charles"])
Derek = Player("Derek", "Male", 4)
Denise = Player("Denise", "Female", 4)
Doris = Player("Doris", "Female", 4)
Edward = Player("Edward", "Male", 5, opponent_affinities=["Charles"])
Elliot = Player("Elliot", "Male", 5)
Emma = Player("Emma", "Female", 5)
Erin = Player("Erin", "Female", 5)
Fiona = Player("Fiona", "Female", 6, partner_affinities=["Felicity"],
               opponent_affinities=["Felicity"])
Felicity = Player("Felicity", "Female", 6, partner_affinities=["Fiona"],
                  opponent_affinities=["Fiona"])
Flynn = Player("Flynn", "Male", 6)
Fred = Player("Fred", "Male", 6)
Gary = Player("Gary", "Male", 7)
George = Player("George", "Male", 7)
Georgina = Player("Georgina", "Female", 7)
Gordon = Player("Gordon", "Male", 7)
Hannah = Player("Hannah", "Female", 8, partner_affinities=["Ian"])
Harry = Player("Harry", "Male", 8)
Heather = Player("Heather", "Female", 8)
Hunter = Player("Hunter", "Male", 8)
Ian = Player("Ian", "Male", 9, partner_affinities=["Hannah"],
             opponent_affinities=["Isaac"])
Igor = Player("Igor", "Male", 9)
Indiana = Player("Indiana", "Male", 9)
Isaac = Player("Isaac", "Male", 9, opponent_affinities=["Ian"])

"""If you have saved players, pickle them in. Otherwise, use the default 
players"""

try:
    pickle_in = open("every_player_pi_2.obj","rb")
    every_player = pickle.load(pickle_in)
    pickle_in.close()
except FileNotFoundError:
    every_player = [Aaron, Andrew, Amanda, Anna, Barry, Beth, Bill, Bob, Caleb,
                Calvin, Cindy, Charles, David, Derek, Denise, Doris, Edward,
                Elliot, Emma, Erin, Fiona, Felicity, Flynn, Fred, Gary,
                George, Georgina, Gordon, Hannah, Harry, Heather, Hunter,
                Ian, Igor, Indiana, Isaac]

"""Ditto but for session data"""
try:
    session_data = open('badminton_session_data.obj', 'rb')
    all_sessions = pickle.load(session_data)
    session_data.close()
except FileNotFoundError:
    all_sessions = b_sessions.all_sessions

all_current_players = []
# player not in all_current_players would duplicate it
absent_players = [player for player in every_player if player.name not in
                  [player.name for player in all_current_players]]

# Bench starts full
bench = all_current_players[:]

random.shuffle(bench)