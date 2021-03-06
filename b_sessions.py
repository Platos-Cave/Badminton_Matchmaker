# todo: update using numpy or pandas
"""I want to to store data about the games that were played in a given
night, as well as other factors."""
import csv
import pickle
import b_scorer

class Session:
    def __init__(self, date, start_time ):

        self.date = date
        self.start_time = start_time
        self.end_time = 0  # updated later
        self.games = []  # gets appended to
        self.player_arrivals = {} # Keys: Player names. Values: times
        self.player_departures = {} # Ditto
        self.payments = {} # Keys: Player names. Values: (Membership
         # Status, Payments)


# DATA | ROUND NO | COURT NO| SPACE NO| PLAYER NAME | PLAYER ABILITY |

def export_game_data(filename):
    session_data = open('badminton_session_data.obj', 'rb')
    loaded_sessions = pickle.load(session_data)
    session_data.close()

    game_file = open('{}.csv'.format(filename), 'w', newline='')

    with game_file:
        writer = csv.writer(game_file)

        writer.writerow(['Date', "Round No", "Court No", "Space No", "Name",
                         "Ability"])

        for i, session in enumerate(loaded_sessions):
            if len(session.games) > 0:
                for j, game in enumerate(session.games):
                    #print([p.name for p in game])
                    for k, court in enumerate(game):
                        #print([p.name for p in court])
                        if k<3:
                            for l in range(4):
                                try:
                                    writer.writerow([session.date, j+1, k+1, l+1,
                                                 game[k][l].name, game[k][
                                        l].ability])
                                except AttributeError:
                                    writer.writerow([session.date, j + 1, k+1,
                                                     l + 1,
                                                     "NONE", 0])
                        else:
                            for player in court: #bench
                                writer.writerow(
                                    [session.date, j + 1, "B", "B",
                                     player.name, player.ability])


def export_player_data(filename):
    names = [player.name for player in b_scorer.every_player]
    sexes = [player.sex for player in b_scorer.every_player]
    abilities = [player.ability for player in b_scorer.every_player]
    partner_affs = [", ".join(player.partner_affinities) for player in
                    b_scorer.every_player]
    opponent_affs = [", ".join(player.opponent_affinities) for player in
                     b_scorer.every_player]
    zip_data = zip(names, sexes, abilities, partner_affs, opponent_affs)

    myFile = open('{}.csv'.format(filename), 'w', newline='')

    with myFile:
        writer = csv.writer(myFile)
        writer.writerow(['NAME', 'SEX', 'ABILITY', 'PARTNER AFFINITIES',
                         'OPPONENT AFFINITIES'])
        writer.writerows(zip_data)

def export_arrival_data(filename):
    session_data = open('badminton_session_data_2.obj', 'rb')
    loaded_sessions = pickle.load(session_data)
    session_data.close()
    game_file = open('{}.csv'.format(filename), 'w', newline='')

    with game_file:
        writer = csv.writer(game_file)

        writer.writerow(['DATE', "NAME", "ARRIVAL TIME", "DEPARTURE TIME"])

        for i, session in enumerate(loaded_sessions):
            if len(session.games) > 0:
                for player in session.player_departures:
                    try:
                        writer.writerow([session.date, player.name,
                                         session.player_arrivals[player],
                                        session.player_departures[player]])

                    except AttributeError:
                        writer.writerow([session.date, "NONE", "NONE"])


# A list of all the sessions.
# Might be better as dict, with date as key?
all_sessions = []


