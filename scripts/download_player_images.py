import shutil
import requests
import json

with open('player_urls_nfl.json', 'r') as infile:
    players = json.load(infile)

for player in players:
    for i, url in enumerate(players[player]):
        response = requests.get(url, stream=True)
        ext = url.split('.')[-1]
        with open(u'../player_images_nfl/{}{}.{}'.format(player.lower().replace("'", '').replace(' ', '_'), 2 if i == 1 else '', ext), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

    print u'{} done.'.format(player)
    del response
