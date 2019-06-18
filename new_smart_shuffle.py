'''Rather than exhaustively test all combos, or test random combos, I should
be smart about testing combos that have high desert'''

def sort_by_deservedness(players):
    return sorted(players, key=lambda x: x.desert, reverse=True)




