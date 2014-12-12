import json
import pandas as pd
from bing_search_api import BingSearchAPI

my_key = "kCKs16wqbxThIJAfR7MIeSRez+zpuLLZm92ZP0nJKBw"

players = {}

df = pd.DataFrame.from_csv('../data/aggregate_data.csv')
players_list = pd.concat((df['QB'], df['RB']))

try:
    for player in players_list:
        bing = BingSearchAPI(my_key)
        params = {
            'ImageFilters': '"Face:Face"',
            '$format': 'json',
            '$top': 2,
            '$skip': 0,
        }
        r = bing.search('image', u'{} site:nfl.com'.format(player), params)
        data = r.json()

        players[player] = [data['d']['results'][0]['Image'][0]['MediaUrl'], data['d']['results'][0]['Image'][1]['MediaUrl']]
except:
    print u'An error occurred on {}'.format(player)
finally:
    with open('player_urls_nfl.json', 'w+') as outfile:
        json.dump(players, outfile)
