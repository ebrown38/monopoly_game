# This is the file that will run the monopoly game
import random
import json
from Banker import Banker
from Player import Player
from Game import Game


class Main():

    players = []

    def __init__(self):
        self.score = 0
        self.banker = Banker()
        self.game = Game(banker=self.banker)
        self.run_game = True
        self.count = 0

    def initiate_game(self):

        player_count = (2,3,4,5,6)

        players = 2

        count = 1
        while count <= players:
            player = Player(main=self, name='Player ' + str(count))
            self.players.append(player)
            count += 1

        self.run_game = True
        self.play_game()

    def play_game(self):

        play = True
        print('Players Start', self.players)
        for player in self.players:
            print(player.name)
        while len(self.players) > 1 and play:
            play = self.round()
        else:
            if play:
                print('Player Won!')
                print('Winning Player', self.players[0].name)

            self.reset_game()
        print('End Game')


    def round(self):

        for player in self.players:
            print('Player', player.name, 'Money before', player.money)
            # if player.money > 10000:
            #     return False
            player.player_turn()
            print('Player', player.name, 'Money after', player.money)

        return True

    def reset_game(self):
        self.players = []
        self.banker = Banker()
        self.game = Game(banker=self.banker)


count = 0
main = Main()
while count < 1:
    main.initiate_game()
    count += 1
