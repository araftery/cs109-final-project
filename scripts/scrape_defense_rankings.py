from bs4 import BeautifulSoup
import csv
import requests

for season in range(2000, 2014):
    url = 'http://www.pro-football-reference.com/years/{}/opp.htm'.format(season)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    table = soup.findAll('table', {'id': 'passing'})
    team_stats = soup.find('table', {'id': 'team_stats'})

    header_rows = team_stats.select('thead tr')
    body_rows = team_stats.select('tbody tr')

    header = [i.text for i in header_rows[1].findAll('th')]
    tm_index = header.index('Tm')
    yp_index = header.index('Y/P')
    passing_ya_index = header.index('NY/A')
    rushing_ya_index = header.index('Y/A')

    rows = []
    for row in body_rows:
        row = [i.text for i in row.findAll('td')]
        team = row[tm_index]
        if team == 'Avg Team':
            continue

        # we just want the team name, not the team's city
        team_list = team.split(' ')
        team = team_list[-1]

        rows.append([team, row[yp_index], row[passing_ya_index], row[rushing_ya_index]])

    # add rankings
    sorted_by_passing = sorted(rows, key=lambda x: x[2])
    sorted_by_rushing = sorted(rows, key=lambda x: x[3])
    passing_rankings = {info[0]: ranking + 1 for ranking, info in enumerate(sorted_by_passing)}
    rushing_rankings = {info[0]: ranking + 1 for ranking, info in enumerate(sorted_by_rushing)}

    for row in rows:
        team = row[0]
        row += [passing_rankings[team], rushing_rankings[team]]

    # output csv
    new_header = ('Tm', 'Y/P', 'Passing Y/A', 'Rushing Y/A', 'Pass Defense Ranking', 'Rush Defense Ranking')
    with open('../data/defense_rankings/{}.csv'.format(season), 'w+') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(new_header)
        writer.writerows(rows)
