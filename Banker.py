from properties import Properties


class Banker():

    properties = {}
    special = {}

    def __init__(self, main):
        properties = Properties()
        self.houses = 32
        self.hotels = 12
        self.properties = dict(properties.properties)
        self.special = dict(properties.special)
        self.main = main

    def buy_property(self, purchasing_property, player, price=0):
        purchased = self.properties[purchasing_property]
        if price == 0:
            player.money -= purchased['price']
            self.main.game.cost_of_property(purchasing_property, purchased['price'])
        else:
            player.money -= price
            self.main.game.cost_of_property(purchasing_property, price)
        player.properties[purchasing_property] = purchased
        if purchased['Color'] in player.owned_colors:
            player.owned_colors[purchased['Color']]['owned'] += 1
            player.owned_colors[purchased['Color']]['name'].append(purchasing_property)
        else:
            player.owned_colors[purchased['Color']] = {'owned': 1, 'possible': purchased['total'], 'name': [purchasing_property]}

        self.main.game.set_color_assigned(player, purchased)
        del self.properties[purchasing_property]

    def buy_house(self, property, player, name):
            if 'houses' in property:
                if self.houses >= 1 and property['houses'] < 4:
                    property['houses'] += 1
                    self.houses -= 1
                    player.money -= property['houses_props']['cost']
                    self.main.game.cost_of_property(name, property['houses_props']['cost'])

    def buy_hotel(self, property, player, name):
        if 'hotels' in property and 'houses' in property:
            if self.hotels >= 1 and property['houses'] == 4:
                property['hotels'] += 1
                self.hotels -= 1
                player.money -= property['hotel_props']['cost']
                property['houses'] = 0
                self.main.game.cost_of_property(name, property['hotel_props']['cost'])

    def unmortgage_property(self, property, player, name):
        player.money -= (property['price'] * .5) * 1.1
        property['ismortgaged'] = False
        player.owned_colors[property['Color']]['owned'] += 1
        self.main.game.cost_of_property(name, (property['price'] * .5) * 1.1)

    def mortgage(self, deficit, player):
        total = 0
        for property, values in player.properties.items():

            if 'hotels' in values:
                if values['hotels'] == 1:
                    sell_hotel = values['hotel_props']['cost'] * .5
                    values['hotels'] = 0
                    self.hotels += 1
                    if self.houses < 4:
                        houses_difference = abs(4 - self.houses)
                        values['houses'] = self.houses
                        self.houses = 0
                        sell_hotel += values['houses_props']['cost'] * .5 * houses_difference
                    else:
                        values['houses'] = 4
                        self.houses -= 4
                    total += sell_hotel
                    self.main.game.cost_of_property(property, sell_hotel * -1)
                    if total > deficit:
                        return total
            if 'houses' in values:
                if values['houses'] >= 1:
                    while total < deficit and values['houses'] > 0:
                        sell_house = values['houses_props']['cost'] * .5
                        values['houses'] -= 1
                        self.houses += 1
                        total += sell_house
                        self.main.game.cost_of_property(property, sell_house * -1)
                        if total > deficit:
                            return total

        for property, values in player.properties.items():
            if not values['ismortgaged']:
                mortgage = values['price'] * .5
                values['ismortgaged'] = True
                total += mortgage
                self.main.game.cost_of_property(property, mortgage * -1)
                player.owned_colors[values['Color']]['owned'] -= 1
                if total > deficit:
                    return total

        return total
