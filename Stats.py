from collections import Counter
import json
from properties import Properties

class Stats():

    def __init__(self):
        self.players_in_game = {}
        self.winning_players_properties = []
        self.total_rounds_played = {}
        self.total_property_stats = {}
        self.total_spots = {}
        self.properties_dict = Properties().properties

    # def set_players_in_game(self, players):
    #     for player in players:
    #         if not player.name in self.players_in_game:
    #             self.players_in_game[player.name] = {}
    #         if player.iswinner:
    #             if not 'Win' in self.players_in_game[player.name]:
    #                 self.players_in_game[player.name]['Win'] = 0
    #             self.players_in_game[player.name]['Win'] += 1
    #             for name in player.properties:
    #                 self.winning_players_properties.append(name)
    #                 if not 'Winning Properties' in self.players_in_game[player.name]:
    #                     self.players_in_game[player.name]['Winning Properties'] = []
    #                 self.players_in_game[player.name]['Winning Properties'].append(name)

    def set_game_stats(self, property_stats, rounds, player_count):
        player_count_name = str(player_count) + ' Players'
        if not str(player_count) + ' Players' in self.total_property_stats:
            self.total_property_stats[player_count_name] = {}
        for name, stats in property_stats.items():
            prop_color = self.get_color(name)
            if not prop_color in self.total_property_stats[player_count_name]:
                self.total_property_stats[player_count_name][prop_color] = {}
            if not name in self.total_property_stats[player_count_name][prop_color]:
                self.total_property_stats[player_count_name][prop_color][name] = {}
            if 'rent' in stats:
                if not 'Total Rent Paid' in self.total_property_stats[player_count_name][prop_color][name]:
                    self.total_property_stats[player_count_name][prop_color][name]['Total Rent Paid'] = 0
                    self.total_property_stats[player_count_name][prop_color]['Total Rent For Color'] = 0
                self.total_property_stats[player_count_name][prop_color][name]['Total Rent Paid'] += stats['rent']
                self.total_property_stats[player_count_name][prop_color]['Total Rent For Color'] += stats['rent']
                if not 'Total Cost of Property' in self.total_property_stats[player_count_name][prop_color][name]:
                    self.total_property_stats[player_count_name][prop_color][name]['Total Cost of Property'] = 0
                    self.total_property_stats[player_count_name][prop_color]['Total Cost for Property Color'] = 0
                self.total_property_stats[player_count_name][prop_color][name]['Total Cost of Property'] += stats['Cost']
                self.total_property_stats[player_count_name][prop_color]['Total Cost for Property Color'] += stats['Cost']
            if not 'Total Times Landed On 1' in self.total_property_stats[player_count_name][prop_color][name]:
                self.total_property_stats[player_count_name][prop_color][name]['Total Times Landed On 1'] = 0
                self.total_property_stats[player_count_name][prop_color]['Total Times Landed on for Property Color'] = 0
            self.total_property_stats[player_count_name][prop_color][name]['Total Times Landed On 1'] += stats['Land On Count']
            self.total_property_stats[player_count_name][prop_color]['Total Times Landed on for Property Color'] += stats['Land On Count']
            if not player_count_name in self.total_spots:
                self.total_spots[player_count_name] = 0
            self.total_spots[player_count_name] += stats['Land On Count']



    def get_final_stats(self, games):
        players = (2,3,4,5,6)
        final_stats = {}
        final_stats['Property Stats'] = {}
        for player_count, sts in self.total_property_stats.items():
            final_stats['Property Stats'][player_count] = {}
            for color, stats in sts.items():
                final_stats['Property Stats'][player_count][color] = {}
                for name, stats2 in stats.items():
                        if type(stats2) is dict:
                            final_stats['Property Stats'][player_count][color][name] = {}
                            final_stats['Property Stats'][player_count][color][name]['Total Times Landed On'] = int(stats2['Total Times Landed On 1'])
                            final_stats['Property Stats'][player_count][color]['Total Times Landed on for Property Color'] = int(stats['Total Times Landed on for Property Color'])

                            if 'Total Rent Paid' in stats2:

                                final_stats['Property Stats'][player_count][color][name]['Total Rent Paid'] = int(stats2['Total Rent Paid'])
                                final_stats['Property Stats'][player_count][color]['Total Rent Paid for Color'] = int(stats['Total Rent For Color'])

                            if 'Total Cost of Property' in stats2:

                                final_stats['Property Stats'][player_count][color][name]['Total Cost of Property'] = int(stats2['Total Cost of Property'])
                                final_stats['Property Stats'][player_count][color]['Total Cost for Property Color'] = int(stats['Total Cost for Property Color'])

                            if 'Total Cost of Property' in stats2 and 'Total Rent Paid' in stats2:

                                return_on_investment_prop = ((stats2['Total Rent Paid'] - stats2['Total Cost of Property']) / stats2['Total Cost of Property']) * 100
                                final_stats['Property Stats'][player_count][color][name]['Return on Investment (Percent)'] = round(return_on_investment_prop, 2)

                                return_on_investment_color = ((stats['Total Rent For Color'] - stats['Total Cost for Property Color']) / stats['Total Cost for Property Color']) * 100
                                final_stats['Property Stats'][player_count][color]['Return on Investment (Percent)'] = round(return_on_investment_color, 2)

                            percent = round(((stats2['Total Times Landed On 1'] / self.total_spots[player_count]) * 100), 2)
                            final_stats['Property Stats'][player_count][color][name]['Percent Landed on'] = percent
                        else:
                            final_stats['Property Stats'][player_count][color][name] = int(stats2)


        return json.dumps(final_stats)

    def get_color(self, property):
        for name, values in self.properties_dict.items():
            if name == property:
                return values['Color']
        return 'Misc'








