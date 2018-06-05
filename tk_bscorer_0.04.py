'''A GUI for placing players on the courts in a way that is ideally
readable by the players themselves.'''

import tkinter as tk
from tkinter import Tk, ttk, Frame, Menu, messagebox
from tkinter.messagebox import showinfo, askyesno, showerror
import b_scorer
import b_sessions
import pickle
import datetime
import random


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)

        # A (probably unPythonic) way of randomly loading the bench
        self.test_mode = True

        self.title("Badminton Matchmaker")

        self.protocol("WM_DELETE_WINDOW", lambda: self.confirm_quit())

        self.bench_popup_menus = {}
        self.court_menus = {}
        self.space_menus = {}

        self.court_labels = [ttk.Label(text = "Court {}".format(i+1),
                            background = bg_colour,
                            font=('Helvetica', 33, 'bold')) for i in range (3)]

        self.court_frames = [CourtFrame(self, i) for i in range(3)]
        self.absent_label = ttk.Label(text = "Absent Players",
                                      background = bg_colour,
                                      font=('Helvetica', 16, 'bold'))
        self.bench_label = ttk.Label(text = "Bench",
                                     background = bg_colour,
                                     font=('Helvetica', 24, 'bold'))
        self.bench = BenchFrame(self)
        # Create labels representing players on the bench
        self.bench_labels = [tk.Label(self.bench,
                            text = player.name, width = 8,
                            height = 2) for player in b_scorer.bench]

        # These attempts to format my lines to >80 characters seem unnatural

        #The names of the Players who haven't joined
        self.all_plyr_cbox = ttk.Combobox(self, width = 24,
                                          postcommand = self.get_all_players)
        self.all_plyr_cbox.config(values = ["Select or "
                                                   "type-in name..."])
        self.all_plyr_cbox.current(0)
        self.all_plyr_cbox.bind('<FocusIn>',
                                lambda event: self.player_cbox_clear())
        self.all_plyr_cbox.bind('<Return>', lambda event: self.add_player())

        self.add_player_button = ttk.Button(self,
                                text = "Add Player to Bench",
                                command = self.add_player)
        self.create_player_button = ttk.Button(self,
                                               text = "Create New Player",
                                               command = self.create_player)
        self.delete_player_button = ttk.Button(self, text = "Delete Player",
                                    command = self.delete_player)
        self.rounds_label = ttk.Label(text = "Rounds: {}".format(b_scorer.total_rounds),
                                      background = bg_colour,
                                      font=('Helvetica', 16, 'bold'))
        self.start_button = ttk.Button(self, text = "Generate New Board",
                                       command = self.start)
        self.confirm_button = ttk.Button(self, text = "Confirm Board",
                                     command = self.confirm)
        self.game_weighting_button = ttk.Button(self,
                                     text = "Change Automatic Rules",
                                     command = self.edit_game_weightings)
        self.empty_courts_button = ttk.Button(self, text = "Empty Courts",
                                              command = self.empty_courts)

        for i, court in enumerate(self.court_labels):
            court.grid(column = (5*i)+2, row = 2, sticky = 'nsew',
                       padx= 10, pady = 10)

        for i, court in enumerate(self.court_frames):
            court.grid(column= 5*i, row = 5, rowspan = 5, columnspan = 5,
                                padx= 10, pady = 10, sticky = 'nsew')

        for i in range(50):
                self.columnconfigure(i, weight=1)
                self.rowconfigure(i, weight=1)


        self.absent_label.grid(column = 1, row = 15, columnspan = 2)
        self.all_plyr_cbox.grid(column = 1, row = 16, columnspan = 2,
                                padx= 2, pady = 2)

        self.add_player_button.grid(column = 2, row = 17,
                                    sticky = 'nsew', padx= 1, pady = 1)
        self.create_player_button.grid(column = 1, row = 17,
                                       sticky = 'nsew', padx= 1, pady = 1)
        self.delete_player_button.grid(column = 1, row = 18,
                                       sticky = 'nsew', padx= 1, pady = 1)

        self.bench_label.grid(column = 7, row = 15, columnspan = 2,
                              padx= 1, pady = 1 )
        self.bench.grid(column = 4, row = 16, columnspan = 7, rowspan = 5,
                        sticky = 'nsew', padx= 1, pady = 1)

        self.rounds_label.grid(column = 12, row = 15, columnspan = 2)
        self.start_button.grid(column = 12, row = 16, sticky = 'nsew',
                               padx= 1, pady = 1)
        self.confirm_button.grid(column = 13, row = 16, sticky = 'nsew',
                                 padx= 1, pady = 1)
        self.empty_courts_button.grid(column = 13, row = 17, sticky = 'nsew',
                                      padx= 1, pady = 1)
        self.game_weighting_button.grid(column = 12, row = 17, sticky = 'nsew',
                                        padx= 1, pady = 1)

        if self.test_mode is True:
            random.shuffle(b_scorer.every_player)
            for player in b_scorer.every_player[0:16]:
                b_scorer.add_player(player)
                self.add_bench_menus(player)
            self.colour_dict = b_scorer.colour_sorter(b_scorer.all_current_players)

        # If program crashed or exited otherwise normally, reload all data
        try:
            pickle_in = open("board_data.obj","rb")
            board_data = pickle.load(pickle_in)
        except FileNotFoundError:
            board_data = {}

        try:
            b_scorer.every_player = board_data["every_player"]
            b_scorer.all_current_players = board_data["all_current_players"]
            b_scorer.absent_players = board_data["absent_players"]
            b_scorer.total_rounds = board_data["total_rounds"]
            b_scorer.bench = board_data["bench"]
            b_scorer.courts = board_data["courts"]
            b_scorer.today_session = board_data["today_session"]
            self.colour_dict = board_data["colour_dict"]
            self.confirm_button.configure(state = board_data["confirm_state"])
            for player in b_scorer.bench:
                self.add_bench_menus(player)
                self.bench_popup_menus =  board_data["bench_menus"]
                self.court_menus = board_data["court_menus"]
                self.space_menus = board_data["space_menus"]
            pickle_in.close()
            # If it hasn't been saved before, or was blanked when it quit
        except KeyError: # board_data was blanked on exit
            pass

        self.update_board()

    # Save the current state, in order 
    def autosave(self):

        pickle_in = open('board_data.obj', 'wb')
        board_data = {}
        board_data["every_player"] = b_scorer.every_player
        board_data["all_current_players"] = b_scorer.all_current_players 
        board_data["absent_players"] = b_scorer.absent_players 
        board_data["total_rounds"] = b_scorer.total_rounds 
        board_data["bench"] = b_scorer.bench
        board_data["courts"] = b_scorer.courts
        board_data["today_session"] = b_scorer.today_session
        board_data["colour_dict"] = self.colour_dict
        # For some reason, wouldn't work otherwise
        button_state = str(self.confirm_button["state"])
        if button_state == "disabled":
            board_data["confirm_state"] = "disabled"
        else:
            board_data["confirm_state"] = "normal"

        pickle.dump(board_data, pickle_in)
        pickle_in.close()

    def confirm_quit(self):
        answer = tk.messagebox.askokcancel("Confirm Quit",
                                           "Are you sure you want to quit?")
        if answer is True:
            b_scorer.save_and_quit()

            every_pi = open('every_player_pi_2.obj', 'wb')
            pickle.dump(b_scorer.every_player, every_pi)
            every_pi.close()

            self.destroy()
        
    def player_cbox_clear(self):
        entry = self.all_plyr_cbox
        
        """function that gets called whenever entry is clicked"""
        if entry.get() == "Select or type-in name...":
            entry.delete(0, "end")  # delete all the text in the entry
            entry.insert(0, '')  # Insert blank for user input
            

    def empty_courts(self):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                    "Are you sure you want to empty the courts?")

        if are_you_sure is True:
            b_scorer.empty_courts()
            self.confirm_button.configure(state = "normal")
            self.update_board()

    # Create popup menus for each player that are saved to dictionaries
    def add_bench_menus(self, player):

        self.bench_popup_menus[player] = Menu(self, tearoff=0)
        self.court_menus[player] = Menu(self, tearoff=0)
        self.space_menus[player] = []

        #The methods call the court names and numbers, which are invalid here
        # Seems ugly, can't figure out how to get to >80 characters
        self.bench_popup_menus[player].add_command(command = lambda: self.view_player_stats(None, None, player),
                                                   label = "View Player Stats")
        self.bench_popup_menus[player].add_command(command = lambda: self.remove_player_entirely(None, None, player),
                                                   label="Remove From Night")
        self.bench_popup_menus[player].add_command(command = lambda: self.keep_player_off(None, None, player),
                                                   label="Keep Player Off Next Round")
        self.bench_popup_menus[player].add_cascade( menu=self.court_menus[player],
                                                    label="Pin to Court...",)
        # Add menu options for manually adding players to courts
        for j in range(3):
                self.space_menus[player].append(Menu(self, tearoff=0))
                self.court_menus[player].add_cascade(label= "#{}...".format(j+1),
                                            menu = self.space_menus[player][j])

                for k in range(4):
                    self.space_menus[player][j].add_command(
                    label = "Space {}".format(k+1),
                    command = lambda player = player, court = j, space = k:
                    self.bench_to_court(player, court, space)) 

        
    # Regrid the players on the bench, update size and colours
    def bench_grid(self):

        # Forget current labels.
        for label in self.bench.grid_slaves():
            label.grid_forget()

        # Adjust label values for size of grid
        if len(b_scorer.bench) < 9:
            custom_width = 10
            custom_height = 2
            players_per_row = 4
            custom_font = ('Helvetica', 15, 'bold')
            custom_pad = 1
        elif len(b_scorer.bench) < 19:
            custom_width = 8
            custom_height = 2
            players_per_row = 6
            custom_font = ('Helvetica', 12, 'bold')
            custom_pad = 1
        else:
            custom_width = 8
            custom_height = 2
            players_per_row = 8
            custom_font = ('Helvetica', 8, 'bold')
            custom_pad = 1


        self.bench_labels = [tk.Label(self.bench, width = custom_width,
                             height = custom_height,
                             font = custom_font,
                             text = player.name) for player in b_scorer.bench]

        for i, label in enumerate(self.bench_labels):

            player = b_scorer.bench[i]
 
            label.bind("<ButtonPress-3>", lambda event, player = player: self.show_bench_options(event, player))
            self.bench_labels[i].config(background=self.colour_dict[player])

        #Creating the bench labels
        
        count = -1
        new_row = 0

        for i, label in enumerate(self.bench_labels):
            count += 1
            if count == players_per_row:
                count = 0
                new_row +=1
            label.grid(column = count, row = new_row, padx= custom_pad, pady = custom_pad, sticky = 'nsew')


    # Manually put a player on the court
    def bench_to_court(self, player, court, space):

        if b_scorer.courts[court].spaces[space] != None:
            tk.messagebox.showerror("Error", "Player already in that space")
        else:
            b_scorer.courts[court].spaces[space] = player
            # Currently unused way of "pinning" players to court
##            b_scorer.pin_courts[court].spaces[space] = player
            b_scorer.courts[court].spaces[space] = player
            b_scorer.bench.remove(player)
            self.update_board()

    def add_player(self):

        selected = self.all_plyr_cbox.get()
        existing = [player.name for player in b_scorer.every_player]
        currents = [player.name for player in b_scorer.all_current_players]

        if selected == "Select or type-in name...":
            error = tk.messagebox.showerror("Error",
                        "Please select a player to add to the board.")
            return
        elif selected not in existing:
             new_query = tk.messagebox.askyesno("Player Not Found",
                                     "No player with that name found!"
                                     " Would you like to create this player?")
             if new_query is True:
                 self.create_player()
                 self.create_toplevel.name_entry.insert(0, selected)
             else:
                 return
                
        elif selected in currents:
            tk.messagebox.showerror("Error", "This player is already on!")
            return
        
        else:            
            for player in b_scorer.absent_players:
                if selected == player.name:
                    b_scorer.add_player(player)
                    self.colour_dict = b_scorer.colour_sorter(b_scorer.all_current_players)
                    self.add_bench_menus(player)
        #Refresh the combobox with the new values
        self.get_all_players()

        #Refresh the grid
        self.bench_grid()

        self.autosave()

    def create_player(self):
        self.create_toplevel = NewPlayerWindow(self)

    def delete_player(self):

        selected = self.all_plyr_cbox.get()
        if selected == "Select or type-in name...":
            error = tk.messagebox.showerror("Error",
                                "Please select a player to delete.")
        else:
            query = tk.messagebox.askyesno("Are you sure?",
                   "Are you sure you want to permanently delete this player?")
            if query is True:
                # Surely there should be a better way of deleting a player?
                b_scorer.absent_players = [player for player
                                           in b_scorer.absent_players
                                           if player.name != selected]
                b_scorer.every_player = [player for player
                                         in b_scorer.every_player
                                         if player.name != selected]
                self.all_plyr_cbox.current(0)

                #Delete all affinities
                for player in b_scorer.every_player:
                    if selected in player.partner_affinities:
                        player.partner_affinities.remove(selected)
                    if selected in player.opponent_affinities:
                        player.opponent_affinities.remove(selected)

                # Save to pickle
                self.autosave()

                every_pi = open('every_player_pi_2.obj', 'wb')
                pickle.dump(b_scorer.every_player, every_pi)
                every_pi.close()

    # Remove player from the game night
    def remove_player_entirely(self, court_number, index, player = None):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                            "Are you sure this player is leaving?")

        if are_you_sure is True:
            b_scorer.remove_player(court_number, index, player)
            self.colour_dict = b_scorer.colour_sorter(b_scorer.all_current_players)
            self.get_all_players()
            self.update_board()
            self.autosave()

    def start(self):

        '''If fewer than 12, will cause error. Rather than figure out a way of sorting this out,
        I'm just going to leave it up to the person to do it manually'''

        players_on = [player for player in b_scorer.all_current_players
                      if player.keep_off is False]

        if len(b_scorer.all_current_players) < 12:
            tk.messagebox.showerror(
                "Error", "There are fewer players available than spaces"
                " on courts! This program can't handle that.")
        elif len(players_on) < 12:
             tk.messagebox.showerror(
                "Error", "You've kept so many players off that you can't "
                "fill the courts! Put some back on!")
        else:          
            
            b_scorer.generate_new_game()
            self.update_board()            
            self.confirm_button.configure(state = "normal")

    def confirm(self):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                        "Are you sure you want to confirm this game for the next round?")

        if are_you_sure is True:
            b_scorer.confirm_game()
            self.colour_dict = b_scorer.colour_sorter(b_scorer.all_current_players)
            self.update_board()
            self.confirm_button.configure(state = "disabled")

            self.autosave()

            every_pi = open('every_player_pi_2.obj', 'wb')
            pickle.dump(b_scorer.every_player, every_pi)
            every_pi.close()

    # Whenever anything is updated
    def update_board(self):

        #Display all player on the courts, unless the courts are empty.
        for i, court in enumerate(self.court_frames):
            for j, label in enumerate(court.labels):
                try:
                    label.config(text = b_scorer.courts[i].spaces[j].name)
                except AttributeError: # if there is no-one in that space
                    label.config(text = "-")

        #Update the rounds label
        self.rounds_label.config(text = "Rounds: {}".format(b_scorer.total_rounds))

        #Redisplay the bench
        self.bench_grid()

    # When bench label clicked, show the menu
    def show_bench_options(self, event, player):

        if player.keep_off is False:
            self.bench_popup_menus[player].entryconfigure(2,
                                        label = "Keep Player Off Next Round")
        else:
            self.bench_popup_menus[player].entryconfigure(2,
                                             label = "Undo Keep Player Off")

        self.bench_popup_menus[player].post(event.x_root, event.y_root)

    def show_options(self, event, court_number, index):

        # Show popup only when the court is full.
         if b_scorer.courts[court_number].spaces[index] is not None:

            player = b_scorer.courts[court_number].spaces[index]
            # If the player is already "kept off", configure the label to "undo keep off"
            if player.keep_off is False:
                self.court_frames[court_number].popup_menus[index].entryconfigure(3,
                                                label = "Keep Player Off Next Round")
            else:
                self.court_frames[court_number].popup_menus[index].entryconfigure(3,
                                                      label = "Undo Keep Player Off")

            self.court_frames[court_number].popup_menus[index].post(event.x_root, event.y_root)

    #returns a player from the court to the bench
    def return_to_bench(self, court, space):
        b_scorer.bench.append(b_scorer.courts[court].spaces[space])
        b_scorer.courts[court].spaces[space] = None
        b_scorer.pin_courts[court].spaces[space] = None
        self.update_board()

    #Ensure player isn't put onto the next game
    def keep_player_off(self, court_number, index, player = None):

        # Differentiating between players on the court and the bench
        if court_number == None:
            player = player # due to reconfiguring the way menus work
        else:
            player = b_scorer.courts[court_number].spaces[index]

        # toggle on/off
        if player.keep_off == True:
            player.keep_off = False
        else:
            player.keep_off = True


    def view_player_stats(self, court_number, index, player = None):

        # That is, if it's called from the court
        if player is None:
            player = b_scorer.courts[court_number].spaces[index]
        else:
            pass #i.e. player = player

        self.stats = PlayerStats(self, player, new = False)

    # Open up toplevel widget where the weightings can be modified
    def edit_game_weightings(self):
        self.gamestats = GameStats(self)

    # For the combobox
    def get_all_players(self):
        self.all_player_names = sorted([player.name
                                     for player in b_scorer.absent_players])
        self.all_player_names.insert(0, "")
        self.all_plyr_cbox.config(values = self.all_player_names)
        self.all_plyr_cbox.current(0)


class CourtFrame(tk.Frame):
    def __init__(self, controller, court_number):
        tk.Frame.__init__(self, controller, background=bg_colour)

        #gets updated when created, to distinguish it. Not ideal?
        self.court_number = court_number

        self.labels = [tk.Label(self, text = "-",
                                font=("Helvetica", 33, 'bold'),
                                fg = "white", background = "black",
                                width = 8, height = 4) for i in range(4)]

        # Create the popup menus for each player
        self.popup_menus = []

        for i, label in enumerate(self.labels):
            label.bind("<ButtonPress-3>", lambda event,
                        court_number = self.court_number,
                        index = i: controller.show_options(event, court_number, index))

            self.popup_menus.append(Menu(self, tearoff=0))
            self.popup_menus[i].add_command(command = lambda
                index = i: controller.view_player_stats(self.court_number, index),
                                            label = "View Player Stats")
            self.popup_menus[i].add_command(command = lambda
                index = i: controller.return_to_bench(self.court_number, index),
                                            label="Return to Bench")
            self.popup_menus[i].add_command(command = lambda
                index = i: controller.remove_player_entirely(self.court_number,
                                      index), label="Remove From Night")
            self.popup_menus[i].add_command(command = lambda
                index = i: controller.keep_player_off(self.court_number, index))


        self.labels[0].grid(row = 0, column = 0, sticky="nsew", padx=1, pady=1)
        self.labels[1].grid(row = 0, column = 1, sticky="nsew", padx=1, pady=1)
        self.labels[2].grid(row = 1, column = 0, sticky="nsew", padx=1, pady=1)
        self.labels[3].grid(row = 1, column = 1, sticky="nsew", padx=1, pady=1)

        for column in range(2):
            self.grid_columnconfigure(column, weight=1)

        for row in range(2):
            self.grid_rowconfigure(2, weight=1)


class BenchFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background= bg_colour)


'''Originally I had the popups for creating new players and modifying
them together in the same class, thinking it'd make it more succinct. 
I'd pass in an argument like "new = True"   
However, the two behave in sufficiently different ways that it just made it confusing.
Still, it seems there's a lot of duplication.'''


class NewPlayerWindow(tk.Toplevel):
    def __init__(self, controller):
        tk.Toplevel.__init__(self, controller)

        self.title("Player Stats")
        self.controller = controller

        self.test_label = ttk.Label(self, text = "Create New Player")
        self.name_label = ttk.Label(self, text = "Name")
        self.sex_label = ttk.Label(self, text = "Sex")
        self.ability_label = ttk.Label(self, text = "Ability (1-9)")
        self.partner_aff_label = ttk.Label(self, text = "Partner Affinities")
        self.opp_aff_label = ttk.Label(self, text = "Opponent Affinities")
        self.partner_aff_box = ttk.Combobox(self, width = 8)
        self.opp_aff_box = ttk.Combobox(self, width = 8)

        self.new_partner_aff = ttk.Button(self, text = "New", width =4,
                                          command = self.new_partner_affinity)
        self.new_opp_aff = ttk.Button(self, text = "New", width = 4,
                                      command = self.new_opp_affinity)

        self.save_partner_aff_button = ttk.Button(self, text = "Save",
                                                  width = 5,
                                      command = lambda: self.save_affinity("partner"))
        self.save_opponent_aff_button = ttk.Button(self, text = "Save",
                                                   width = 5,
                                      command = lambda: self.save_affinity("opponent"))

        self.del_partner_aff = ttk.Button(self, text = "Delete", width = 7,
                                          command = self.del_partner_affinity)
        self.del_opp_aff = ttk.Button(self, text = "Delete", width = 7,
                                          command = self.del_opp_affinity)

        self.partner_affs = []
        self.opp_affs = []

        self.name_entry = ttk.Entry(self, width = 11)
        self.sex_combobox = ttk.Combobox(self, width = 8,
                                         values = ["Male", "Female", "Other"],
                                         state = 'readonly')
        self.ability_combobox = ttk.Combobox(self, width = 8,
                                         values = [i for i in range (1,10)],
                                             state = 'readonly')
        self.sex_combobox.current(0)
        self.ability_combobox.current(4)

        self.player_notes = tk.Text(self, height=5, width=15, wrap=tk.WORD)

        self.save_player_button = ttk.Button(self, text = "Save New Player",
                                             command = self.save_player)

        self.test_label.grid(column = 0, row = 0)
        self.name_label.grid(column = 0, row = 1)
        self.name_entry.grid(column = 1, row = 1)
        self.sex_label.grid(column = 0, row = 2)
        self.sex_combobox.grid(column = 1, row = 2)
        self.ability_label.grid(column = 0, row = 3)
        self.ability_combobox.grid(column = 1, row = 3)
        self.partner_aff_label.grid(column = 0, row = 4)
        self.partner_aff_box.grid(column = 1, row = 4)
        self.new_partner_aff.grid(column = 2, row = 4)
        self.save_partner_aff_button.grid(column = 3, row = 4)
        self.del_partner_aff.grid(column = 4, row = 4)
        self.opp_aff_label.grid(column = 0, row = 5)
        self.opp_aff_box.grid(column = 1, row = 5)
        self.new_opp_aff.grid(column = 2, row = 5)
        self.save_opponent_aff_button.grid(column = 3, row = 5)
        self.del_opp_aff.grid(column = 4, row = 5)
        self.player_notes.grid(column = 0, row = 6, columnspan = 2)
        self.save_player_button.grid(column = 1, row = 10)

    def new_partner_affinity(self):
        self.partner_aff_box.delete(0, "end")

    def new_opp_affinity(self):
        self.opp_aff_box.delete(0, "end")

    def del_partner_affinity(self):
        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                            "Are you sure you want to delete this affinity?")

        #UPDATE THIS TO ONLY CHANGE COMBOBOX

        if are_you_sure == True:

            other_player = self.partner_aff_box.get()

            self.player.partner_affinities.remove(other_player)

            self.partner_aff_box.config(values = self.player.partner_affinities)
            self.partner_aff_box.delete(0, "end")

            for other in b_scorer.every_player:
                if other.name == other_player:
                    try:
                        other.partner_affinities.remove(self.player.name)
                    except ValueError: #in case it's not on the other affinity for some reason
                        pass


    def del_opp_affinity(self):
        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                            "Are you sure you want to delete this affinity?")

        if are_you_sure == True:

            other_player = self.opp_aff_box.get()

            self.player.opponent_affinities.remove(other_player)

            self.opp_aff_box.config(values = self.player.opponent_affinities)
            self.opp_aff_box.delete(0, "end")

            for other in b_scorer.every_player:
                if other.name == other_player:
                    try:
                        other.opponent_affinities.remove(self.player.name)
                    except ValueError: #in case it's not on the other affinity for some reason
                        pass

    # Not really in the right place?

    def save_player(self):

        # Should check for identical name first to save time

        are_you_sure = tk.messagebox.askyesno("Are you sure?", "Are you sure you want to save this player?")

        if are_you_sure == False:
            return

        name = self.name_entry.get()
        sex =  self.sex_combobox.get()
        ability = int(self.ability_combobox.get())
        notes = self.player_notes.get("1.0", "end-1c")

        #NEED TO GET THE AFFINITIES FROM THE COMBOBOXES

         # Identical name check
        if name in [player.name for player in b_scorer.every_player]:
            error = tk.messagebox.showerror("Error", "Error: player with identical name found. Please enter a new name")
            return

        ''' Create the player, add them to "every player" and "absent players"
            Then call the add_player function from b_scorer to add them to the bench
            with their respective games etc'''

        New_Player = b_scorer.Player(name, sex, ability)
        New_Player.player_notes = notes
        New_Player.partner_affinities = self.partner_affs
        New_Player.opponent_affinities = self.opp_affs
        b_scorer.every_player.append(New_Player)
        b_scorer.absent_players.append(New_Player)
        b_scorer.add_player(New_Player)
        self.controller.colour_dict = b_scorer.colour_sorter(b_scorer.all_current_players)
        self.controller.add_bench_menus(New_Player)
        self.controller.bench_grid()

        #NOW APPEND THE AFFINITIES TO THE NEW PLAYER
        for player in b_scorer.every_player:
                    if player.name in self.partner_affs:
                        player.partner_affinities.append(name)
                    if player.name in self.opp_affs:
                        player.opponent_affinities.append(name)

        every_pi = open('every_player_pi_2.obj', 'wb')
        pickle.dump(b_scorer.every_player, every_pi)
        every_pi.close()

        self.destroy()

    # Should have a parameter to make it usable for opponent affinities too
    def save_affinity(self, side):

        all_names = [player.name for player in b_scorer.every_player]
        if side == "partner":
            other_player = self.partner_aff_box.get()
        elif side == "opponent":
            other_player = self.opp_aff_box.get()

        if other_player not in all_names:
            not_found = tk.messagebox.showerror("Error",
                                                "Player name not found")
            return

        if side == "partner":
            if other_player in self.partner_affs:
                already_aff = tk.messagebox.showerror("Error",
                                    "Player already has this affinity.")
                return
        elif side == "opponent":
            if other_player in self.opp_affs:
                already_aff = tk.messagebox.showerror("Error",
                                     "Player already has this affinity.")
                return

        # Add affinity to the current player
        if side == "partner":
            self.partner_affs.append(other_player)
            self.partner_aff_box.config(values = self.partner_affs)

        elif side == "opponent":
            self.opp_affs.append(other_player)
            self.opp_aff_box.config(values = self.opp_affs)

        # Now, to add an affinity to the partner. How to do so? Need to find the player in all players, then append theirs
        # Searches them them all and checks if the name is right? Seems slightly inefficient perhaps, but probably doesn't matter?

        player_saved = tk.messagebox.showinfo("Success", "Player's affinity added!")


class PlayerStats(tk.Toplevel):
    def __init__(self, controller, player = None, new = True):

        tk.Toplevel.__init__(self, controller)

        self.title("Player Stats")

        self.controller = controller
        self.new = new
        self.player = player

        #If new player, Create New. If existing, Player Stats
        if self.new == True:
            self.test_label = ttk.Label(self, text = "Create New Player")
        else:
            self.test_label = ttk.Label(self, text = "Player Stats")

        self.name_label = ttk.Label(self, text = "Name")
        self.sex_label = ttk.Label(self, text = "Sex")
        self.ability_label = ttk.Label(self, text = "Ability (1-9)")
        self.partner_aff_label = ttk.Label(self, text = "Partner Affinities")
        self.opp_aff_label = ttk.Label(self, text = "Opponent Affinities")
        self.partner_aff_box = ttk.Combobox(self, width = 8)
        self.opp_aff_box = ttk.Combobox(self, width = 8)

        self.new_partner_aff = ttk.Button(self, text = "New", width = 4, command = self.new_partner_affinity)
        self.new_opp_aff = ttk.Button(self, text = "New", width = 4, command = self.new_opp_affinity)

        self.save_partner_aff_button = ttk.Button(self, text = "Save", width = 5, command = lambda: self.save_affinity("partner"))
        self.save_opponent_aff_button = ttk.Button(self, text = "Save", width = 5, command = lambda: self.save_affinity("opponent"))

        self.del_partner_aff = ttk.Button(self, text = "Delete", width = 7, command = self.del_partner_affinity)
        self.del_opp_aff = ttk.Button(self, text = "Delete", width = 7, command = self.del_opp_affinity)

        self.name_entry = ttk.Entry(self, width = 11)
        self.sex_combobox = ttk.Combobox(self, width = 8, values = ["Male", "Female", "Other"], state = 'readonly')
        self.ability_combobox = ttk.Combobox(self, width = 8, values = [i for i in range (1,10)], state = 'readonly')
        self.sex_combobox.current(0)
        self.ability_combobox.current(4)

        self.games_played_label = ttk.Label(self, text = "Actual Games Played")
        self.games_played_number = ttk.Label(self, text = "0")

        self.late_penalty_label = ttk.Label(self, text = "Lateness Penalty")
        self.late_penalty_entry = ttk.Entry(self, width = 4)

        self.games_total_label = ttk.Label(self, text = "Adjusted Games")
        self.games_total_number = ttk.Label(self, text = "0")                              
                                           

        self.player_notes = tk.Text(self, height=5, width=15, wrap=tk.WORD)

        self.save_player_button = ttk.Button(self, text = "Save New Player", command = self.save_player)

        #If current player, upload their existing stats

        if self.new == False:
            self.name_entry.insert(0, player.name)

            # Should be able to do this more succinctly
            if self.player.sex == "Male":
                self.sex_combobox.current(0)
            elif self.player.sex == "Female":
                self.sex_combobox.current(1)
            else:
                self.sex_combobox.current(2)

            self.ability_combobox.current(self.player.ability - 1)

            self.partner_values = self.player.partner_affinities
            self.partner_aff_box.config(values = self.partner_values)

            self.opp_values = self.player.opponent_affinities

            self.opp_aff_box.config(values = self.opp_values)

            if len(self.partner_values)>0:
                self.partner_aff_box.current(0)
            if len(self.opp_values)>0:
                self.opp_aff_box.current(0)

            self.save_player_button.config(text = "Save Player Stats")

            self.games_played_number.config(text = round(self.player.total_games,2))
            self.late_penalty_entry.insert(0, round(self.player.penalty_games,2))
            self.games_total_number.config(text = round(self.player.adjusted_games,2))
            
            
            self.player_notes.insert(1.0, self.player.player_notes)

        self.test_label.grid(column = 0, row = 0)
        self.name_label.grid(column = 0, row = 1)
        self.name_entry.grid(column = 1, row = 1)
        self.sex_label.grid(column = 0, row = 2)
        self.sex_combobox.grid(column = 1, row = 2)
        self.ability_label.grid(column = 0, row = 3)
        self.ability_combobox.grid(column = 1, row = 3)
        self.partner_aff_label.grid(column = 0, row = 4)
        self.partner_aff_box.grid(column = 1, row = 4)
        self.new_partner_aff.grid(column = 2, row = 4)
        self.save_partner_aff_button.grid(column = 3, row = 4)
        self.del_partner_aff.grid(column = 4, row = 4)
        self.opp_aff_label.grid(column = 0, row = 5)
        self.opp_aff_box.grid(column = 1, row = 5)
        self.new_opp_aff.grid(column = 2, row = 5)
        self.save_opponent_aff_button.grid(column = 3, row = 5)
        self.del_opp_aff.grid(column = 4, row = 5)
        self.games_played_label.grid(column = 0, row = 6)
        self.games_played_number.grid(column = 1, row = 6)
        self.late_penalty_label.grid(column = 0, row = 7)
        self.late_penalty_entry.grid(column = 1, row = 7)

        self.games_total_label.grid(column = 0, row = 8)
        self.games_total_number.grid(column = 1, row = 8)
        
        self.player_notes.grid(column = 0, row = 9, columnspan = 2)


        self.save_player_button.grid(column = 1, row = 10)

    def new_partner_affinity(self):
        self.partner_aff_box.delete(0, "end")

    def new_opp_affinity(self):
        self.opp_aff_box.delete(0, "end")

    def del_partner_affinity(self):
        are_you_sure = tk.messagebox.askyesno("Are you sure?", "Are you sure you want to delete this affinity?")

        if are_you_sure == True:

            other_player = self.partner_aff_box.get()

            self.player.partner_affinities.remove(other_player)

            self.partner_aff_box.config(values = self.player.partner_affinities)
            self.partner_aff_box.delete(0, "end")

            for other in b_scorer.every_player:
                if other.name == other_player:
                    try:
                        other.partner_affinities.remove(self.player.name)
                    except ValueError: #in case it's not on the other affinity for some reason
                        pass



    def del_opp_affinity(self):
        are_you_sure = tk.messagebox.askyesno("Are you sure?", "Are you sure you want to delete this affinity?")

        if are_you_sure == True:

            other_player = self.opp_aff_box.get()

            self.player.opponent_affinities.remove(other_player)

            self.opp_aff_box.config(values = self.player.opponent_affinities)
            self.opp_aff_box.delete(0, "end")

            for other in b_scorer.every_player:
                if other.name == other_player:
                    try:
                        other.opponent_affinities.remove(self.player.name)
                    except ValueError: #in case it's not on the other affinity for some reason
                        pass

    #

    def save_player(self):

        # Should check for identical name first to save time

        are_you_sure = tk.messagebox.askyesno("Are you sure?", "Are you sure you want to save this player?")

        if are_you_sure == False:
            return

        name = self.name_entry.get()
        sex =  self.sex_combobox.get()
        ability = int(self.ability_combobox.get())
        notes = self.player_notes.get("1.0", "end-1c")
        
        try:
            late_penalty = float(self.late_penalty_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a valid lateness penalty")
            return
    
        #if the player's name is changed, update all the affinities

        if self.player.name != name:
            for player in b_scorer.every_player:
                if player.name in self.player.partner_affinities:
                    try:
                        player.partner_affinities.remove(self.player.name)
                    except ValueError:
                        pass
                    player.partner_affinities.append(name)
                if player.name in self.player.opponent_affinities:
                    try:
                        player.partner_affinities.remove(self.player.name)
                    except ValueError:
                        pass
                    player.opponent_affinities.append(name)


        self.player.name = name

        self.player.sex = sex
        self.player.ability = ability
        self.player.player_notes = notes

        self.player.penalty_games = late_penalty
        self.player.adjusted_games = self.player.total_games +  late_penalty


        every_pi = open('every_player_pi_2.obj', 'wb')
        pickle.dump(b_scorer.every_player, every_pi)
        every_pi.close()

        self.controller.update_board()

        self.destroy()

    # Should have a parameter to make it usable for opponent affinities too
    def save_affinity(self, side):

        # Organise this better

        all_names = [player.name for player in b_scorer.every_player]
        if side == "partner":
            other_player = self.partner_aff_box.get()
        elif side == "opponent":
            other_player = self.opp_aff_box.get()


        if other_player not in all_names:
            not_found = tk.messagebox.showerror("Error", "Player name not found")
            return


        if side == "partner":
            if other_player in self.player.partner_affinities:
                already_aff = tk.messagebox.showerror("Error", "Player already has this affinity.")
                return
        elif side == "opponent":
            if other_player in self.player.opponent_affinities:
                already_aff = tk.messagebox.showerror("Error", "Player already has this affinity.")
                return


        # What if the player object isn't created yet?
        # Could temporarily create the object, then delete it if it isn't saved
        # Or could avoid having affinities an option with new players? Seems kind of annoying though.

        #Not very elegant


        # Add affinity to the current player
        if side == "partner":
            self.player.partner_affinities.append(other_player)
            self.partner_aff_box.config(values = self.player.partner_affinities)
            if self.new is False:
                for player in b_scorer.every_player:
                    if player.name == other_player:
                        player.partner_affinities.append(self.player.name)
        elif side == "opponent":
            self.player.opponent_affinities.append(other_player)
            self.opp_aff_box.config(values = self.player.opponent_affinities)
            if self.new is False:
                for player in b_scorer.every_player:
                    if player.name == other_player:
                        player.opponent_affinities.append(self.player.name)

        player_saved = tk.messagebox.showinfo("Success", "Player's affinity added!")


class GameStats(tk.Toplevel):
    def __init__(self, controller):

        tk.Toplevel.__init__(self, controller)

        self.controller = controller
        self.title("Weightings for Game Scoring Algorithm")

        self.bal_label = ttk.Label(self, text="Game Balance Weighting")
        self.seg_label = ttk.Label(self, text="Ability Segregation Weighting")
        self.mix_label = ttk.Label(self, text="Player Mixing Weighting")
        self.aff_label = ttk.Label(self, text="Player Affinity Weighting")
        
        self.shuffle_label = ttk.Label(self, text = "Shuffle Algorithm")

        self.bal_entry = ttk.Entry(self, width = 4)
        self.seg_entry = ttk.Entry(self, width = 4)
        self.mix_entry = ttk.Entry(self, width = 4)
        self.aff_entry = ttk.Entry(self, width = 4)
        self.shuffle_combo = ttk.Combobox(self, width = 10,
                                          values = ["Random", "Segregated"])
              

        self.bal_entry.insert(0, b_scorer.enumerate_b.scoring_vars[0])
        self.seg_entry.insert(0, b_scorer.enumerate_b.scoring_vars[1])
        self.mix_entry.insert(0, b_scorer.enumerate_b.scoring_vars[2])
        self.aff_entry.insert(0, b_scorer.enumerate_b.scoring_vars[3])
        self.shuffle_combo.current(b_scorer.enumerate_b.scoring_vars[4])

        self.default_button = ttk.Button(self, text = "Return to Default", command = self.return_default_weightings)
        self.save_button = ttk.Button(self, text = "Save Weightings", command = self.save_weightings)

        self.bal_label.grid(column = 0, row = 1)
        self.bal_entry.grid(column = 1, row = 1)
        self.seg_label.grid(column = 0, row = 2)
        self.seg_entry.grid(column = 1, row = 2)
        self.mix_label.grid(column = 0, row = 3)
        self.mix_entry.grid(column = 1, row = 3)
        self.aff_label.grid(column = 0, row = 4)
        self.aff_entry.grid(column = 1, row = 4)
        self.shuffle_label.grid(column = 0, row = 5)
        self.shuffle_combo.grid(column = 1, row = 5) 
        self.default_button.grid(column = 0, row = 6)
        self.save_button.grid(column = 1, row = 6)


    def save_weightings(self):
        # Check to see if you want to update
        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                        "Are you sure you want to update these weightings? "
                        "They will affect the way every game is generated from now on.")
        if are_you_sure is True:

            # Ensure all entries are floats, then update the new weightings
            # Double imported naming seems wonky
            try:
                b_scorer.enumerate_b.scoring_vars[0] = float(self.bal_entry.get())
                b_scorer.enumerate_b.scoring_vars[1] = float(self.seg_entry.get())
                b_scorer.enumerate_b.scoring_vars[2] = float(self.mix_entry.get())
                b_scorer.enumerate_b.scoring_vars[3] = float(self.aff_entry.get())
                b_scorer.enumerate_b.scoring_vars[4] = self.shuffle_combo.current()
            

                # MMmmmm score pie
                score_pi = open('score_pi.obj', 'wb')
                pickle.dump(b_scorer.enumerate_b.scoring_vars, score_pi)
                score_pi.close()

                self.destroy()

            except ValueError:
                error = tk.messagebox.showerror("Error",
                        "Please ensure all values are numbers only.")


    def return_default_weightings(self):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                "Are you sure you want to return to the default weightings?")

        if are_you_sure is True:
            b_scorer.enumerate_b.scoring_vars[0] = 5.0
            b_scorer.enumerate_b.scoring_vars[1] = 3.0
            b_scorer.enumerate_b.scoring_vars[2] = 1.0
            b_scorer.enumerate_b.scoring_vars[3] = 6.0

            # should be able to loop

            self.bal_entry.delete(0, "end")
            self.seg_entry.delete(0, "end")
            self.mix_entry.delete(0, "end")
            self.aff_entry.delete(0, "end")

            self.bal_entry.insert(0, b_scorer.enumerate_b.scoring_vars[0])
            self.seg_entry.insert(0, b_scorer.enumerate_b.scoring_vars[1])
            self.mix_entry.insert(0, b_scorer.enumerate_b.scoring_vars[2])
            self.aff_entry.insert(0, b_scorer.enumerate_b.scoring_vars[3])


if __name__ == '__main__':

    bg_colour = "light blue"

    app = Application()
    app.configure(background = bg_colour)
    app.mainloop()