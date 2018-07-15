import csv
import b_scorer

names = [player.name for player in b_scorer.every_player]
sexes = [player.sex for player in b_scorer.every_player]
abilities = [player.ability for player in b_scorer.every_player]
partner_affs = [", ".join(player.partner_affinities) for player in b_scorer.every_player]
opponent_affs = [", ".join(player.opponent_affinities) for player in b_scorer.every_player]
zip_data = zip(names, sexes, abilities, partner_affs, opponent_affs)

myFile = open('all_player_data_test_2.csv', 'w', newline='')

with myFile:
    writer = csv.writer(myFile)
    writer.writerow(['NAME', 'SEX', 'ABILITY', 'PARTNER AFFINITIES', 'OPPONENT AFFINITIES'])
    writer.writerows(zip_data)




