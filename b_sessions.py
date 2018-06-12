"""I want to to store data about the games that were played in a given
night, as well as other factors."""

class Session:
    def __init__(self, date, start_time):

        self.date = date
        self.start_time = start_time
        self.end_time = 0  # updated later
        self.games = []  # gets appended to
        self.player_arrivals = {} # Keys: Player names. Values: times
        self.player_departures = {} # Ditto


# A list of all the sessions.
# Might be better as dict, with date as key?
all_sessions = []

