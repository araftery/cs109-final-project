import csv
import requests
import pandas as pd

# load NFL stadium data
# originally from https://www.google.com/fusiontables/DataSource?snapid=S291132B2Wb
# Note: We'll treat domed stadiums and stadiums with retractable roofs
# equivalently. According to this article:
# http://sports.yahoo.com/blogs/nfl-shutdown-corner/nfl-retractable-roof-stadiums-stay-closed-66-percent-175043306--nfl.html
# teams with a retractable roof close the roof 66% of the time, so this is a
# reasonable simplification. In any case it's likely the weather is good on the
# gamedays they do not close the roof.

stadiums = {}
with open('../data/other/stadiums.csv', 'rU') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

for row in rows:
    team = row['Team'].split(' ')[-1]
    location = row['City']
    city, state = location.split(', ', 1)
    dome = row['Dome'] == 'TRUE' or row['Retractable Roof'] == 'TRUE'
    stadiums[team] = (city, state, dome)


def get_weather(date, city, state, dome):
    date_str = date.strftime("%Y%m%d")
    r = requests.get('http://api.wunderground.com/api/113cecba1dfb48b9/history_{}/q/{}/{}.json'.format(date_str, state, city))
    data = r.json()
    daily_summary = data.get('history', {}).get('dailysummary', [{}])[0]
    mean_temp = daily_summary.get('meantempi')
    precipitation_inches = daily_summary.get('precipi')
    snowfall_inches = daily_summary.get('snowfalli')
    wind_speed = daily_summary.get('meanwindspdi')
    snow = daily_summary.get('snow') == '1'
    rain = daily_summary.get('rain') == '1'

    if precipitation_inches == 'T':
        precipitation_inches = 0

    return mean_temp, rain, snow, precipitation_inches, snowfall_inches, wind_speed

season = 2013

df = pd.DataFrame.from_csv('../data/play_by_play/{}.csv'.format(season)).reset_index()
games_list = df.copy().drop_duplicates(cols=['Date', 'Tm', 'Opp'])
games_list_tuples = [tuple(x) for x in games_list[['Date', 'Tm', 'Opp', 'Team Game Location', 'Game Week']].values]
games = set()

for date, team, opponent, home_away, week in games_list_tuples:
    if home_away == 'Home':
        home_team = team
        away_team = opponent
    elif home_away == 'Away':
        home_team = opponent
        away_team = team

    # if neither team is home or away, then we don't know where the game is, so we can't
    # get weather data.

    games.add((date, home_team, away_team, week))

games = list(games)
games_with_weather = []

for date, home_team, away_team, week in games:
    try:
        city, state, dome = stadiums.get(home_team)

        if dome:
            # we'll assume 0 precipitation and a temperature of 65.0 degrees F
            # for domed stadiums (and those with a retractable roof)
            precipitation_inches = 0
            snowfall_inches = 0
            snow = False
            rain = False
            wind_speed = 0
            mean_temp = 65.0
        else:
            mean_temp, rain, snow, precipitation_inches, snowfall_inches, wind_speed = get_weather(date, city, state, dome)
    except:
        print 'Error on {} {} {} {}'.format(date, home_team, away_team, week)
        print 'Skipping...'
        continue

    games_with_weather.append({
        'Week': week,
        'Home Team': home_team,
        'Away Team': away_team,
        'Mean Temperature': mean_temp,
        'Rain': rain,
        'Snow': snow,
        'Precipitation Inches': precipitation_inches,
        'Snowfall Inches': snowfall_inches,
        'Mean Wind Speed MPH': wind_speed,
        'Dome': dome,
    })

with open('../data/weather/{}.csv'.format(season), 'w+') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=('Week', 'Home Team', 'Away Team', 'Mean Temperature', 'Rain', 'Snow', 'Precipitation Inches', 'Snowfall Inches', 'Mean Wind Speed MPH', 'Dome'))
    writer.writeheader()
    writer.writerows(games_with_weather)
