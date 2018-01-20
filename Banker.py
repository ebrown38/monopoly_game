from properties import Properties


class Banker():

    properties = {}
    special = {}

    def __init__(self):
        properties = Properties()
        self.houses = 32
        self.hotels = 12
        self.properties = dict(properties.properties)
        self.special = dict(properties.special)

    def buy_property(self, purchasing_property, player):
        purchased = self.properties[purchasing_property]
        player.money -= purchased['price']
        player.properties[purchasing_property] = purchased
        if purchased['Color'] in player.owned_colors:
            player.owned_colors[purchased['Color']]['owned'] += 1
            player.owned_colors[purchased['Color']]['name'].append(purchasing_property)
        else:
            player.owned_colors[purchased['Color']] = {'owned': 1, 'possible': purchased['total'], 'name': [purchasing_property]}
        del self.properties[purchasing_property]

    def buy_house(self, property, player):
            if self.houses >= 1 and property['houses'] < 4:
                property['houses'] += 1
                self.houses -= 1
                player.money -= property['houses_props']['cost']

    def buy_hotel(self, property, player):
            if self.hotels >= 1 and property['houses'] == 4:
                property['hotels'] += 1
                self.hotels -= 1
                player.money -= property['hotel_props']['cost']
                property['houses'] = 0

    def unmortgage_property(self, property, player):
        player.money -= (property['price'] * .5) * 1.1
        property['ismortgaged'] = False
        player.owned_colors[property['Color']]['owned'] += 1

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
                    if total > deficit:
                        return total
            if 'houses' in values:
                if values['houses'] >= 1:
                    while total < deficit and values['houses'] > 0:
                        sell_house = values['houses_props']['cost'] * .5
                        values['houses'] -= 1
                        self.houses += 1
                        total += sell_house
                        if total > deficit:
                            return total

        for property, values in player.properties.items():
            if not values['ismortgaged']:
                mortgage = values['price'] * .5
                values['ismortgaged'] = True
                total += mortgage
                player.owned_colors[values['Color']]['owned'] -= 1
                if total > deficit:
                    return total

        return total