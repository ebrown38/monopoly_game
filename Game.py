import random


class Game(object):

    def __init__(self, banker):
        self.banker = banker
        self.community_chest_cards = list(range(0, 16))
        self.chance_cards = list(range(0, 16))

    def find_property(self, spot, player):

        for name, spots in self.banker.special.items():
            for spot1 in spots:
                if spot1 == spot:
                    if name == 'Go':
                        # player.money += 200
                        return True
                    elif name == 'Community Chest':
                        self.community_chest(player)
                        return True
                    elif name == 'Chance':
                        self.chance(player)
                        return True
                    elif name == 'Income Tax':
                        ten_percent = int(player.money*.1)
                        paid = player.sub_money(min(200, ten_percent))
                        return True
                    elif name == 'Luxury Tax':
                        player.sub_money(75)
                        return True
                    elif name == 'Go Jail':
                        player.spot = 10
                        player.jail = True
                        return True
                    else:
                        return True

        return False

    def community_chest(self, player):
        card = random.choice(self.community_chest_cards)
        if card == 0:
            player.spot = 0
            player.money += 200
        elif card == 1:
            player.money += 200
        elif card == 2:
            player.sub_money(50)
        elif card == 3:
            player.money += 50
        elif card == 4:
            player.get_out_jail += 1
        elif card == 5:
            player.spot = 10
            player.jail = True
        elif card == 6:
            players = list(player.main.players)
            players.remove(player)
            for other_player in players:
                pay = other_player.sub_money(50)
                player.money += pay
        elif card == 7:
            player.money += 100
        elif card == 8:
            player.money += 20
        elif card == 9:
            player.sub_money(100)
        elif card == 10:
            player.sub_money(150)
        elif card == 11:
            player.money += 25
        elif card == 12:
            for name, values in player.properties.items():
                if 'hotels' in values and 'houses' in values:
                    if values['hotels'] == 1:
                        player.sub_money(115)
                    elif values['houses'] > 0:
                        player.sub_money(40 * values['houses'])
        elif card == 13:
            player.money += 100
        elif card == 14:
            player.money += 10
        elif card == 15:
            player.money += 100

        index = self.community_chest_cards.index(card)
        del self.community_chest_cards[index]
        if len(self.community_chest_cards) == 0:
            self.community_chest_cards = list(range(0, 16))

    def chance(self, player):
        card = random.choice(self.chance_cards)
        if card == 0:  # Advance To Go
            player.spot = 0
            player.money += 200
        elif card == 1:  # Advance to Illinois Ave
            if player.spot > 24:
                player.money += 200
            player.spot = 24
            player.land_on_property()

        elif card == 2:  # Advance to St. Charles Place
            if player.spot > 11:
                player.money += 200
            player.spot = 11
            player.land_on_property()

        elif card == 3:  # Advance token to nearest railroad and pay owner twice as much
            if (0 <= player.spot <= 5) or (35 < player.spot <= 39):
                if 35 <= player.spot <= 39:
                    player.money += 200
                player.spot = 5
            elif 5 < player.spot <= 15:
                player.spot = 15
            elif 15 < player.spot <= 25:
                player.spot = 25
            elif 25 < player.spot <= 35:
                player.spot = 35
            player.land_on_property(multiplier=2)

        elif card == 4:  # Get out of Jail Free Card
            player.get_out_jail += 1

        elif card == 5:  # Go directly to jail
            player.spot = 10
            player.jail = True

        elif card == 6:  # Elected Chariman of the board, pay each player $50
            players = list(player.main.players)
            players.remove(player)
            for other_player in players:
                pay = player.sub_money(50)
                other_player.money += pay

        elif card == 7:  # Go back 3 spaces
            player.spot -= 3
            player.land_on_property()

        elif card == 8:  # Advance to nearest utility and pay 10 times dice roll
            if 12 < player.spot <= 28:
                player.spot = 28
                player.land_on_property(multiplier=10)
            elif (28 < player.spot <= 39) or (0 < player.spot <= 12):
                if 28 < player.spot <= 39:
                    player.money += 200
                player.spot = 12
                player.land_on_property(multiplier=10)

        elif card == 9:  # Pay poor tax of $15
            player.sub_money(15)

        elif card == 10:  # Advance to Reading Railroad, if pass go, Collect $200
            if 5 < player.spot <= 39:
                player.money += 200
            player.spot = 5
            player.land_on_property()

        elif card == 11:  # Advance to Boardwalk
            player.spot = 39
            player.land_on_property()

        elif card == 12:  # Make general repairs to all properties
            for name, values in player.properties.items():
                if 'hotels' in values and 'houses' in values:
                    if values['hotels'] == 1:
                        player.sub_money(100)
                    elif values['houses'] > 0:
                        player.sub_money(25 * values['houses'])

        elif card == 13:  # You have won a crossword competition, Collect $100
            player.money += 100

        elif card == 14:  # Your Building and loan matures, Collect $150
            player.money += 150

        elif card == 15:  # Bank Pays you Dividend of $50
            player.money += 50

        index = self.chance_cards.index(card)
        del self.chance_cards[index]
        if len(self.chance_cards) == 0:
            self.chance_cards = list(range(0, 16))