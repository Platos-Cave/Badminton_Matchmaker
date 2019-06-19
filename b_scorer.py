'''Creates players and courts, has functions for selecting which
players are due on, starting and confirming games.'''

import random
import pickle
import enumerate_b
import b_sessions
import datetime
from datetime import datetime
import operator
import time
from statistics import mean
from collections import defaultdict
from itertools import combinations
import new_smart_shuffle as nss
import genetic


#easily togglable test-mode with players with randomly created abilities
fake_players = False

class Player:
    def __init__(self, name, sex, ability, partner_affinities=[],
                 opponent_affinities=[], membership = "Casual"):
        self.name = name
        self.sex = sex
        self.ability = ability  # An integer from 1-10 (1 being weakest)
        self.ability_history = [ability]
        self.fitness = 2 #Default fitness level

        self.first_night = True

        # Other players this player likes to be partnered with/oppose
        # Newly updated to be (Player.name, Level) pairs, where Level is
        # (currently) Low/Medium/High
        self.partner_affinities = partner_affinities
        self.opponent_affinities = opponent_affinities

        self.affinity_for_newbies = False
        # membership status: Member or Casual. Had trouble making
        # backwards-compatible with pickle
        self.membership = membership
        self.money_owed = 0


        self.total_games = 0
        # if a player arrives late, add extra games for game priority purposes
        self.penalty_games = 0
        # will be the sum of the above two.
        self.adjusted_games = 0
        # No. of rounds since the player last had a game. 0 = was on last round
        self.time_since_last = 0
        # numbers of games in a row that have been played
        self.consecutive_games_on = 0
        # "old" time_since_last purely for undoing purposes
        self.old_tsl = 0
        # who this player's partners have been this night
        self.played_with = []
        # who this player's opponents have been this night
        self.played_against = []

        # NEW: for more efficient matching
        self.partner_histories = defaultdict(float)
        self.opp_histories = defaultdict(float)

        self.old_partner_histories = defaultdict(float)
        self.old_opp_histories = defaultdict(float)

        # how deserving is this player of another game?
        # a replacement for looking at "total games"

        # Brand new players start with a desert of 1, giving them likely an
        # extra game
        self.desert = 1
        self.old_desert = 1

        self.hunger = 0
        self.old_hunger = 0
        self.mean_game_abs = self.ability

        # Our second court has a projector, we want to ensure players don't
        # play too much on it, nor put strong players on it
        self.court_2_attr = 0
        self.old_court_2_attr = 0

        # user modifiable notes
        self.player_notes = ''

        # If True, player will not be selected in automatic game
        self.keep_off = False
        # If True, player will always be selected in automatic games
        self.keep_on = False
        # # If True, player is in manual game, and goes above Keep_On
        # self.manual_game = False

        self.paid_tonight = True

    def add_affinity(self, side, name, level):
        '''Given a side (partner/opponent), a name, and a level
        (Low/Medium/High), add/update that to the respective affinity list.'''
        if side == "partner":
            affs = self.partner_affinities
        elif side == "opponent":
            affs = self.opponent_affinities
        else:
            return NameError # is that right?


        # Uses list comprehension rather than loop - however, loses references
        affs = [(name,level) if player[0] == name else player for player in
                affs]


        # Add new affinity otherwise. Seems like I should be able to
        # integrate this with the flow of the above loop?
        if name not in [p[0] for p in affs]:
            affs.append((name,level))
      
        # Reassigning to the correct list. Seems inelegant
        if side == "partner":
            self.partner_affinities = affs
        elif side == "opponent":
            self.opponent_affinities = affs
        else:
            return NameError # is that right?


    def remove_affinity(self, name, side):
        '''Remove an affinity, so long as it exists'''
        if side == "partner":
            affs = self.partner_affinities
        elif side == "opponent":
            affs = self.opponent_affinities
        else:
            return NameError  # is that right?

        if name not in [p[0] for p in affs]: # error
            return NameError # is that right?
        else:
            affs = [p for p in affs if p[0] != name]
            # Again need to get reference back, seems annoying
            if side == "partner":
                self.partner_affinities = affs
            elif side == "opponent":
                self.opponent_affinities = affs
            else:
                return NameError


    def update_game_count(self):
        self.total_games += 1
        self.adjusted_games += 1
        self.old_consecutive_games_on = self.consecutive_games_on # for undoing
        self.consecutive_games_on +=1
        self.old_tsl = self.time_since_last # for undoing
        self.time_since_last = 0

    def update_when_benched(self):
        self.old_tsl = self.time_since_last  # for undoing
        self.time_since_last += 1
        self.old_consecutive_games_on = self.consecutive_games_on # for undoing
        self.consecutive_games_on = 0


    def recalculate_hunger(self, last_game_ab):
        '''Take the average ability of the last game the player was in,
        add it to the mean (a moving average), divide by 2.'''
        self.old_hunger = self.hunger
        self.old_mean_game_abs = self.mean_game_abs
        self.mean_game_abs = (self.mean_game_abs + last_game_ab)/2
        self.hunger = self.ability - self.mean_game_abs

    def undo_game(self, on_court):

        self.time_since_last = self.old_tsl
        self.consecutive_games_on = self.old_consecutive_games_on
        self.desert = self.old_desert

        if on_court:
            self.total_games -= 1
            self.adjusted_games -= 1
            self.hunger = self.old_hunger
            self.mean_game_abs = self.old_mean_game_abs
            self.partner_histories = self.old_partner_histories
            self.opp_histories = self.old_opp_histories
            self.court_2_attr = self.old_court_2_attr

            del self.played_against[-1]
            del self.played_with[-1]



        # if self.name == "David":
        #     keys = sum([v for v in self.opp_histories.values()])
        #     print(keys)


    def accumulate_fee(self):

        # put this somewhere else!
        # keys are a tuple of membership and day of the week)


        # first: check membership status
        # then check what the fee is for tonight for a given status
        # thus, need to have a means of saving fee levels for certain nights
        # basic version first: just assume it's $5 for everyone
        try:
            today = datetime.today().weekday()
            fee_key = (self.membership, today)

            # if this player has a membership that requires them to have money

            try:
                if fee_structure[fee_key] > 0:
                    self.paid_tonight = False

                self.money_owed += fee_structure[fee_key]
            except KeyError: # in case it's the wrong day/stuffed up
                pass


        except TypeError:
            print(self.money_owed)

    # pay tonight's fee only
    def pay_fee(self):

        today = datetime.today().weekday()
        fee_key = (self.membership, today)
        self.paid_tonight = True

        try:
            if self.name not in today_session.payments: # if already a payment
                today_session.payments[self.name] = (self.membership,
                                                 fee_structure[fee_key])
            else:
                today_session.payments[self.player.name] = \
                    (self.player.membership,
                     today_session.payments[self.player.name][1] +
                     (self.player.money_owed - owed))

        except KeyError:
            pass

        try:
            self.money_owed -= fee_structure[fee_key]
        except KeyError:  # in case it's the wrong day/stuffed up
            pass



class Court:
    def __init__(self):

        '''The spaces on the court where indices 0,1 is one side of the
        court, and 2,3 are the other.
        Seems like each side should be its own list?  But that makes it
        annoying to unpack'''
        self.spaces = [None, None, None, None]
        # If the game is to be made manually on this court
        self.manual = False
        self.old_manual = False

    def update_manual(self):
        self.old_manual = self.manual


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
    times = [player.time_since_last for player in lst if player]
    return [lst[i] for i, j in enumerate(times) if j == max(times)]

def find_least_consecutive(lst):
    """Of a list of players, find those who have played the least consecutive games in a row"""
    times = [player.consecutive_games_on for player in lst if player]
    return [lst[i] for i, j in enumerate(times) if j == min(times)]


def find_least_games(lst):
    """"Of a selection of players, find those who have played the least games.
    References "adjusted_games", as it accounts for a lateness penalty"""
    times = [player.adjusted_games for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == min(times)]

def find_most_deserving(lst):
    """Of a list of players, find those with the highest "deserving" score,
    which is similar to 'least games' in practice"""
    times = [player.desert for player in lst if player is not None]
    return [lst[i] for i, j in enumerate(times) if j == max(times)]


def get_ability(player):
    """To give a key for the next function to sort by ability. Unnecessary?
    Could use lambda?"""
    return player.ability



def select_players(shuffle_version, selectable, no_courts = 3):
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

    (Probably too long and should be split up)
    """

    # The players who have been selected by this function to go on the board.
    trial_players = []

    # Add kept on players
    for player in selectable:
        if player.keep_on:
            trial_players.append(player)

    # Ensure don't pick manual games
    for court in courts:
        if court.manual:
            for player in court.spaces:
                if player:
                    player.keep_off = True

    players_to_pick = [player for player in selectable if
                       not player.keep_off and not player.keep_on] # and not
                       #player.manual_game]


    total_court_space = 4*(no_courts) # should be 4*len(courts) for
    # extensibility


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

            if shuffle_version == "Smart":
                players_with_least = players_most_due

            else:
                players_with_least = find_least_games(players_most_due)



            #  If players with the least number of games fill the courts,
            # add them
            if len(players_with_least) <= (total_court_space - taken):
                for player in players_with_least:
                    trial_players.append(player)
            else:

                if shuffle_version in ("Random", "Smart"):

                    if shuffle_version == "Random":
                    # put players with least consecutive games on first
                        least_consec = find_least_consecutive(players_with_least)

                    else:
                        least_consec = players_with_least


                    if len(least_consec) <= (total_court_space - taken):
                        for player in least_consec:
                            trial_players.append(player)

                    else:
                    # To hopefully ensure tiebreaks are fair
                        random.shuffle(least_consec)

                        for i in range(total_court_space - taken):
                            trial_players.append(least_consec[i])

                elif shuffle_version == "Segregated":
                    # To hopefully ensure tiebreaks are fair
                    random.shuffle(players_with_least)
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
    # num = 4*len(courts)
    # players_left = players[:]
    colour_dict = {}
    #
    # # If there are 12 or fewer players, then they're all "due"
    if len(players) <= 4*(court_count):
        for player in players:
            if player.keep_off:
                colour_dict[player] = "gray"
            elif player.keep_on:
                colour_dict[player] = "white"
            else:
                colour_dict[player] = "light green"

        return colour_dict
    #
    # # players due on
    # green_players = []
    # # players maybe due on
    # orange_players = []
    # # players definitely not due on
    # red_players = []
    #
    # # Much the same as select_players()
    # while len(green_players + orange_players) <=  num:
    #     most_off = find_most_off(players_left)
    #     if len(most_off) <= (num - len(green_players + orange_players)):
    #         for player in most_off:
    #             green_players.append(player)
    #     else:
    #         least_off = find_least_games(most_off)
    #         if len(least_off) <= (num - len(green_players + orange_players)):
    #             for player in least_off:
    #                 green_players.append(player)
    #         else:
    #             for player in least_off:
    #                 orange_players.append(player)
    #
    #     players_left = [i for i in players_left if
    #                     i not in green_players and i not in orange_players]
    #
    # red_players = players_left
    green_players, orange_players, red_players = smart_select(players,
                                                            court_count)
    for player in green_players:
        colour_dict[player] = "light green"
    for player in orange_players:
        colour_dict[player] = "orange"
    for player in red_players:
        colour_dict[player] = "red"

    # Overrule colours with Keep On/Keep off:
    for player in players:
        if player.keep_off:
            colour_dict[player] = "gray"
        elif player.keep_on:
            colour_dict[player] = "white"


    return colour_dict

def smart_select(players, c_count=3):

    players_left = players[:]
    spaces = 4*c_count

    green_players = []
    orange_players = []
    red_players = []

    # Add kept on/off
    for player in players_left:
        if player.keep_on:
            green_players.append(player)
        if player.keep_off:
            red_players.append(player)

    # Could do some kind of pop() above instead?
    players_left = [i for i in players_left if
                    i not in green_players and i not in orange_players and i
                    not in red_players]

    if len(players_left + green_players) <= spaces:
        for player in players_left:
            green_players.append(player)
        # print([p.name for p in green_players])
        # print([p.name for p in orange_players])
        # print([p.name for p in red_players])
        for lst in green_players, orange_players, red_players:
            random.shuffle(lst)
        return (green_players, orange_players, red_players)

    while len(green_players + orange_players) <= spaces:
        if len(green_players) == spaces:
            break
        # Find most off
        most_off = find_most_off(players_left)
        if len(most_off) <= (spaces - len(green_players + orange_players)):
            for player in most_off:
                green_players.append(player)
        else:
            for player in most_off:
                orange_players.append(player)


        players_left = [i for i in players_left if
                        i not in green_players and i not in orange_players
                        and i not in red_players]

    for player in players_left:
        red_players.append(player)
    #
    # print([p.name for p in green_players])
    # print([p.name for p in orange_players])
    # print([p.name for p in red_players])
    for lst in green_players, orange_players, red_players:
        random.shuffle(lst)
    return (green_players, orange_players, red_players)




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

# Make work for multiple versions
def generate_new_game():

    """Find the best game possible, then add those players to the courts"""

    # Quick and dirty rule to always start with random shuffle, then use
    # segregated if you've saved that
    profile = enumerate_b.scoring_vars['Shuffle',
                             enumerate_b.profile]
    if profile == 0:
        players = select_players("Random", all_current_players, court_count)
        best_game = (enumerate_b.find_best_game(players, courts=court_count))


    elif profile == 1:
        players = select_players("Segregated", all_current_players,
                                 court_count)
        best_game = (enumerate_b.find_best_game(players, courts=court_count))
    elif profile == 4:

        best_game = enumerate_b.find_best_exhaustive(all_current_players, 10, 2)
        place_on_courts(best_game)
        return

    elif profile == 3:

        # #for i in range(10):
        # best_game = enumerate_b.find_best_exhaustive(all_current_players,
        #                                                  0, 0)
        #     # if not best_game:
        #     #      print("NOT!")
        #     #      break
        # #print("FINISHED")
        # place_on_courts(best_game)
        # return
        best_game = enumerate_b.smart_shuffle_trial(all_current_players,
                                         courts=court_count)


    elif profile == 2: # Smart Shuffle

        # Ensure don't pick manual games
        for court in courts:
            if court.manual:
                for player in court.spaces:
                    if player:
                        player.keep_on = False
                        player.keep_off = True


        trials = enumerate_b.scoring_vars["Trials", enumerate_b.profile]

        greens, oranges, reds = smart_select(all_current_players, court_count)


        #oranges = sorted(oranges, key=lambda x: x.desert, reverse=True)

        spaces = 4 * court_count
        no_oranges = spaces - len(greens)

        ### TESTING GENETIC
        counter = 0
        generation = 0

        comb_scores = {}
        combs = genetic.initialise(oranges, no_oranges, no_candidates=5)

        t_gen = time.time()

        while counter < 100:
            for comb in combs:
                if frozenset(comb) in comb_scores.keys():
                    continue
                players = greens[:]
                players.extend(comb)
                #print([p.name for p in players])
                benched = [p for p in all_current_players if p not in players]
                cost = (enumerate_b.find_best_game(players, courts=
                        court_count, benched=benched, scored=True))
                comb_scores[frozenset(comb)] = cost[1]
                counter += 1

            #print("\nMutation Time!")
            mutants = set()

            for comb in combs:
                #print([i.name for i in comb])
                new = genetic.mutate(comb, oranges, 0.1)
                if new:
                    mutants.add(new)
                    #print("Added mutant!")

            for comb in mutants:
                if comb in comb_scores.keys():
                    continue
                players = greens[:]
                players.extend(comb)
                #print([p.name for p in players])
                benched = [p for p in all_current_players if p not in players]
                cost = (enumerate_b.find_best_game(players, courts=
                court_count, benched=benched, scored=True))
                comb_scores[frozenset(comb)] = cost[1]
                counter += 1

                #print(len(comb_scores.keys()))
                combs = sorted(comb_scores, key = comb_scores.get)[:5]
                #print(combs)
            generation += 1
            #print(f"Generation {generation} over!")

        print(f"Best score genetic: {comb_scores[combs[0]]}")
        t_gen2 = time.time()
        print(f"Took {t_gen2 -t_gen}")






        #genetic.initialise_deserve(oranges, no_oranges, 5)


        ###

        if no_oranges > 0:
            # adds time to convert to list, but not enough to worry about at
            # this level
            orange_combos = list(combinations(oranges, no_oranges))
            # if too big, shuffle so the combos selected will be a random sample
            if len(orange_combos) > trials:
                # if random.random() > 0.5:
                #     print("Random!")
                random.shuffle(orange_combos)
                # else:
                #     print("Sorted!")

        else:
            orange_combos = [()]

        games = []
        scores = []
        tolerance_scores = []
        bench_scores = []
        t1 = time.time()

        combo_count = 0

        TEST_SELECTION = True


        for i, combo in enumerate(orange_combos):
            if stop_generation:
                return False

            # if TEST_SELECTION:
            #     # Test combos with decreasing probabilities:
            #     if random.random() >


            combo_count +=1
            if combo_count > trials:
                break

            players = greens[:]
            # print([p.name for p in combo])
            for player in combo:
                players.append(player)

            #players = select_players("Smart", pickable, court_count)

            benched = [p for p in all_current_players if p not in players]
            total = (enumerate_b.find_best_game(players, courts =
                    court_count, benched = benched, scored = True))
            games.append(total[0])
            scores.append(total[1])
            tolerance_scores.append(total[2])
            bench_scores.append(total[3])


        display = True

        index, lowest_score = min(enumerate(scores), key=operator.itemgetter(
            1))
        best_game = games[index]

        t2 = time.time()

        if display:
            #print_game(best_game[0])
            # print('')
            #print_game(best_game_2[0])

            print(f'Max score of {trials} games: {max(scores)}')
            print(f'Mean score of {trials} games: {mean(scores)}')
            tenth_list = scores[:int(len(scores)/10)]
            print(f'Best score of 1/10th of these games: {min(tenth_list)}')
            print(f'Score of this game: {lowest_score} (Tolerance: {tolerance_scores[index]})'
                  f'(Bench score: {bench_scores[index]})')
            print(f'Took {t2-t1} seconds')



    else:
        best_game = (enumerate_b.find_best_game(players, courts = court_count))

    place_on_courts(best_game)
    return True
    #return lowest_score #if simulated






def place_on_courts(best_game):
    for court in courts:
        if court.manual:
            continue
        else:
            court.empty()

    scores = 0
    count = 0

    for i, court in enumerate(courts):
        if court.manual:
            continue
        else:
            #for i, game in enumerate(best_game):
            for j, side in enumerate(best_game[count]):
                for k, player in enumerate(side):
                    if player:
                        # tolerance_score = 10*((abs(player.desert) ** 1.5)
                        #                       * player.desert/abs(player.desert))
                        # print(f'{player.name}s tolerance is {tolerance_score}')

                        court.spaces[(2 * j) + k] = player
                        if player in bench:
                            bench.remove(player)
            count +=1 # because 'i' goes up

        scores += enumerate_b.score_court(((0,1),(2,3)),courts[i].spaces,
                                            explain = False)
    # print(scores)
    enumerate_b.score_num = 0

    calculate_swap_TEST()

    # for player in bench:
    #     print(player.desert)
    # print('')


def print_game(game):
     for i, court in enumerate(game):
        print("*Court {}* \n".format(i + 1))
        for side in court:
            print("{} and {}".format(side[0].name,
                                          side[1].name))
        print('')
     print("--------------------")


def confirm_game():
    '''Update game counts, game history, save data'''
    for i, court in enumerate(courts):
        mean_ability = sum([p.ability for p in court.spaces if p]) / 4
        for j, player in enumerate(court.spaces):
            if player:
                player.update_game_count()
                player.recalculate_hunger(mean_ability)


        # Add played with/against to lists. Seems kind of suboptimal
        for player in court.spaces:
            if player:
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
        # should be Player Method?
        player.update_when_benched()

    for player in all_current_players:
        player.keep_off = False
        player.keep_on = False

    # not ideal to use globals, what but else should I do?    
    global total_rounds
    total_rounds += 1

    # saving session
    today_session.games.append([courts[i].spaces.copy() for i in range(len(
        courts))])

    # adding bench
    today_session.games[-1].append(bench.copy())

    # adding "results" section
    today_session.games[-1].append([None for i in range(len(courts))])



    # Updating desert.
    update_desert()
    # print_desert()

    #todo - trialing out new pvp
    update_pvp()

    #todo - trialing court_2_attr
    update_court_2_attr(courts[1].spaces)

def get_game_stats(court):
    '''Get information about a generated game'''
    abilities = [player.ability for player in court.spaces if player]

    if len(abilities) == 4:  # doubles
        ability_diff = abs(sum(abilities[0:2]) - sum(abilities[2:4]))
    else:  # singles
        ability_diff = abs(abilities[0] - abilities[1])

    ability_seg = abs(max(abilities) - min(abilities))

    return ability_diff, ability_seg





# should be able to make more concise, lots of duplication
def update_pvp():

    # discount

        # if player.name == "Henry":
        #     print(player.partner_histories)
        #     print(player.opp_histories)
    # for undoing
    #for player in all_current_players:

    for court in courts:
        for player in court.spaces:
            if player:

                player.old_partner_histories = player.partner_histories.copy()
                player.old_opp_histories = player.opp_histories.copy()

                # discounting, only when placed on the court.
                for key in player.partner_histories.keys():
                    player.partner_histories[key] *= 0.9
                for key in player.opp_histories.keys():
                    player.opp_histories[key] *= 0.9

                # i.e. not NONE, an empty space
                if player in court.spaces[0:2]:
                    partner = [i for i in court.spaces[0:2] if i is not
                               player if i is not None]
                    opponents = [i for i in court.spaces[2:4] if i is not
                                 player if i is not None]
                else:
                    partner = [i for i in court.spaces[2:4] if i is not
                               player if i is not None]
                    opponents = [i for i in court.spaces[0:2] if i is not
                                 player if i is not None]

                    # if player on side 1. Time to split list?
                for o_player in partner:
                    #try:
                    player.partner_histories[o_player] += 3*(1 + (
                            1/10)*player.partner_histories[o_player])
                    player.opp_histories[o_player] += 1*(1 + (
                            1/10)*player.opp_histories[o_player])
                    #except KeyError:
                        #player.partner_histories[o_player] = 1

                for o_player in opponents:
                    #try:
                    player.opp_histories[o_player] += 2*(1 + (
                            1/10)*player.opp_histories[o_player])
                    player.partner_histories[o_player] += 1*(1 + (
                            1/10)*player.partner_histories[o_player])
                    #except KeyError:
                    #    player.opp_histories[o_player] = 1



                # else:  # if on side #2
                #     if player in court.spaces[
                #                  2:4]:
                #         for o_player in [i for i in court.spaces[2:4] if i is not player]:
                #             player.partner_histories[o_player] += 3 * (1 + (
                #                     1 / 10) * player.partner_histories[
                #                                                            o_player])
                #             player.opp_histories[o_player] += 1 * (1 + (
                #                     1 / 10) * player.opp_histories[o_player])
                #
                #
                #         for o_player in [i for i in court.spaces[0:2] if i is not
                #                                                      player]:
                #             player.opp_histories[o_player] += 2 * (1 + (
                #                     1 / 10) * player.opp_histories[o_player])
                #             player.partner_histories[o_player] += 1 * (1 + (
                #                     1 / 10) * player.partner_histories[o_player])

                # if player.name == "Henry":
                #     print("Partner Histories")
                #     for p in player.partner_histories:
                #         print(p.name, player.partner_histories)
                #     print("Old Partner Histories")
                #     for p in player.old_partner_histories:
                #         print(p.name, player.old_partner_histories)


    # names = [courts[0].spaces[i].opp_histories for i in range(4)]
    #
    # for i, history in enumerate(names):
    #     print(f'{courts[0].spaces[i].name}')
    #     for p in history:
    #         print(p.name, history[p])
    #     print('')

def update_court_2_attr(court_spaces):

    for court in courts:
        for player in court.spaces:
            if player:
                player.old_court_2_attr = player.court_2_attr
                player.court_2_attr *= 0.8


    for player in court_spaces:
        if player:
            player.court_2_attr += 1 * (1 +(1/2 * player.court_2_attr))
        # print(player.name, player.court_2_attr)

def calculate_swap_TEST():

    #todo - make sure this doesn't stuff up/do weird with manual games
    # this probably works?
    for court in courts:
        if court.manual:
            return

    court_scores = []

    for i, court in enumerate(courts):
        abilities = [player.ability for player in court.spaces if player]
        average_abilities = sum(abilities)/4
        # print(f'Court {i+1} abilities: {average_abilities}')
        ab_cost = average_abilities**1.3

        court_2_costs = [player.court_2_attr for player in court.spaces if
                         player]
        average_c2 = sum(court_2_costs)
        #average_c2 *= 2
        # print(average_c2)

        court_scores.append(ab_cost + average_c2)

    # print(court_scores)


    val = (court_scores.index(min(court_scores)))
    if val != 1:
        swap_courts(courts[1], courts[val])
        # print(f"Swapped Court 2 with  Court {val+1}!")

def learn_new_abilities(done_before, round_no):
    '''From results, update each player's ability'''


    last_round = today_session.games[round_no]

    for i, game in enumerate(last_round[:-2]):

        score = last_round[-1][i]

        names = []

        for player in game:
            if player is None:
                names.append("NONE")
            else:
                names.append(player.name)

        if done_before:
            #doesn't work if some people's results are not inputted
            abilities = [player.ability_history[-2] for player in game if
                         player]
        else:
            abilities = [player.ability for player in game if player]

        if len(abilities) == 4: #doubles
            ability_diff = sum(abilities[0:2]) - sum(abilities[2:4])
        elif len(abilities) == 2: #singles
            ability_diff = abilities[0] - abilities[1]
        else: # empty game
            print(f'\n***Court {i+1}***\n EMPTY \n')
            continue # go to next game


        ability_seg = max(abilities) - min(abilities)


        print(f'\n***Court {i+1}***\n')
        print(f'{names[0]} and {names[1]} VS.')
        print(f'{names[2]} and {names[3]}')
        print('')
        print(f'Score: {score}')
        print(f'Side 1 ability advantage: {round(ability_diff,2)}')
        print(f'Span of abilities: {round(ability_seg,2)}')
        print('')

        if score is None: # no score, no update
            print("No results recorded \n")


            for player in game:
                if player:
                # append to history for purpose of checking done_before. Could
                # get weird if you
                #  do silly things like keep removing and adding
                    print(f'{player.name}\'s ability is {player.ability}')
                    player.ability_history.append(player.ability)
            continue

        margin = score[0] - score[1]

        # if done_before:
        #     #doesn't work if some people's results are not inputted
        #     abilities = [player.ability_history[-2] for player in game if
        #                  player]
        # else:
        #     abilities = [player.ability for player in game if player]
        #
        # if len(abilities) == 4: #doubles
        #     ability_diff = sum(abilities[0:2]) - sum(abilities[2:4])
        # else: #singles
        #     ability_diff = abilities[0] - abilities[1]
        #
        # ability_seg = max(abilities) - min(abilities)
        #
        # print(f'Score: {score}')
        # print(f'Side 1 ability advantage: {round(ability_diff,2)}')
        # print(f'Span of abilities: {round(ability_seg,2)}')
        # print('')

        for i, player in enumerate(game):
            if player:
                #Side 1 vs Side 2, have opposite margins/ability diff
                if i>1:
                    team_margin= -margin
                    team_ability = -ability_diff
                else:
                    team_margin = margin
                    team_ability = ability_diff

                if player.first_night:
                    #quick and dirty way of making
                    # abilities adjust quicker for new players
                    learning_variable = 20
                else:
                    learning_variable = 40

                ability_change = (team_margin- 4*team_ability)/(learning_variable*(
                        1+ability_seg))

                if done_before:
                    ability_to_update = player.ability_history[-2]
                    player.ability = player.ability_history[-2] + ability_change
                    del player.ability_history[-1]
                else:
                    ability_to_update = player.ability
                    player.ability += ability_change

                player.ability_history.append(player.ability)

                round_atu = round(ability_to_update,2)
                round_new_ab = round(player.ability, 2)
                round_ac = round(ability_change, 2)
                print(f'{player.name}\'s ability changes from {round_atu} to '
                      f'{round_new_ab}, a change of {round_ac}')





def undo_confirm():

    for court in courts:
        for player in court.spaces:
            if player:
                player.undo_game(on_court=True)

    # should be part of the undo game method
    for player in bench:
        player.undo_game(on_court=False)
        #player.partner_histories = player.old_partner_histories
        #player.opp_histories = player.old_opp_histories

    # not ideal to use globals, what but else should I do?
    global total_rounds
    total_rounds -= 1

    del today_session.games[-1]



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
    today_session.player_departures[player] = datetime.now().time()

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
    player.accumulate_fee()
    all_current_players.append(player)
    today_session.player_arrivals[player] = datetime.now().time()


def swap_courts(court_a, court_b):
    '''Assign each court the players of each other'''
    a_spaces = court_a.spaces
    b_spaces = court_b.spaces
    court_a.spaces = b_spaces
    court_b.spaces = a_spaces

def empty_courts():

    # greens, oranges, reds = smart_select(all_current_players, court_count)
    # spaces = 4 * court_count
    # no_oranges = spaces - len(greens)
    # if no_oranges > 0:
    #     orange_combos = combinations(oranges, no_oranges)
    # for combo in orange_combos:
    #     players = greens[:]
    #     #print([p.name for p in combo])
    #     for player in combo:
    #         players.append(player)
    #     print([p.name for p in players])

    for court in courts:
        court.empty()

# should be class attribute
def make_manual(court_no, toggle=True):
    '''Toggle court on to manual or automatic'''

    if courts[court_no].manual:
        add_court()
        courts[court_no].manual = False

    elif not toggle: # when resetting
        pass
    else:
        remove_court()
        courts[court_no].manual = True

    # Save the old manual state for undoing purposes
    if toggle:
        courts[court_no].update_manual()


# For purposes of manual game court counting
def remove_court():
    global court_count
    court_count -= 1

def add_court():
    global court_count
    court_count += 1

# How to work with fewer than 12 players? Can't make desert go up high,
# or too low either?
# For a temporary fix, just don't change desert?
def update_desert():

    # ignore deserts with low numbers for now
    if len(all_current_players) < 4*len(courts):
        return

    for player in all_current_players:
        player.old_desert = player.desert
        player.desert += ((4 * len(courts))/len(all_current_players)) - 1
    for player in bench:  # as opposed to checking the courts
        player.desert += 1



def print_desert():
    for player in every_player:
        #print(player.name, player.total_games)
        #if player.name in ('Henry', 'David', 'Jack', 'Desmond'):
        #print(f'{player.name} played {player.total_games}')
        print(f'{player.name}s desert is {player.desert}')


def save_and_quit(pickling=True):
    """Reset everything only when exited properly.
    Otherwise, you can reload your previous state."""

    # Sum deserts for normalising
    sum_deserts = 0
    for player in every_player:
        sum_deserts += player.desert

    av_deserts = sum_deserts/len(every_player)

    # Reset all the players
    for player in every_player:
        player.total_games = 0
        player.penalty_games = 0
        player.adjusted_games = 0
        player.time_since_last = 0
        player.consecutive_games_on = 0
        player.played_with = []
        player.played_against = []
        player.keep_off = False
        player.keep_on = False
        player.mean_game_abs = player.ability
        player.hunger = 0
        player.old_hunger = 0
        player.court_2_attr *= 0.3
        player.old_court_2_attr *= 0.3
        player.desert -= av_deserts
        # deweighting histories.
        # todo: make sure the following two doen't happen with autosave
        for key in player.partner_histories.keys():
            player.partner_histories[key] *= 0.3 # 0.5
        for key in player.opp_histories.keys():
            player.opp_histories[key] *= 0.3

        if player.first_night:
            player.first_night = False

        # try: # new players get first_night added
        #     if player.first_night:
        #         player.desert = 0
        # except AttributeError:
        #     pass

        # deweighting court_2 relevance. Should it be 0.5? set to 0? else?

        #print(f'{player.name} reset!')

    # Save departure times
    for player in all_current_players:
        today_session.player_departures[player] = datetime.now().time()

    today_session.end_time = datetime.now().time()

    all_sessions.append(today_session)

    global fake_players
    if fake_players:
        pickling = False

    if pickling:

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
date = datetime.now().date()
start_time = datetime.now().time()
today_session = b_sessions.Session(date, start_time)

total_rounds = 0

courts = [Court() for i in range(3)]
court_count = len(courts)


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

    for player in every_player:
        if not hasattr(player, 'consecutive_games_on'):
            player.consecutive_games_on = 0
            print("Add consec!")
        # if not hasattr(player, 'manual_game'):
        #     player.manual_game = False


        if not hasattr(player, 'hunger'):
            player.hunger = player.ability
        if not hasattr(player, 'old_hunger'):
            player.old_hunger = 0
        if not hasattr(player, 'mean_game_abs'):
            player.mean_game_abs = player.ability

    # backwards compatibility code

        if not hasattr(player, 'membership'):
            player.membership = "Member (incl. feathers)"
        else:
            pass
        if not hasattr(player, 'money_owed'):
            player.money_owed = 0
        if not hasattr(player, "paid_tonight"):
            player.paid_tonight = True
        if not hasattr(player, 'keep_on'):
            player.keep_on = False

        if not hasattr(player, 'desert'):
            player.desert = 0
        if not hasattr(player, 'old_desert'):
            player.old_desert = 0

        if not hasattr(player, 'partner_histories'):
            player.partner_histories = defaultdict(float)
            player.opp_histories = defaultdict(float)

            player.old_partner_histories = defaultdict(float)
            player.old_opp_histories = defaultdict(float)

        if not hasattr(player, 'court_2_attr'):
            player.court_2_attr = 0
        if not hasattr(player, 'old_court_2_attr'):
            player.old_court_2_attr = 0

        if not hasattr(player, 'fitness'):
            player.fitness = 2

        if not hasattr(player, 'first_night'):
            player.first_night = False

        # if hasattr(player, 'new_ability'):
        #     player.ability = player.new_ability
        # if hasattr(player, 'new_ability'): # TEMPORARY
        #     player.new_ability = player.ability

        if not hasattr(player, 'ability_history'):
            player.ability_history = [player.ability]
        #
        # if hasattr(player, 'ability_history'): # TEMPORARY
        #     player.ability_history = [player.ability]

        if not hasattr(player, 'affinity_for_newbies'):
            if player.name in ("Henry", "David"):
                player.affinity_for_newbies = True
            else:
                player.affinity_for_newbies = False



        # Grandfather in new affinities
        temp_partners = []
        for name in player.partner_affinities:
            if isinstance(name, tuple): # i.e. already updated
                temp_partners.append(name)
            elif isinstance(name, str): # if string, add "Medium" level
                temp_partners.append((name, "Medium"))
            else:
                print("Affinity Error!")
        player.partner_affinities = temp_partners

        temp_opps = []
        for name in player.opponent_affinities:
            if isinstance(name, tuple): # i.e. already updated
                temp_opps.append(name)
            elif isinstance(name, str): # if string, add "Medium" level
                temp_opps.append((name, "Medium"))
            else:
                print("Affinity Error!")
        player.opponent_affinities = temp_opps



except FileNotFoundError:
    every_player = [Aaron, Andrew, Amanda, Anna, Barry, Beth, Bill, Bob, Caleb,
                Calvin, Cindy, Charles, David, Derek, Denise, Doris, Edward,
                Elliot, Emma, Erin, Fiona, Felicity, Flynn, Fred, Gary,
                George, Georgina, Gordon, Hannah, Harry, Heather, Hunter,
                Ian, Igor, Indiana, Isaac]

    for player in every_player:
        player.membership = "Member (incl. feathers)"


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

# fee structure
fee_structure = {("Casual", 1): 5, ("Casual", 3): 10,
                 ("Member (incl. feathers)", 1): 0,
                 ("Member (incl. feathers)", 3): 0,
                 ("Member (no feathers)", 1): 0,
                 ("Member (no feathers)", 3): 3}

# Hackish way of doing "boost", should be better organsied
old_seg = False
old_aff = False
#for player in every_player:
#    player.desert = 0
stop_generation = False

### random trial stuff
# from pprint import pprint
#
# for player in every_player:
#     print(player.name)
#     for opp in player.opp_histories.keys():
#         if player.opp_histories[opp] >1:
#             print(opp.name, player.opp_histories[opp])

#fake_players = False

def init_fake_players(num):
    every_player = []

    for i in range(num):
        ability = 10 * random.random()
        name = str(round(ability, 2))
        new_player = Player(name, "Male", ability)
        every_player.append(new_player)

    all_current_players = []
    # player not in all_current_players would duplicate it
    absent_players = [player for player in every_player if player.name not in
                      [player.name for player in all_current_players]]

    # Bench starts full
    bench = all_current_players[:]

if fake_players:
    init_fake_players(18)





