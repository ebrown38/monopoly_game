# This is the file that will run the monopoly game
from Banker import Banker
from Player import Player
from Game import Game
from Stats import Stats
from properties import Properties


class Main():

    players = []

    def __init__(self):
        self.score = 0
        self.banker = Banker(main=self)
        self.game = Game(banker=self.banker, main=self)
        self.run_game = True
        self.count = 0
        self.color_assigned = {}
        self.stats = Stats()
        self.property_stats = {}
        self.property_list = Properties().properties
        self.player_count = 0

    def initiate_game(self):

        player_count = (2,3,4,5,6)

        for players in player_count:
            if True:
                count = 1
                while count <= players:
                    player = Player(main=self, name='Player ' + str(count))
                    self.players.append(player)
                    count += 1

                self.player_count = len(self.players)
                self.run_game = True
                self.play_game()

    def play_game(self):
        round = 0
        while len(self.players) > 1:
            if round == 100:
                break
            self.round()
            round += 1
        else:
            if round < 100:
                if len(self.players) > 1:
                    winner = []
                    for player in self.players:
                        total = player.money
                        for name, values in player.properties.items():
                            if not values['ismortgaged']:
                                if 'houses' in values and 'hotels' in values:
                                    total += values['houses'] * values['houses_props']['cost']
                                    total += values['hotels'] * values['hotel_props']['cost']
                                total += values['price']

                        if not winner:
                            winner = [[player, total]]
                        else:
                            if winner[0][1] < total:
                                winner = [[player, total]]

                    winning_player = winner[0][0]

                else:
                    winning_player = self.players[0]

                winning_player.iswinner = True

                self.stats.set_game_stats(self.property_stats, round, self.player_count)

        self.reset_game()

    def round(self):
        for player in self.players:
            player.player_turn()

    def reset_game(self):
        self.players = []
        self.banker = Banker(main=self)
        self.game = Game(banker=self.banker, main=self)
        self.color_assigned = {}
        self.property_stats = {}


count = 0
main = Main()
games = 1000000
while count < games:
    if count % 1000 == 0:
        print('Game', count)
    main.initiate_game()
    count += 1
else:
    print('Final Stats', main.stats.get_final_stats(games))
