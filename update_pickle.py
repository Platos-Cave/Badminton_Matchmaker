import pickle
import pandas as pd

pickle_in = open("every_player_pi_2 (1).obj","rb")
every_player = pickle.load(pickle_in)
pickle_in.close()

fbc = pd.read_csv("FBC 2019.csv")

for player in every_player:

    player.money_owed = 0

    if player.name not in fbc['Name on program'].values:
        player.membership = "Casual"
    else:
        player_entry = fbc.loc[fbc['Name on program'] == player.name]
        if player_entry['Membership type'].str.contains("Feathers "
                                                        "included").any():
            player.membership = "Member (incl. feathers)"
        elif player_entry['Membership type'].str.contains("No feathers").any():
            player.membership = "Member (no feathers)"
        else:
            print(player.name)
            print("Error in membership!")

for p in every_player:
    print(f'{p.name}, {p.membership}, {p.money_owed}')



pickle_out = open('every_player_pi_2 (1).obj', 'wb')
pickle.dump(every_player, pickle_out)
pickle_out.close()


