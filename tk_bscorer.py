'''A GUI for placing players on the courts in a way that is ideally
readable by the players themselves.'''

import tkinter as tk
from tkinter import Tk, ttk, Frame, Menu, messagebox, Scrollbar
from tkinter.messagebox import showinfo, askyesno, showerror
import b_scorer
import b_sessions
import pickle
import random
import datetime
from datetime import datetime # huh?

class Application(tk.Tk):
    """The main application"""
    def __init__(self):
        tk.Tk.__init__(self)

        # A (probably unPythonic) way of randomly loading the bench
        self.test_mode = False

        self.title("Badminton Matchmaker")

        self.protocol("WM_DELETE_WINDOW", lambda: self.confirm_quit())

        self.bench_popup_menus = {}
        self.court_menus = {}
        self.space_menus = {}

        start_menu = Menu(self)
        self.config(menu=start_menu)

        start_menu.add_cascade(label="Help", command = lambda: self.help())

        self.court_labels = [ttk.Label(text="Court {}".format(i + 1),
                                       background=bg_colour,
                                       font=('Helvetica', 33, 'bold')) for i
                             in range(3)]

        self.court_frames = [CourtFrame(self, i) for i in range(3)]
        self.absent_label = ttk.Label(text="Absent Players",
                                      background=bg_colour,
                                      font=('Helvetica', 16, 'bold'))
        self.bench_label = ttk.Label(text="Bench",
                                     background=bg_colour,
                                     font=('Helvetica', 24, 'bold'))
        self.bench = BenchFrame(self)
        # Create labels representing players on the bench
        self.bench_labels = [tk.Label(self.bench,
                                      text=player.name, width=8,
                                      height=2) for player in b_scorer.bench]

        # These attempts to format my lines to >80 characters seem unnatural

        # The names of the Players who haven't joined
        self.abs_plyr_cbox = ttk.Combobox(self, width=24,
                                          postcommand=self.refresh_combobox)
        self.abs_plyr_cbox.config(values=["Select or "
                                          "type-in name..."])
        self.abs_plyr_cbox.current(0)
        self.abs_plyr_cbox.bind('<FocusIn>',
                                lambda event: self.player_cbox_clear())
        self.abs_plyr_cbox.bind('<Return>', lambda event: self.add_player())

        self.add_player_button = ttk.Button(self,
                                            text="Add Player to Bench",
                                            command=self.add_player)
        self.create_player_button = ttk.Button(self,
                                               text="Create New Player",
                                               command=self.create_player)
        self.delete_player_button = ttk.Button(self, text="Delete Player",
                                               command=self.delete_player)
        self.game_history_button = ttk.Button(self, text="View Game "
                                                         "History", command=
                                              self.view_history)

        self.rounds_label = ttk.Label(text="Rounds: {}".format(
            b_scorer.total_rounds),
                                      background=bg_colour,
                                      font=('Helvetica', 16, 'bold'))
        self.start_button = ttk.Button(self, text="Generate New Board",
                                       command=self.start)
        self.confirm_button = ttk.Button(self, text="Confirm Board",
                                         command=self.confirm)
        self.undo_confirm_button = ttk.Button(self, text="Undo Confirm",
                                         command=self.undo_confirm)

        self.game_weighting_button = ttk.Button(self,
                                                text="Change Automatic Rules",
                                                command=self.edit_game_weightings)
        self.empty_courts_button = ttk.Button(self, text="Empty Courts",
                                              command=self.empty_courts)

        self.undo_confirm_button.configure(state="disabled")

        for i, court in enumerate(self.court_labels):
            court.grid(column=(5 * i) + 2, row=2, sticky='nsew',
                       padx=10, pady=10)

        for i, court in enumerate(self.court_frames):
            court.grid(column=5 * i, row=5, rowspan=5, columnspan=5,
                       padx=10, pady=10, sticky='nsew')

        for i in range(50):
            self.columnconfigure(i, weight=1)
            self.rowconfigure(i, weight=1)

        self.absent_label.grid(column=1, row=15, columnspan=2)
        self.abs_plyr_cbox.grid(column=1, row=16, columnspan=2,
                                padx=2, pady=2)

        self.add_player_button.grid(column=2, row=17,
                                    sticky='nsew', padx=1, pady=1)
        self.create_player_button.grid(column=1, row=17,
                                       sticky='nsew', padx=1, pady=1)
        self.delete_player_button.grid(column=1, row=18,
                                       sticky='nsew', padx=1, pady=1)
        self.game_history_button.grid(column=2, row=18,
                                       sticky='nsew', padx=1, pady=1)

        self.bench_label.grid(column=7, row=15, columnspan=2,
                              padx=1, pady=1)
        self.bench.grid(column=4, row=16, columnspan=7, rowspan=5,
                        sticky='nsew', padx=1, pady=1)

        self.rounds_label.grid(column=12, row=15, columnspan=2)
        self.start_button.grid(column=12, row=16, sticky='nsew',
                               padx=1, pady=1)
        self.confirm_button.grid(column=13, row=16, sticky='nsew',
                                 padx=1, pady=1)
        self.undo_confirm_button.grid(column=14, row=16, sticky='nsew',
                                 padx=1, pady=1)
        self.empty_courts_button.grid(column=13, row=17, sticky='nsew',
                                      padx=1, pady=1)
        self.game_weighting_button.grid(column=12, row=17, sticky='nsew',
                                        padx=1, pady=1)

        if self.test_mode is True:
            random.shuffle(b_scorer.every_player)
            for player in b_scorer.every_player[0:17]:
                b_scorer.add_player(player)
                self.add_bench_menus(player)
            self.colour_dict = b_scorer.colour_sorter(
                b_scorer.all_current_players)

        # If program crashed or exited otherwise normally, reload all data
        try:
            pickle_in = open("board_data.obj", "rb")
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
            self.confirm_button.configure(state=board_data["confirm_state"])
            if str(board_data["confirm_state"]) == "disabled":
                self.undo_confirm_button.configure(state = "normal")
            elif str(board_data["confirm_state"]) == "normal":
                self.undo_confirm_button.configure(state="disabled")
            for player in b_scorer.all_current_players:
                self.add_bench_menus(player)
            pickle_in.close()
            # If it hasn't been saved before, or was blanked when it quit
        except KeyError:  # board_data was blanked on exit
             pickle_in.close()

        self.update_board()

    def help(self):
        """produces help popup"""
        self.help_menu = HelpMenu(self)


    def autosave(self):
        """Save the current state, such that if the program/computer
        crashes, restarting the program will reload the previous state of it"""

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

        every_pi = open('every_player_pi_2.obj', 'wb')
        pickle.dump(b_scorer.every_player, every_pi)
        every_pi.close()

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

        """Clears the absent player combobox if it's currently on the default
        text"""

        entry = self.abs_plyr_cbox

        if entry.get() == "Select or type-in name...":
            entry.delete(0, "end")  # delete all the text in the entry
            entry.insert(0, '')  # Insert blank for user input

    def empty_courts(self):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to "
                                              "empty the courts?")
        if are_you_sure is True:
            b_scorer.empty_courts()
            self.confirm_button.configure(state="normal")
            self.undo_confirm_button.configure(state="disabled")
            self.update_board()

    def quick_pay(self, player):
        player.pay_fee()
        self.bench_grid()
        # replace menu
        self.add_bench_menus(player)


    def add_bench_menus(self, player):
        """Creates the pop-up menus for a given player (for the bench,
        the court, and for selecting the space to be added to from the
        bench), then saves them each to a dictionary"""

        self.bench_popup_menus[player] = Menu(self, tearoff=0)
        self.court_menus[player] = Menu(self, tearoff=0)
        self.space_menus[player] = []

        # The methods call the court names and numbers, which are invalid here
        # Seems ugly, can't figure out how to get to >80 characters without
        # making it even uglier
        self.bench_popup_menus[player].add_command(command=lambda: self.view_player_stats(None, None, player),
                                                   label="View Player Profile")
        self.bench_popup_menus[player].add_command(command=lambda: self.remove_player_entirely(None, None, player),
                                                   label="Remove From Night")
        self.bench_popup_menus[player].add_command(command=lambda: self.keep_player_off(None, None, player),
                                                   label="Keep Player Off Next Round")
        self.bench_popup_menus[player].add_command(
            command=lambda: self.keep_player_on(None, None, player),
            label="Keep Player On Next Round")

        if not player.paid_tonight:
            self.bench_popup_menus[player].add_command(
            command = lambda: self.quick_pay(player),
            label="Pay Tonight's Fee")

        self.bench_popup_menus[player].add_cascade(menu=self.court_menus[player],
                                                   label="Pin to Court...", )
        # Add menu options for manually adding players to courts
        for j in range(3):
            self.space_menus[player].append(Menu(self, tearoff=0))
            self.court_menus[player].add_cascade(label="#{}...".format(j + 1),
                                                 menu=self.space_menus[player][j])

            for k in range(4):
                self.space_menus[player][j].add_command(
                    label="Space {}".format(k + 1),
                    command=lambda player=player, court=j, space=k:
                    self.bench_to_court(player, court, space))

    def bench_grid(self):
        """Regrid the players on the bench, update size and colours"""

        # Forget current labels.
        for label in self.bench.grid_slaves():
            label.grid_forget()

        # Adjust label values for size of grid. Fewer players = bigger labels
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

        self.bench_labels = [tk.Label(self.bench, width=custom_width,
                                      height=custom_height,
                                      font=custom_font,
                                      text=player.name) for player in
                             b_scorer.bench]

        for i, label in enumerate(self.bench_labels):
            player = b_scorer.bench[i]

            # players who owe money get their name italicised
            if player.money_owed > 0:
                # turn font into list to modify it, then back to tuple.
                # seems dirty?
                new_font = list(custom_font)
                new_font[2] = 'bold italic'
                self.bench_labels[i].config(font = tuple(new_font))

            label.bind("<ButtonPress-3>", lambda event, player=player: self.show_bench_options(event, player))
            self.bench_labels[i].config(background=self.colour_dict[player])

        # Creating the bench labels

        count = -1
        new_row = 0

        for i, label in enumerate(self.bench_labels):
            count += 1
            if count == players_per_row:
                count = 0
                new_row += 1
            label.grid(column=count, row=new_row,
                       padx=custom_pad, pady=custom_pad, sticky='nsew')

    def colour_change(self):
        """Rejig the colours off the bench"""
        self.colour_dict = b_scorer.colour_sorter(
            b_scorer.all_current_players)
        self.bench_grid()

    def bench_to_court(self, player, court, space):
        """Manually add a player from the bench to the court"""

        if b_scorer.courts[court].spaces[space] is not None:
            tk.messagebox.showerror("Error", "Player already in that space")
        else:
            b_scorer.courts[court].spaces[space] = player
            b_scorer.bench.remove(player)
            self.update_board()

    def add_player(self):
        """From the absent players combobox, add a player to the bench. If a
        typed-in name is not found, prompt the user to create a new player
        with that name."""

        selected = self.abs_plyr_cbox.get()
        existing = [player.name for player in b_scorer.every_player]
        currents = [player.name for player in b_scorer.all_current_players]


        if selected == "Select or type-in name...":
            error = tk.messagebox.showerror("Error",
                                            "Please select a player to add "
                                            "to the board.")
            return
        elif selected not in existing:
            new_query = tk.messagebox.askyesno("Player Not Found",
                                               "No player with that name found!"
                                               " Would you like to create "
                                               "this player?")
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
                    self.colour_dict = b_scorer.colour_sorter(
                        b_scorer.all_current_players)
                    self.add_bench_menus(player)
        # Refresh the combobox with the new values
        self.refresh_combobox()

        # Refresh the grid
        self.bench_grid()

        self.autosave()

    def create_player(self):
        """Launch a popup for creating new players"""
        self.create_toplevel = PlayerStats(self)

    def delete_player(self):
        """From the absent players combobox, delete the selected player,
        then update other things. Given some of those things aren't core GUI
        logic, I suppose it'd be a good idea to move them to a different
        module/class"""

        selected = self.abs_plyr_cbox.get()
        if selected == "Select or type-in name...":
            error = tk.messagebox.showerror("Error",
                                            "Please select a player to delete.")
        else:
            query = tk.messagebox.askyesno("Are you sure?",
                                           "Are you sure you want to "
                                           "permanently delete this player?")
            if query is True:
                # Surely there should be a better way of deleting a player?
                b_scorer.absent_players = [player for player
                                           in b_scorer.absent_players
                                           if player.name != selected]
                b_scorer.every_player = [player for player
                                         in b_scorer.every_player
                                         if player.name != selected]
                self.abs_plyr_cbox.current(0)

                # Delete all affinities
                for player in b_scorer.every_player:
                    if selected in player.partner_affinities:
                        player.partner_affinities.remove(selected)
                    if selected in player.opponent_affinities:
                        player.opponent_affinities.remove(selected)

                # Save to pickle
                self.autosave()

    def remove_player_entirely(self, court_number, index, player=None):
        """Return a current player to absent players, then update relevant
        information"""

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure this player is "
                                              "leaving?")

        if are_you_sure is True:
            b_scorer.remove_player(court_number, index, player)
            self.colour_dict = b_scorer.colour_sorter(
                b_scorer.all_current_players)
            self.refresh_combobox()
            self.update_board()
            self.autosave()


    def start(self):
        """Calls b_scorer.generate_new_game.

        Can't make game with <12 players. Rather than figure out a
        way of creating singles matches, I'm just going to leave it up to the
        person to do it manually"""

        if len(b_scorer.all_current_players) < 12:
            tk.messagebox.showerror(
                "Error", "There are fewer players available than spaces"
                         " on courts! This program can't handle that.")
        else:

            b_scorer.generate_new_game()
            self.update_board()
            self.confirm_button.configure(state="normal")
            self.undo_confirm_button.configure(state="disabled")

    def confirm(self):
        """Call b_scorer's confirm_game() function, update and autosave"""

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to "
                                              "confirm this game for the "
                                              "next round?")

        if are_you_sure is True:
            b_scorer.confirm_game()
            self.colour_dict = b_scorer.colour_sorter(
                b_scorer.all_current_players)
            self.update_board()
            # Disabled to stop you accidentally pressing it multiple times
            self.confirm_button.configure(state="disabled")
            self.undo_confirm_button.configure(state="normal")

            self.autosave()

    def undo_confirm(self):
        """In case you made a mistake confirming"""
        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to undo "
                                              "the confirmation?")

        if are_you_sure is True:
            b_scorer.undo_confirm()
            self.colour_dict = b_scorer.colour_sorter(
                b_scorer.all_current_players)
            self.update_board()
            self.undo_confirm_button.configure(state="disabled")
            self.confirm_button.configure(state="normal")
            self.autosave()



    def update_board(self):
        """Whenever anything is updated, redisplay all courts and labels.
        Seems kind of wasteful - doesn't matter too much here, but it will
        often redisplay things that aren't changing"""

        # Display all player on the courts, unless the courts are empty.
        for i, court in enumerate(self.court_frames):
            for j, label in enumerate(court.labels):
                try:
                    name = b_scorer.courts[i].spaces[j].name
                    label.config(text=name, font=("Helvetica", 32, 'bold'))

                except AttributeError:  # if there is no-one in that space
                    label.config(text="-")

        # Update the rounds label
        self.rounds_label.config(text="Rounds: {}".format(
            b_scorer.total_rounds))

        # Redisplay the bench
        self.bench_grid()


    def show_bench_options(self, event, player):
        """When bench label clicked, show the menu"""

        if player.keep_off is False:
            self.bench_popup_menus[player].entryconfigure(2,label="Keep "
                                                                  "Player Off "
                                                                  "Next Round")
        else:
            self.bench_popup_menus[player].entryconfigure(2,
                                                          label="Undo Keep "
                                                                "Player Off")

        if player.keep_on is False:
            self.bench_popup_menus[player].entryconfigure(3,label="Keep "
                                                                  "Player On "
                                                                  "Next Round")
        else:
            self.bench_popup_menus[player].entryconfigure(3,
                                                          label="Undo Keep "
                                                                "Player On")

        self.bench_popup_menus[player].post(event.x_root, event.y_root)

    def show_court_options(self, event, court_number, index):
        """Similar to the above, but for the court labels. Could probably
        combine into one function?"""

        # Show popup only when the court is full.
        if b_scorer.courts[court_number].spaces[index] is not None:

            player = b_scorer.courts[court_number].spaces[index]
            # If the player is already "kept off", configure the label to "undo keep off"
            # Can't manage to get it to >80 characters
            if player.keep_off is False:
                self.court_frames[court_number].popup_menus[
                    index].entryconfigure(3,
                                          label="Keep Player Off Next Round")
            else:
                self.court_frames[court_number].popup_menus[
                    index].entryconfigure(3,
                                          label="Undo Keep Player Off")
            if player.keep_on is False:
                self.court_frames[court_number].popup_menus[
                    index].entryconfigure(4,
                                          label="Keep Player On Next Round")
            else:
                self.court_frames[court_number].popup_menus[
                    index].entryconfigure(4,
                                          label="Undo Keep Player On")



            self.court_frames[court_number].popup_menus[index].post(event.x_root, event.y_root)

    def return_to_bench(self, court, space):
        """Returns a player from the court to the bench"""
        b_scorer.bench.append(b_scorer.courts[court].spaces[space])
        b_scorer.courts[court].spaces[space] = None
        self.update_board()


    def keep_player_off(self, court_number, index, player=None):
        """Ensure player isn't put onto the next game. Should probably be in """

        # Ensure there aren't too many players off
        players_available = [player for player in b_scorer.all_current_players
                             if not player.keep_off]
        if len(players_available) <=12:
            tk.messagebox.showerror("Error", "Keeping this player off would "
                                             "leave you with too few "
                                             "players!", parent= self)
            return


        # Differentiating between players on the court and the bench
        if court_number is None:
            player = player # due to reconfiguring the way menus work
        else:
            player = b_scorer.courts[court_number].spaces[index]

        # toggle on/off
        if player.keep_off is True:
            player.keep_off = False
        else:
            player.keep_off = True
            player.keep_on = False

        self.colour_change()

    def keep_player_on(self, court_number, index, player=None):

        # Ensure there aren't too many players on
        players_kept_on = [player for player in b_scorer.all_current_players
                             if player.keep_on]
        if len(players_kept_on) >=12:
            tk.messagebox.showerror("Error", "You can't keep on more players "
                                             "than there are spaces on the "
                                             "court!", parent= self)
            return

        # Differentiating between players on the court and the bench
        if court_number is None:
            player = player # due to reconfiguring the way menus work
        else:
            player = b_scorer.courts[court_number].spaces[index]

        # toggle on/off
        if player.keep_on is True:
            player.keep_on = False
        else:
            player.keep_on = True
            player.keep_off = False

        self.colour_change()

    def view_player_stats(self, court_number, index, player=None):
        """Create a top-level popup menu which displays editable statistics
        about that player, such as their total games played and affinities
        for others"""

        # That is, if it's called from the court
        if player is None:
            player = b_scorer.courts[court_number].spaces[index]
        else:
            pass  # i.e. player = player

        self.stats = PlayerStats(self, player, new=False)

    def edit_game_weightings(self):
        """Open up top-level widget where the weightings can be modified"""
        self.gamestats = GameStats(self)

    def refresh_combobox(self):
        """Refresh the combobox of absent players"""
        self.all_player_names = sorted([player.name
                                        for player in b_scorer.absent_players])
        self.all_player_names.insert(0, "")
        self.abs_plyr_cbox.config(values=self.all_player_names)
        self.abs_plyr_cbox.current(0)

    def view_history(self):
        self.history = HistoryPopup(self)


class CourtFrame(tk.Frame):
    """A frame for each of the courts to be placed in"""
    def __init__(self, controller, court_number):
        tk.Frame.__init__(self, controller, background=bg_colour)

        # gets updated when created, to distinguish it. Not ideal?
        self.court_number = court_number

        self.labels = [tk.Label(self, text="-",
                                font=("Helvetica", 33, 'bold'),
                                fg="white", background="black",
                                width=8, height=4) for i in range(4)]

        # Create the popup menus for each player
        self.popup_menus = []

        for i, label in enumerate(self.labels):
            label.bind("<ButtonPress-3>", lambda event,
                       court_no=self.court_number,
                       index=i: controller.show_court_options(event,
                                                              court_no, index))

            self.popup_menus.append(Menu(self, tearoff=0))
            self.popup_menus[i].add_command(command=lambda
                index=i: controller.view_player_stats(self.court_number, index),
                                            label="View Player Profile")
            self.popup_menus[i].add_command(command=lambda
                index=i: controller.return_to_bench(self.court_number, index),
                                            label="Return to Bench")
            self.popup_menus[i].add_command(command=lambda
                index=i: controller.remove_player_entirely(self.court_number,
                                                           index),
                                            label="Remove From Night")
            self.popup_menus[i].add_command(command=lambda
                index=i: controller.keep_player_off(self.court_number, index))
            self.popup_menus[i].add_command(command=lambda
                index=i: controller.keep_player_on(self.court_number, index))


        # padding creates a de facto border
        self.labels[0].grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.labels[1].grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        self.labels[2].grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        self.labels[3].grid(row=1, column=1, sticky="nsew", padx=1, pady=1)

        for column in range(2):
            self.grid_columnconfigure(column, weight=1)

        for row in range(2):
            self.grid_rowconfigure(row, weight=1)


class BenchFrame(tk.Frame):
    """A frame for placing the labels of the players who are on the bench.
    Seems bad that it's basically blank, though it does work"""
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background=bg_colour)

class PlayerStats(tk.Toplevel):
    """Using the same class for new and existing player popups.
    Can make it a bit confusing"""
    def __init__(self, controller, player=None, new=True):

        tk.Toplevel.__init__(self, controller)

        self.controller = controller
        self.new = new
        self.player = player

        # If new player, Create New. If existing, Player Stats
        if self.new is True:
            self.title("Create New Player")
        else:
            self.title("Player Profile")

        self.name_label = ttk.Label(self, text="Name")
        self.sex_label = ttk.Label(self, text="Sex")
        self.ability_label = ttk.Label(self, text="Ability (1-9)")
        self.membership_label = ttk.Label(self, text = "Membership Status")
        self.owed_label =  ttk.Label(self, text = "Money Owed ($)")
        self.partner_aff_label = ttk.Label(self, text="Partner Affinities")
        self.opp_aff_label = ttk.Label(self, text="Opponent Affinities")
        self.partner_aff_box = ttk.Combobox(self, width=8)
        self.partner_aff_level_box = ttk.Combobox(self, width=8, values=[
            "Low", "Medium", "High", "Maximum"], state='readonly')
        self.opp_aff_box = ttk.Combobox(self, width=8)
        self.opp_aff_level_box = ttk.Combobox(self, width=8,
                                              values=["Low", "Medium",
                                                      "High", "Maximum"],
                                              state='readonly')

        self.new_partner_aff = ttk.Button(self, text="New", width=4,
                                          command=self.new_partner_affinity)
        self.new_opp_aff = ttk.Button(self, text="New", width=4,
                                      command=self.new_opp_affinity)

        self.save_par_aff_butn = ttk.Button(self, text="Save", width=5,
                                            command=lambda: self.save_affinity(
                                                      "partner"))
        self.save_opp_aff_butn = ttk.Button(self, text="Save", width=5,
                                            command=lambda: self.save_affinity(
                                                       "opponent"))

        self.del_partner_aff = ttk.Button(self, text="Delete", width=6,
                                          command=lambda:
                                          self.del_affinity("partner"))
        self.del_opp_aff = ttk.Button(self, text="Delete", width=6,
                                      command=lambda:
                                      self.del_affinity("opponent"))

        self.name_entry = ttk.Entry(self, width=11)
        self.sex_combobox = ttk.Combobox(self, width=8,
                                         values=["Male", "Female", "Other"],
                                         state='readonly')
        self.ability_combobox = ttk.Combobox(self, width=8,
                                             values=[i for i in range(1, 10)],
                                             state='readonly')
        self.membership_cbox = ttk.Combobox(self, width=8,
                                             values=["Casual", "Member (no "
                                                    "feathers)", "Member ("
                                                    "incl. feathers)"],
                                                state='readonly')
        self.owed_entry = ttk.Entry(self, width = 11)
        self.pay_owed_button = ttk.Button(self, text = "Pay Off", command =
                                          self.pay_off)

        self.games_played_label = ttk.Label(self, text="Actual Games Played")
        self.games_played_number = ttk.Label(self, text="0")

        self.late_penalty_label = ttk.Label(self, text="Lateness Penalty")
        self.late_penalty_entry = ttk.Entry(self, width=4)

        self.games_total_label = ttk.Label(self, text="Adjusted Games")
        self.games_total_number = ttk.Label(self, text="0")

        self.player_notes_label = ttk.Label(self, text="Player Notes")
        self.player_notes = tk.Text(self, height=5, width=15, wrap=tk.WORD)

        self.save_player_button = ttk.Button(self, text="Save New Player",
                                             command=self.save_player)
        
        self.sex_combobox.current(0)
        self.ability_combobox.current(4)
        self.membership_cbox.current(0)
        self.owed_entry.insert(0, 0)
        self.partner_aff_level_box.current(1)
        self.opp_aff_level_box.current(1)

        # So new players can get affs saved when their objects don't exist yet
        # Should move
        self.partner_affs = []
        self.opp_affs = []

        # If current player, upload their existing stats

        if self.new is False:
            self.name_entry.insert(0, player.name)

            # Should be able to do this more succinctly
            if self.player.sex == "Male":
                self.sex_combobox.current(0)
            elif self.player.sex == "Female":
                self.sex_combobox.current(1)
            else:
                self.sex_combobox.current(2)

            self.ability_combobox.current(self.player.ability - 1)

            # Isn't very extensible
            if self.player.membership == "Casual":
                self.membership_cbox.current(0)
                # self.player.money_owed +=
            elif self.player.membership == "Member (no feathers)":
                self.membership_cbox.current(1)
            else:
                self.membership_cbox.current(2)

            self.owed_entry.delete(0, "end")
            self.owed_entry.insert(0, self.player.money_owed)


            self.partner_affs = self.player.partner_affinities
            self.partner_aff_box.config(values=[p[0] for p in
                                                self.partner_affs])

            self.opp_affs = self.player.opponent_affinities
            self.opp_aff_box.config(values=[p[0] for p in
                                                self.opp_affs])

            if len(self.partner_affs) > 0:
                self.partner_aff_box.current(0)
                self.switch_aff("partner")

                # self.partner_aff_level_box.current(
            if len(self.opp_affs) > 0:
                self.opp_aff_box.current(0)
                self.switch_aff("opponent")
                # self.opp_aff_level_box.current()

            self.partner_aff_box.bind("<<ComboboxSelected>>",
                                    lambda event: self.switch_aff("partner"))

            self.opp_aff_box.bind("<<ComboboxSelected>>",
                                      lambda event: self.switch_aff("opponent"))

            self.save_player_button.config(text="Save Player Stats")

            self.games_played_number.config(
                text=round(self.player.total_games, 2))
            self.late_penalty_entry.insert(0,
                                           round(self.player.penalty_games, 2))
            self.games_total_number.config(
                text=round(self.player.adjusted_games, 2))

            self.player_notes.insert(1.0, self.player.player_notes)

        self.name_label.grid(column=0, row=1)
        self.name_entry.grid(column=1, row=1, columnspan=3, sticky='ew')
        self.sex_label.grid(column=0, row=2)
        self.sex_combobox.grid(column=1, row=2, columnspan=3, sticky='ew')
        self.ability_label.grid(column=0, row=3)
        self.ability_combobox.grid(column=1, row=3, columnspan=3, sticky='ew')
        self.membership_label.grid(column=0, row = 4)
        self.membership_cbox.grid(column=1, row = 4, columnspan=3, sticky='ew')
        self.owed_label.grid(column = 0, row = 5)
        self.owed_entry.grid(column = 1, row = 5)
        self.pay_owed_button.grid(column = 2, row = 5)
        self.partner_aff_label.grid(column=0, row=7)
        self.partner_aff_box.grid(column=1, row=7, columnspan=2, sticky='ew')
        self.partner_aff_level_box.grid(column=3, row=7, sticky='ew')
        self.new_partner_aff.grid(column=1, row=8, sticky='ew')
        self.save_par_aff_butn.grid(column=2, row=8, sticky='ew')
        self.del_partner_aff.grid(column=3, row=8, sticky='ew')
        self.opp_aff_label.grid(column=0, row=9)
        self.opp_aff_box.grid(column=1, row=9, columnspan=2, sticky='ew')
        self.opp_aff_level_box.grid(column=3, row=9, sticky='ew')
        self.new_opp_aff.grid(column=1, row=10, sticky='ew')
        self.save_opp_aff_butn.grid(column=2, row=10, sticky='ew')
        self.del_opp_aff.grid(column=3, row=10,  sticky='ew')

        # Games played. Irrelevant for new players
        if not self.new:
            self.games_played_label.grid(column=0, row=11)
            self.games_played_number.grid(column=2, row=11)
            self.late_penalty_label.grid(column=0, row=12)
            self.late_penalty_entry.grid(column=2, row=12)
            self.games_total_label.grid(column=0, row=13)
            self.games_total_number.grid(column=2, row=13)

        self.player_notes_label.grid(column=1, row=14, columnspan=2)
        self.player_notes.grid(column=0, row=15, columnspan=6,
                               padx=5, pady=5, sticky='nsew')

        self.save_player_button.grid(column=1, row=16, columnspan=3)

    def switch_aff(self, side):
        '''Bind the aff level combo to the aff name combo'''
        aff_dict = {'Low': 0, 'Medium': 1, 'High': 2, 'Maximum': 3}
        if side == "partner":
            for plyr in self.player.partner_affinities:
                # if name, set the level to the corresponding level
                if plyr[0] == self.partner_aff_box.get():
                    self.partner_aff_level_box.current(aff_dict[plyr[1]])
                    break # saving a search of the whole list, pointless?

        elif side == "opponent":
            for plyr in self.player.opponent_affinities:
                if plyr[0] == self.opp_aff_box.get():
                    self.opp_aff_level_box.current(aff_dict[plyr[1]])
                    break

    def pay_off(self):
        """only clears entry widget"""
        self.owed_entry.delete(0, "end")
        self.owed_entry.insert(0, 0)


    # Could combine the two into one method, but it doesn't save space?
    def new_partner_affinity(self):
        """Simply clears the combobox"""
        self.partner_aff_box.delete(0, "end")

    def new_opp_affinity(self):
        """Simply clears the combobox"""
        self.opp_aff_box.delete(0, "end")

    def save_affinity(self, side):

        # Need to organise this better?

        all_names = [player.name for player in b_scorer.every_player]
        if side == "partner":
            other_player = self.partner_aff_box.get()
        elif side == "opponent":
            other_player = self.opp_aff_box.get()

        # Can't save your own name as affinity. Seems inconcise
        if self.new:
            if other_player == self.name_entry.get():
                not_found = tk.messagebox.showerror("Error", "A player can't have"
                                                             " an affinity with "
                                                             "him/herself!",
                                                    parent=self)
                return False

        else:
            if other_player == self.player.name:
                not_found = tk.messagebox.showerror("Error", "A player can't have"
                                                             " an affinity with "
                                                             "him/herself!",
                                                    parent=self)
                return False

        # Can't save non-existing player
        if other_player not in all_names:
            not_found = tk.messagebox.showerror("Error", "Player name not "
                                                         "found", parent = self)
            return False


        # Add affinity to the current player
        if side == "partner":

            level = self.partner_aff_level_box.get()

            self.partner_affs.append((other_player, level))
            self.partner_aff_box.config(values=[p[0] for p in
                                                self.partner_affs])
            # If not new, add affinities right now
            if not self.new:
                for player in b_scorer.every_player:
                    if player.name == other_player:
                        player.add_affinity("partner", self.player.name, level)
                self.player.add_affinity("partner", other_player, level)

        elif side == "opponent":

            level = self.opp_aff_level_box.get()

            self.opp_affs.append((other_player, level))
            self.opp_aff_box.config(values=[p[0] for p in
                                                self.opp_affs])

            if not self.new:
                for player in b_scorer.every_player:
                    if player.name == other_player:
                        player.add_affinity("opponent", self.player.name, level)
                self.player.add_affinity("opponent", other_player, level)

        player_saved = tk.messagebox.showinfo("Success",
                                              "Player's affinity added!",
                                              parent = self)

    # Currently - doesn't work for new players, doesn't raise NameErrors for
    # missing players. But those seem unlikely to be of much relevance atm
    def del_affinity(self, side):

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to "
                                              "delete this affinity?",
                                              parent = self)
        if are_you_sure:

            if side == "partner":
                other_player = self.partner_aff_box.get()

            elif side == "opponent":
                other_player = self.opp_aff_box.get()

            # try:
            #     self.partner_affs.remove(other_player)
            # except ValueError:
            #     tk.messagebox.showerror("Error", "Error: Name not found")
            #     return

            if not self.new:
                try:
                    self.player.remove_affinity(other_player, side)
                except NameError:
                    tk.messagebox.showerror("Error", "Error: Name not found")
                    return

                if side == "partner":
                    self.partner_affs = self.player.partner_affinities
                    self.partner_aff_box.config(values=[p[0] for p in
                                                        self.partner_affs])
                    self.partner_aff_box.delete(0, "end")
                elif side == "opponent":
                    self.opp_affs = self.player.opponent_affinities
                    self.opp_aff_box.config(values=[p[0] for p in
                                                    self.opp_affs])
                    self.opp_aff_box.delete(0, "end")

                for other in b_scorer.every_player:
                    if other.name == other_player:
                        try:
                            other.remove_affinity(self.player.name, side)
                        # In case it's new, or not there for some reason
                        except NameError:
                            print("Name problem removing affinity!")
            else:
                #  How many times do you need to delete an affinity from a
                # new player?
                print("I can't be bothered working this out")

    def save_player(self):
        """If the player is existing, then update their stats. If new,
        create a new player and add them to bench"""

        name = self.name_entry.get()
        # Check if name is already taken, unless it's already this name
        if not self.new and self.player.name == name:
            pass
        elif name in [player.name for player in b_scorer.every_player]:
            error = tk.messagebox.showerror("Error",
                                            "Error: player with identical"
                                            " name found."
                                            " Please enter a new name.",
                                            parent=self)
            return

        # money currently must be an integer
        try:
            owed = int(self.owed_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Error: Money owed must be an "
                                             "integer.", parent=self)
            return

        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to save"
                                              " this player?",  parent = self)
        if are_you_sure is False:
            return

        sex = self.sex_combobox.get()
        ability = int(self.ability_combobox.get())
        membership =  self.membership_cbox.get()
        notes = self.player_notes.get("1.0", "end-1c")

        #If the player is New:
        #Create the player, add them to "every player" and "absent players"
        #Then call the add_player function from b_scorer to add them
        #to the bench with their respective games etc
        if self.new:

            New_Player = b_scorer.Player(name, sex, ability)
            New_Player.player_notes = notes
            New_Player.partner_affinities = self.partner_affs
            New_Player.opponent_affinities = self.opp_affs
            New_Player.membership = membership
            b_scorer.every_player.append(New_Player)
            b_scorer.absent_players.append(New_Player)
            b_scorer.add_player(New_Player)
            New_Player.money_owed = owed
            self.controller.colour_dict = b_scorer.colour_sorter(
                b_scorer.all_current_players)
            self.controller.add_bench_menus(New_Player)
            self.controller.bench_grid()

            # Add affinities to other players

            for player in b_scorer.every_player:
                for aff in self.partner_affs:
                    if aff[0] == player.name:
                        player.add_affinity("partner", name, aff[1])
                for aff in self.opp_affs:
                    if aff[0] == player.name:
                        player.add_affinity("opponent", name, aff[1])

                    # print(player.opponent_affinities)
        else:
            # if player is existing, update their stats
            try:
                late_penalty = float(self.late_penalty_entry.get())
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a valid "
                                                 "lateness penalty",
                                                  parent = self)
                return

            # if the player's name is changed, update all the affinities

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
            self.player.membership = membership

            # Not ideal place for this
            if owed != self.player.money_owed:

                if self.player.name not in b_scorer.today_session.payments:
                    b_scorer.today_session.payments[self.player.name] = (
                        self.player.membership, self.player.money_owed - owed)
                else: # if already paid. ugly
                    b_scorer.today_session.payments[self.player.name] = \
                        (self.player.membership,
                         b_scorer.today_session.payments[self.player.name][1] +
                         (self.player.money_owed - owed))

            self.player.money_owed = owed


            self.player.penalty_games = late_penalty
            self.player.adjusted_games = self.player.total_games + late_penalty

        # save stuff
        every_pi = open('every_player_pi_2.obj', 'wb')
        pickle.dump(b_scorer.every_player, every_pi)
        every_pi.close()

        self.controller.update_board()

        self.destroy()


class GameStats(tk.Toplevel):
    """A Toplevel popup which allows the user to modify the weightings given to
    the various factors of the sorting algorithm"""
    def __init__(self, controller):

        tk.Toplevel.__init__(self, controller)

        self.controller = controller
        self.title("Weightings for Game Scoring Algorithm")

        self.profile_label = ttk.Label(self, text="Profile:")
        self.bal_label = ttk.Label(self, text="Game Balance Weighting")
        self.seg_label = ttk.Label(self, text="Ability Segregation Weighting")
        self.mix_label = ttk.Label(self, text="Player Mixing Weighting")
        self.aff_label = ttk.Label(self, text="Player Affinity Weighting")
        self.female_aff_label = ttk.Label(self, text="Female Affinity "
                                                     "Weighting")
        self.shuffle_label = ttk.Label(self, text="Shuffle Algorithm")

        self.profile_combo = ttk.Combobox(self, width = 10, state = 'readonly',
                                          values=["Default", "Tuesday",
                                             "Thursday"])
        self.bal_entry = ttk.Entry(self, width=4)
        self.seg_entry = ttk.Entry(self, width=4)
        self.mix_entry = ttk.Entry(self, width=4)
        self.aff_entry = ttk.Entry(self, width=4)
        self.female_aff_entry = ttk.Entry(self, width=4)
        self.shuffle_combo = ttk.Combobox(self, width=10, state = 'readonly',
                                          values=["Random", "Segregated"])


        # self.bal_entry.insert(0, b_scorer.enumerate_b.scoring_vars['Balance'])
        # self.seg_entry.insert(0, b_scorer.enumerate_b.scoring_vars['Ability_Seg'])
        # self.mix_entry.insert(0, b_scorer.enumerate_b.scoring_vars['Mixing'])
        # self.aff_entry.insert(0, b_scorer.enumerate_b.scoring_vars['Affinity'])
        # self.shuffle_combo.current(b_scorer.enumerate_b.scoring_vars['Shuffle'])

        # not used ATM
        # self.default_button = ttk.Button(self, text="Return to Default",
        #                                  command=self.return_default_weightings)
        self.save_button = ttk.Button(self, text="Save Weightings",
                                      command=self.save_weightings)

        self.profile_combo.bind("<<ComboboxSelected>>",
                                lambda event: self.switch_profile())

        self.profile_label.grid(column=0, row=0)
        self.profile_combo.grid(column=1, row=0)
        self.bal_label.grid(column=0, row=1)
        self.bal_entry.grid(column=1, row=1)
        self.seg_label.grid(column=0, row=2)
        self.seg_entry.grid(column=1, row=2)
        self.mix_label.grid(column=0, row=3)
        self.mix_entry.grid(column=1, row=3)
        self.aff_label.grid(column=0, row=4)
        self.aff_entry.grid(column=1, row=4)
        self.female_aff_label.grid(column=0, row=5)
        self.female_aff_entry.grid(column=1, row=5)
        self.shuffle_label.grid(column=0, row=6)
        self.shuffle_combo.grid(column=1, row=6)
        # self.default_button.grid(column=0, row=6)
        self.save_button.grid(column=1, row=7)

        # Set profile based on day
        today = datetime.today().weekday()
        if today == 1:
            self.profile_combo.current(1)
        elif today == 3:
            self.profile_combo.current(2)
        else:
            self.profile_combo.current(0)
        self.switch_profile()

    def save_weightings(self):
        # Check to see if you want to update
        are_you_sure = tk.messagebox.askyesno("Are you sure?",
                                              "Are you sure you want to update these weightings? "
                                              "They will affect the way every game is generated from now on.")
        if are_you_sure is True:

            # Ensure all entries are floats, then update the new weightings
            # Double imported naming seems wonky
            try:
                day = self.profile_combo.get()
                b_scorer.enumerate_b.scoring_vars['Balance', day] = float(
                    self.bal_entry.get())
                b_scorer.enumerate_b.scoring_vars['Ability_Seg', day] = float(
                    self.seg_entry.get())
                b_scorer.enumerate_b.scoring_vars['Mixing', day] = float(
                    self.mix_entry.get())
                b_scorer.enumerate_b.scoring_vars['Affinity', day] = float(
                    self.aff_entry.get())
                b_scorer.enumerate_b.scoring_vars['Female Affinity', day] = \
                    float(
                    self.female_aff_entry.get())
                b_scorer.enumerate_b.scoring_vars[
                    'Shuffle', day] = self.shuffle_combo.current()

                # MMmmmm score pie
                score_pi = open('score_pi.obj', 'wb')
                pickle.dump(b_scorer.enumerate_b.scoring_vars, score_pi)
                score_pi.close()

                self.destroy()

            except ValueError:
                error = tk.messagebox.showerror("Error",
                                                "Please ensure all values are"
                                                " numbers only.")

    # OUT OF DATE ATM
    # def return_default_weightings(self):
    #     """Replace the user-defined weightings with default ones"""
    #
    #
    #     are_you_sure = tk.messagebox.askyesno("Are you sure?",
    #                                           "Are you sure you want to return "
    #                                           "to the default weightings?")
    #
    #     if are_you_sure is True:
    #         b_scorer.enumerate_b.scoring_vars['Balance'] = 5.0
    #         b_scorer.enumerate_b.scoring_vars['Ability_Seg'] = 2.0
    #         b_scorer.enumerate_b.scoring_vars['Mixing'] = 1.5
    #         b_scorer.enumerate_b.scoring_vars['Affinity'] = 4.0
    #
    #         # should be able to loop?
    #         self.bal_entry.delete(0, "end")
    #         self.seg_entry.delete(0, "end")
    #         self.mix_entry.delete(0, "end")
    #         self.aff_entry.delete(0, "end")
    #
    #         self.bal_entry.insert(0,
    #                               b_scorer.enumerate_b.scoring_vars['Balance'])
    #         self.seg_entry.insert(0, b_scorer.enumerate_b.scoring_vars[
    #             'Ability_Seg'])
    #         self.mix_entry.insert(0,
    #                               b_scorer.enumerate_b.scoring_vars['Mixing'])
    #         self.aff_entry.insert(0,
    #                               b_scorer.enumerate_b.scoring_vars['Affinity'])

    def switch_profile(self):
        """When profile_combo selects a new profile, switch to those"""
        # Delete balance entries, and insert the new profile's numbers.
        # print("Selected!")
        profile = self.profile_combo.get() # could pass in?

        self.bal_entry.delete(0, "end")
        self.seg_entry.delete(0, "end")
        self.mix_entry.delete(0, "end")
        self.aff_entry.delete(0, "end")
        self.female_aff_entry.delete(0, "end")

        self.bal_entry.insert(0,
                              b_scorer.enumerate_b.scoring_vars[('Balance',
                                                                profile)])
        self.seg_entry.insert(0, b_scorer.enumerate_b.scoring_vars[
            ('Ability_Seg', profile)])
        self.mix_entry.insert(0,
                              b_scorer.enumerate_b.scoring_vars[('Mixing',
                                                                 profile) ])
        self.aff_entry.insert(0,
                              b_scorer.enumerate_b.scoring_vars[('Affinity',
                                                                 profile)])
        self.female_aff_entry.insert(0,
                              b_scorer.enumerate_b.scoring_vars[(
                                  'Female Affinity',
                                                                 profile)])
        self.shuffle_combo.current(b_scorer.enumerate_b.scoring_vars[(
            'Shuffle', profile)])

class HistoryPopup(tk.Toplevel):
    def __init__(self, controller):

        tk.Toplevel.__init__(self, controller)

        self.controller = controller

        self.sessions = []
        #self.combined_sessions = b_scorer.all_sessions
            #Get only sessions that have at least 2 games. Maybe in method?
        for i, session in enumerate(b_scorer.all_sessions):
            if len(session.games) > 0:
                self.sessions.append(session)

        self.title("Game History")

        self.current_history = ttk.Button(self, text="Print Current Session"
                                                     " History", command=
                                          self.print_current)

        self.print_history_button = ttk.Button(self, text = "Print All "
                                                            "Sessions",
                                               command = self.print_sessions)
        self.session_combo = ttk.Combobox(self, width=20, values = [])
        self.get_sessions()
        self.session_combo.current(0)

        self.print_sess_button = ttk.Button(self, text = "Print Games From "
                                                         "Selected Date",
                                            command = self.print_selected)

        self.print_times_button = ttk.Button(self, text = "Print Times",
                                            command = self.print_times)

        self.print_summary_button = ttk.Button(self, text = "Print Overall "
                                                            "Summary",
                                            command = self.print_overall)

        self.export_game_CSV = ttk.Button(self, text = "Export Game History to CSV",
                                          command=lambda: self.export_to_csv(
                                              "games"))

        self.export_player_CSV = ttk.Button(self, text = "Export Player History to CSV",
                                            command=lambda: self.export_to_csv(
                                                "players"))

        self.every_player_combo = ttk.Combobox(self, width = 20, values =
            sorted([p.name for p in b_scorer.every_player]), state =
        'readonly')

        self.every_player_combo.current(0)

        self.player_stats_button = ttk.Button(self, text="View Player "
                                                         "History", command
                                              =self.view_player_history)

        # self.print_payments_button = ttk.Button(self, text = "Print "
        #                                                      "Payments",
        #                                         command = self.print_payments)


        self.current_history.grid(column=0, row=0)
        self.print_summary_button.grid(column=0, row=1)
        self.print_history_button.grid(column=0, row=2)
        
        self.session_combo.grid(column=0, row=4)
        self.print_sess_button.grid(column=0, row=5)
        self.print_times_button.grid(column=0, row=10)

        self.every_player_combo.grid(column=0, row=6)
        self.player_stats_button.grid(column=0, row=7)
        self.export_game_CSV.grid(column = 0, row = 8)
        self.export_player_CSV.grid(column = 0, row = 9 )

    def export_to_csv(self, type):

        # first, entry popup to name the .csv. Require input validation.
        # then (ideally in b_sessions module), call export function
        # then tk messagebox "Success" if created
        self.export_popup = CSVPopup(self, type)

    def print_sessions(self):
        for i, session in enumerate(b_scorer.all_sessions):
            if len(session.games) > 2:
                print("\nSession", i+1)
                print("Date:", session.date)
                print("Start:", session.start_time)
                print("End Time:", session.end_time)
                print("")

                for i, game in enumerate(session.games):                
                    print("***Game {}*** \n".format(i+1))
                    for i, court in enumerate(game):
                        print("*Court {}* \n".format(i+1))
                        print("{} and {} [VERSUS]".format(court[0].name,
                                                         court[1].name))
                        print("{} and {}".format(court[2].name,
                                                         court[3].name))
                        print("")
                    print("--------------------")

    def print_current(self):

        session = b_scorer.today_session


        print("Date:", session.date)
        print("Start:", session.start_time)

        for i, game in enumerate(session.games):
            print("***Game {}*** \n".format(i+1))
            for i, court in enumerate(game):
                print("*Court {}* \n".format(i+1))
                print("{} and {} [VERSUS]".format(court[0].name,
                                                 court[1].name))
                print("{} and {}".format(court[2].name,
                                                 court[3].name))
                print("")
            print("--------------------")



    def get_sessions(self):
        """Gets session names for the name combobox"""
        self.names = []
        count = 0 # for extra days

        self.session_dict = {} # keying combo to sessions

        for i, session in enumerate(b_scorer.all_sessions):
            if len(session.games) > 1: # so non-sessions are ignored

                day = datetime.strftime(session.date, '%a, %b %d, %Y')
                if day in self.names: # multiple sessions in one day
                    count += 1
                    day = (('{} ({})'.format(day, count + 1)))
                else:
                    count = 0

                self.session_dict[day] = session
                self.names.insert(0, day) # so list is in descending order


        self.session_combo.config(values = self.names)

    def print_selected(self):
        session_title = self.session_combo.get()
        session = self.session_dict[session_title]
        print("\n Games for {} \n".format(session_title))

        for i, game in enumerate(session.games):
            print("***Game {}*** \n".format(i + 1))
            for i, court in enumerate(game):
                print("*Court {}* \n".format(i + 1))
                print("{} and {} [VERSUS]".format(court[0].name,
                                                  court[1].name))
                print("{} and {}".format(court[2].name,
                                         court[3].name))
                print("")
            print("--------------------")

    def print_times(self):
        session_title = self.session_combo.get()
        session = self.session_dict[session_title]
        print("***Arrivals and Departures for {}*** \n".format(session_title))

        arrivals = sorted(session.player_arrivals, key =
                            session.player_arrivals.get)
        departures = sorted(session.player_departures, key =
                            session.player_departures.get)
        print("*Arrivals*: \n")
        for player in arrivals:
            print(player.name, session.player_arrivals[player])#"{}: {

            try:
                pay_value = session.payments[player.name]
                print("Paid {} as a {}".format(pay_value[1], pay_value[0]))
            except (AttributeError, KeyError):
                pass

            # }".format(player.key,
            # player.value))
        print("*Departures*: \n")
        for player in departures:
            print(player.name, session.player_departures[player])


    def print_overall(self):
        "print summary of results"
        sessions = []

        for i, session in enumerate(b_scorer.all_sessions):
            if len(session.games) > 1:
                sessions.append(session)

        print("***Summary of Sessions*** \n")
        print("Total Sessions: {}".format(len(sessions)))
        print("First Recorded Session: {}".format(self.names[-1]))
        print("Last Recorded Session: {}".format(self.names[0]))

        arrivals = []
        for session in sessions:
            arrivals.append(len(session.player_arrivals))

        print("Maximum Recorded Players: {}".format(max(arrivals)))
        print("Minimum Recorded Players: {}".format(min(arrivals)))
        mean = (sum(arrivals) / len(arrivals))
        print("Mean Recorded Players: {}".format(round(mean,2)))

    def view_player_history(self):

        p_name = self.every_player_combo.get()

        # should be less nested way?
        for player in b_scorer.every_player:
            if player.name == p_name:
                print("")
                print(player.name)
                print("Ability: {}".format(player.ability))
                print("Membership: {}".format(player.membership))
                print("Partner Affinities:")
                for p in player.partner_affinities:
                    print("", p)
                print("Opponent Affinities:")
                for p in player.opponent_affinities:
                    print("", p)

                count = 0
                for session in self.sessions:

                    peeps = [p for p in session.player_arrivals]
                    players_in_session = [p.name for p in
                                          session.player_arrivals]
                    if player.name in players_in_session:
                        count += 1
                print("Turned up {} out of {} nights".format(count,
                                                            len(self.sessions)))
                
                # Let's find all the games they've played in
                #print(self.sessions[0].games)
                played_with = []
                for session in self.sessions:
                    for round in session.games:
                        for court in round:
                            if player.name in [p.name for p in court if p is
                                                             not None]:
                                for p in court:
                                    played_with.append(p.name)
                #print(played_with)
                #sorted(played_with, key = )
    #def print_payments(self):


class CSVPopup(tk.Toplevel):
    def __init__(self, controller, type):
        tk.Toplevel.__init__(self, controller)

        self.controller = controller
        self.type = type
        self.title("Save CSV")

        self.entry = ttk.Entry(self, width = 20)
        self.csv_label = ttk.Label(self, text = ".csv")
        self.save_button = ttk.Button(self, text = "Save to File", command =
                                      self.save_file)

        self.entry.grid(column = 0, row = 0)
        self.csv_label.grid(column = 1, row = 0)
        self.save_button.grid(column = 0, row = 1,  sticky = 'nsew')

    def save_file(self):
        if self.type == 'games':
            b_sessions.export_game_data(self.entry.get())
        elif self.type == 'players':
            b_sessions.export_player_data(self.entry.get())
        tk.messagebox.showinfo("Success", "Successfully exported!")
        self.destroy()



class HelpMenu(tk.Toplevel):
    def __init__(self, controller):

        tk.Toplevel.__init__(self, controller)

        self.controller = controller
        self.title("User Guide")

        readme = open('user_guide.txt', 'r')
        readme_contents = readme.read()
        readme.close()

        self.text_widget = tk.Text(self, height=40, width=80, wrap=tk.WORD)
        self.text_widget.insert(1.0, readme_contents)

        self.scrollbar = Scrollbar(self)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.text_widget.grid(column = 0, row = 0, sticky = "NSEW")
        self.scrollbar.grid(column=1, row=0, sticky="NSW")




if __name__ == '__main__':
    bg_colour = "light blue"

    app = Application()
    app.configure(background=bg_colour)
    app.mainloop()
