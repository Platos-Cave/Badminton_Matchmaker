# todo: update using numpy or pandas
"""I want to to store data about the games that were played in a given
night, as well as other factors."""
import csv
import pickle
import b_scorer

class Session:
    def __init__(self, date, start_time):

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

        writer.writerow(['DATE', "ROUND #", "COURT #", "SPACE #", "NAME",
                         "ABILITY"])

        for i, session in enumerate(loaded_sessions):
            if len(session.games) > 0:
                for j, game in enumerate(session.games):
                    for k in range(3):
                        for l in range(4):
                            try:
                                writer.writerow([session.date, j+1, k+1, l+1,
                                             game[k][l].name, game[k][
                                    l].ability])
                            except AttributeError:
                                writer.writerow([session.date, j + 1, k, l + 1,
                                                 "NONE", 0])

            #
            # if len(session.games) > 0:
            #     writer.writerow(['DATE'])
            #     writer.writerow([session.date])
            #     writer.writerow([''])
            #     for i, game in enumerate(session.games):
            #         writer.writerow(['GAME {} \n'.format(i + 1), '', 'COURT 1',
            #                          '', '', 'COURT 2', '', '', 'COURT 3'])

                    # # Dealing with "NoneType" issues
                    # side_1s = ['', 'SIDE 1']
                    # side_2s = ['', 'SIDE 2']
                    #
                    # for i in range(3):
                    #     for j in range(2):
                    #         try:
                    #             side_1s.append(game[i][j].name)
                    #         except AttributeError:
                    #             side_1s.append("NONE")
                    #     side_1s.append('')
                    #
                    # for i in range(3):
                    #     for j in range(2):
                    #         try:
                    #             side_2s.append(game[i][j+2].name)
                    #         except AttributeError:
                    #             side_2s.append("NONE")
                    #     side_2s.append('')
                    #
                    # writer.writerow(side_1s)
                    # writer.writerow(side_2s)
                    #
                    # # writer.writerow(
                    # #     ['', 'SIDE 1', game[0][0].name, game[0][1].name,
                    # #      '', game[1][0].name, game[1][1].name,
                    # #      '', game[2][0].name, game[2][1].name])
                    # # writer.writerow(
                    # #     ['', 'SIDE 2', game[0][2].name, game[0][3].name,
                    # #      '', game[1][2].name, game[1][3].name,
                    # #      '', game[2][2].name, game[2][3].name])
                    #
                    # writer.writerow([''])


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


# A list of all the sessions.
# Might be better as dict, with date as key?
all_sessions = []

# export_game_data("bob")
