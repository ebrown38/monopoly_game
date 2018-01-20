import random
import json


class Player(object):

    def __init__(self, main, name):
        self.name = name
        self.money = int(1500)
        self.properties = {}
        self.owned_colors = {}
        self.spot = 0
        self.move = 0
        self.main = main
        self.jail = False
        self.roll_double = 0
        self.roll_again = False
        self.get_out_jail = 0
        self.get_out_jail_attempt = 0
        self.alive = True

    # Method That Runs Everything
    def player_turn(self):

        if len(self.owned_colors) > 0:
            for color, values in self.owned_colors.items():
                # Trades properties with other players
                if (values['owned']/values['possible']) > .5 and (values['owned'] != values['possible']):
                    self.trade(color)
                    break
                if color != 'RR' and color != 'Util':
                    for prop in values['name']:
                        property = self.properties[prop]
                        if not property['ismortgaged'] and values['owned'] == values['possible']:
                            # Add houses or Hotels to properties
                            if self.money >= (property['houses_props']['cost']) * values['owned'] * 1.5 and self.main.banker.houses > 0 and property['houses'] < 4:
                                self.main.banker.buy_house(property, self)
                            if property['houses'] == 4 and property['hotels'] == 0 and self.money >= (property['hotel_props']['cost']) * values['owned'] * 1.5 and self.main.banker.hotels > 0:
                                self.main.banker.buy_hotel(property, self)

        if len(self.properties) > 0:
            for name, values in self.properties.items():
                if values['ismortgaged'] and self.money >= values['price']:
                    # Unmortgage any mortgaged properties
                    self.main.banker.unmortgage_property(values, self)

        roll = 0
        # Checks if In Jail. If is, tries to get out
        if self.jail:
            if self.get_out_jail > 0:
                self.get_out_jail -= 1
                self.jail = False
            else:
                roll = self.roll_dice()
                if self.jail:
                    self.get_out_jail_attempt += 1
                if self.get_out_jail_attempt == 3:
                    self.jail = False
                    self.sub_money(50)

        # Goes as long as player not in Jail
        if not self.jail:
            self.move_player(roll)
            while self.roll_again and not self.jail:
                self.roll_again = False
                self.move_player()

        self.roll_again = False
        self.roll_double = 0

    def land_on_property(self, multiplier=1):

        isspecial = self.main.game.find_property(spot=self.spot, player=self)

        if not isspecial:
            purchased = False
            for name, values in self.main.banker.properties.items():
                if values['Space'] == self.spot:
                    purchased = self.buy_property()
                    break

            if not purchased:
                self.land_on_rent(multiplier)

    def land_on_rent(self, multiplier):
        players = list(self.main.players)
        if self in players:
            players.remove(self)
        for player in players:
            for name, values in player.properties.items():
                if values['Space'] == self.spot and not values['ismortgaged']:
                    self.pay_rent(values, player, multiplier)
                    return

    def trade(self, color):
        other_players = list(self.main.players)
        other_players.remove(self)

        self_owned_colors = dict(self.owned_colors)

        for player in other_players:
            if True:
                player_owned_colors = dict(player.owned_colors)
                for color2, values in player_owned_colors.items():
                    if color2 == color:
                        for color3 in player_owned_colors:
                            for color4, values2 in self_owned_colors.items():
                                if color3 == color4 and color3 != color:
                                    if values['name'][0] and values2['name'][0]:
                                        player_prop = dict({values['name'][0]: player.properties[values['name'][0]]})
                                        self_prop = dict({values2['name'][0]: self.properties[values2['name'][0]]})
                                    if not player_prop[values['name'][0]]['ismortgaged'] and not self_prop[values2['name'][0]]['ismortgaged']:
                                        player_property_name = values['name'][0]
                                        self_property_name = values2['name'][0]
                                        if player_prop[player_property_name]['price'] == self_prop[self_property_name]['price']:
                                            self.trading(player_property_name, self_property_name, player, player_prop, self_prop)
                                        elif player_prop[player_property_name]['price'] > self_prop[self_property_name]['price']:
                                            difference = abs(player_prop[player_property_name]['price'] - self_prop[self_property_name]['price'])
                                            if self.money > 500:
                                                player.money += int(difference)
                                                self.money -= int(difference)
                                                self.trading(player_property_name, self_property_name, player, player_prop,self_prop)
                                        elif player_prop[player_property_name]['price'] < self_prop[self_property_name]['price']:
                                            difference = abs(self_prop[self_property_name]['price'] - player_prop[player_property_name]['price'])
                                            if player.money > 500:
                                                player.money -= int(difference)
                                                self.money += int(difference)
                                                self.trading(player_property_name, self_property_name, player, player_prop, self_prop)
                                        return

    def trading(self, player_card,self_card,player, player_prop,self_prop):
        player.properties.update(self_prop)
        self.properties.update(player_prop)

        player.owned_colors[self_prop[self_card]['Color']]['name'].append(self_card)
        player.owned_colors[self_prop[self_card]['Color']]['owned'] += 1

        player.owned_colors[player_prop[player_card]['Color']]['name'].remove(player_card)
        player.owned_colors[player_prop[player_card]['Color']]['owned'] -= 1
        if player.owned_colors[player_prop[player_card]['Color']]['owned'] == 0:
            del player.owned_colors[player_prop[player_card]['Color']]

        self.owned_colors[player_prop[player_card]['Color']]['name'].append(player_card)
        self.owned_colors[player_prop[player_card]['Color']]['owned'] += 1

        self.owned_colors[self_prop[self_card]['Color']]['name'].remove(self_card)
        self.owned_colors[self_prop[self_card]['Color']]['owned'] -= 1
        if self.owned_colors[self_prop[self_card]['Color']]['owned'] == 0:
            del self.owned_colors[self_prop[self_card]['Color']]

        del player.properties[player_card]
        del self.properties[self_card]

    def roll_dice(self):
        dice = [1,2,3,4,5,6]
        dice1 = random.choice(dice)
        dice2 = random.choice(dice)

        if dice1 == dice2:
            self.roll_double += 1
            self.roll_again = True
            self.jail = False

        if self.roll_double >= 3:
            self.spot = 10
            self.jail = True
            self.roll_again = False
            self.roll_double = 0

        return dice1 + dice2

    def move_player(self, roll=0):
        if self.alive:
            if roll == 0:
                roll = self.roll_dice()

            if self.spot + roll > 39:
                spot = 40 - self.spot
                self.spot = roll - spot
                self.money += 200
            else:
                self.spot = self.spot + roll
            if not self.jail:
                self.land_on_property()

    def pay_rent(self, property, player, multiplier=1):
        rent = 0

        if property['Color'] == 'RR':
            owned_rr = player.owned_colors['RR']['owned']
            if owned_rr == 1:
                rent = 25 * multiplier
            elif owned_rr == 2:
                rent = 50 * multiplier
            elif owned_rr == 3:
                rent = 100 * multiplier
            elif owned_rr == 4:
                rent = 200 * multiplier
        elif property['Color'] == 'Util':
            owned_util = player.owned_colors['Util']['owned']
            if multiplier == 10 or owned_util == 2:
                rent = self.roll_dice() * 10
            elif owned_util == 1:
                rent = self.roll_dice() * 4
        elif property['houses'] > 0 or property['hotels'] > 0:
            if property['houses'] > 0:
                rent = property['houses_props']['rent'][str(property['houses'])]
            elif property['hotels'] == 1:
                rent = property['hotel_props']['rent']
        else:
            rent = property['rent']

        player.money += self.sub_money(rent)

    def sub_money(self, money):
        total = money
        if self.money - money < 0:
            total = int(self.money)
            deficit = self.money - money
            total += self.main.banker.mortgage(abs(deficit), self)
            if total < money:
                self.player_loss()
                return total
            else:
                difference = abs(total - money)
                self.money = int(difference)
        else:
            self.money -= int(money)

        return total

    def buy_property(self):
        banker = self.main.banker
        for name, values in banker.properties.items():
            if values['Space'] == self.spot and values['isbuyable']:
                if values['price'] < self.money:
                    banker.buy_property(purchasing_property=name, player=self)
                else:
                    players = list(self.main.players)
                    players.remove(self)
                    highest_bid = []
                    for player in players:
                        if not highest_bid:
                            highest_bid = [player, player.money * .1]
                        else:
                            if player.money * .1 > highest_bid[1]:
                                highest_bid = [player, player.money * .1]
                return True
        return False

    def player_loss(self):
        for name, values in self.properties.items():
            values['ismortgaged'] = False
            values['isbuyable'] = True
            values['houses'] = 0
            values['hotels'] = 0
            self.main.banker.properties[name] = values
        self.alive = False
        self.main.players.remove(self)





