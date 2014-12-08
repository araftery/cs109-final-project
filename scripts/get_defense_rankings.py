"""
This script just downloads the HTML files that will later be scraped.
We have to use this library (which is built on top of WebKit's Python bindings)
because the NFL.com site injects the table with JS after the pageload, so
requests doesn't download the information we need.
"""

import dryscrape
import itertools

years = range(2000, 2014)
categories = ['RUSHING', 'TEAM_PASSING']
combos = itertools.product(years, categories)

for season, cat in combos:
    url = "http://www.nfl.com"
    path = "/stats/categorystats?archive=true&conference=null&role=OPP&offensiveStatisticCategory=null&defensiveStatisticCategory={}&season={}&seasonType=REG&tabSeq=2".format(cat, season)
    sess = dryscrape.Session(base_url=url)
    sess.set_attribute('auto_load_images', False)
    sess.visit(path)
    with open('/vagrant/outfiles/{}_{}_defense_rankings.html'.format(season, cat), 'w+') as outfile:
        outfile.write(sess.body())
