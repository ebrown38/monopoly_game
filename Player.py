import random
import json
from properties import Properties


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
        self.iswinner = False
        self.game_properties = dict(Properties().properties)

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
                                self.main.banker.buy_house(property, self, prop)
                            if property['houses'] == 4 and property['hotels'] == 0 and self.money >= (property['hotel_props']['cost']) * values['owned'] * 1.5 and self.main.banker.hotels > 0:
                                self.main.banker.buy_hotel(property, self, prop)

        if len(self.properties) > 0:
            for name, values in self.properties.items():
                if values['ismortgaged'] and self.money >= values['price']:
                    # Unmortgage any mortgaged properties
                    self.main.banker.unmortgage_property(values, self, name)

        roll = 0
        # Checks if In Jail. If is, tries to get out
        if self.jail:
            # Checks if Player has get out of jail free card
            if self.get_out_jail > 0:
                self.get_out_jail -= 1
                self.jail = False
            else:
                # If player does not have get out of jail free, attempt to roll a double
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
        for name, values in self.game_properties.items():
            if values['Space'] == self.spot:
                self.main.game.count_landed_on(name)

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
                    self.pay_rent(values, player, name, multiplier)
                    return

    def trade(self, color):
        other_players = list(self.main.players)
        other_players.remove(self)

        self_owned_colors = dict(self.owned_colors)

        for player in other_players:
            if True:
                player_owned_colors = dict(player.owned_colors)
                for color2, values in player_owned_colors.items():
                    if color2 == color and self.main.color_assigned[color] == self.name:
                        for color3 in player_owned_colors:
                            for color4, values2 in self_owned_colors.items():
                                if color3 == color4 and color3 != color and self.main.color_assigned[color4] == player.name:
                                        if values['name'][0] and values2['name'][0]:
                                            player_prop = dict({values['name'][0]: player.properties[values['name'][0]]})
                                            self_prop = dict({values2['name'][0]: self.properties[values2['name'][0]]})
                                        if not player_prop[values['name'][0]]['ismortgaged'] and not self_prop[values2['name'][0]]['ismortgaged']:
                                            player_property_name = values['name'][0]
                                            self_property_name = values2['name'][0]
                                            is_a_monopoly = self.is_monopoly(player, player_prop[player_property_name]['Color'], self_prop[self_property_name]['price'])
                                            player_extra = 0
                                            self_extra = 0
                                            if is_a_monopoly == 'Player':
                                                player_extra = self_prop[self_property_name]['price']
                                            elif is_a_monopoly == 'Self':
                                                self_extra = player_prop[player_property_name]['price']
                                            if player_prop[player_property_name]['price'] == self_prop[self_property_name]['price']:
                                                if (player_extra > 0 or self_extra > 0) and player.money > player_extra and self.money > self_extra:
                                                    if player_extra > 0:
                                                        player.money -= player_extra
                                                        self.money += player_extra
                                                    elif self.money > 0:
                                                        player.money += player_extra
                                                        self.money -= player_extra
                                                    self.trading(player_property_name, self_property_name, player, player_prop, self_prop)
                                                elif player_extra == 0 and self_extra == 0:
                                                    self.trading(player_property_name, self_property_name, player, player_prop, self_prop)
                                            elif player_prop[player_property_name]['price'] > self_prop[self_property_name]['price']:
                                                difference = abs(player_prop[player_property_name]['price'] - self_prop[self_property_name]['price'])
                                                if self.money > (player_prop[player_property_name]['price'] + self_extra):
                                                    player.money += int(difference + self_extra)
                                                    self.money -= int(difference + self_extra)
                                                    self.trading(player_property_name, self_property_name, player, player_prop,self_prop)
                                            elif player_prop[player_property_name]['price'] < self_prop[self_property_name]['price']:
                                                difference = abs(self_prop[self_property_name]['price'] - player_prop[player_property_name]['price'])
                                                if player.money > (self_prop[self_property_name]['price'] + player_extra):
                                                    player.money -= int(difference + player_extra)
                                                    self.money += int(difference + player_extra)
                                                    self.trading(player_property_name, self_property_name, player, player_prop, self_prop)
                                            return

    def trading(self, player_card,self_card,player, player_prop,self_prop):
        player.properties.update(self_prop)
        self.properties.update(player_prop)

        del player.properties[player_card]
        del self.properties[self_card]

        player_owned_color = {}
        for name1, value1 in player.properties.items():
            if value1['Color'] not in player_owned_color:
                player_owned_color[value1['Color']] = {'owned': 1, 'possible': value1['total'],'name': [name1]}
            else:
                player.owned_colors[value1['Color']]['owned'] += 1
                player.owned_colors[value1['Color']]['name'].append(name1)

        player.owned_colors = player_owned_color

        self_owned_color = {}
        for name2, value2 in self.properties.items():
            if value2['Color'] not in self_owned_color:
                self_owned_color[value2['Color']] = {'owned': 1, 'possible': value2['total'], 'name': [name2]}
            else:
                self_owned_color[value2['Color']]['owned'] += 1
                self_owned_color[value2['Color']]['name'].append(name2)

        self.owned_colors = self_owned_color

        self.main.game.set_color_assigned(player)
        self.main.game.set_color_assigned(self)

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
            self.main.game.count_landed_on('Jail')

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

    def pay_rent(self, property, player, name, multiplier=1):
        rent = 0
        rent_multiplier = 1
        if player.owned_colors[property['Color']]['owned'] == player.owned_colors[property['Color']]['possible']:
            rent_multiplier = 2
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
            rent = property['rent'] * rent_multiplier

        self.main.game.rent_for_property(name, rent)

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
                    highest_bid = self.property_bid(players,values)
                    if highest_bid and highest_bid[1] > 0:
                        banker.buy_property(purchasing_property=name, player=highest_bid[0], price=highest_bid[1])
                return True
        return False

    def property_bid(self, players, values, multiplier=0.95, highest_bid=[]):
        try:
            new_players = list(players)
            saved_players=list(players)
            for player in new_players:
                if player.money > values['price']:
                    if not highest_bid:
                        highest_bid = [player, values['price']]
                    else:
                        if highest_bid[1] * 1.1 < player.money * .75:
                            highest_bid = [player, highest_bid[1] * 1.1]
                        else:
                            players.remove(player)
                else:
                    if not highest_bid:
                        if player.money > (values['price'] * multiplier):
                            highest_bid = [player, int(values['price'] * multiplier)]
                    else:
                        if highest_bid[1] * 1.1 < player.money:
                            highest_bid = [player, int(highest_bid[1] * 1.1)]
                        else:
                            players.remove(player)
            if (len(highest_bid) == 2 and highest_bid[1] <= 0) or multiplier <= 0:
                if multiplier <= 0:
                    highest_bid = [0,0]
                return highest_bid
            if not highest_bid or len(players) > 1:
                multiplier -= .05
                if not players:
                   players = saved_players
                return self.property_bid(players, values, multiplier, highest_bid)
            else:
                return highest_bid
        except RecursionError:
            highest_bid = [0, 0]
            return highest_bid

    # Check if player, self, or both will get a monopoly from trade. Increase cost of trade if only one will get a monopoly
    def is_monopoly(self, player, player_color, self_color):
        is_player_monopoly = False
        is_self_monopoly = False

        player_owned_colors = player.owned_colors
        self_owned_colors = self.owned_colors

        for color, value in player_owned_colors.items():
            if color == self_color and (self_color != 'RR' or self_color != 'Util'):
                if (value['owned'] + 1) == value['possible']:
                    is_player_monopoly = True

        for color, value in self_owned_colors.items():
            if color == player_color and (player_color != 'RR' or player_color != 'Util'):
                if (value['owned'] + 1) == value['possible']:
                    is_self_monopoly = True

        if is_player_monopoly and not is_self_monopoly:
            return 'Player'
        elif is_self_monopoly and not is_player_monopoly:
            return 'Self'

        return 'None'

    # Runs when a player has no more money
    def player_loss(self):
        properties = dict(self.properties)
        for name, values in properties.items():
            values['ismortgaged'] = False
            values['isbuyable'] = True
            if 'houses' in values and 'hotels' in values:
                values['houses'] = 0
                values['hotels'] = 0
            self.main.banker.properties[name] = values
            del self.properties[name]
        self.alive = False
        if self in self.main.players:
            self.main.players.remove(self)





