# -*- coding: utf-8 -*-

import requests
import json
import re
from bs4 import BeautifulSoup

from werkzeug.contrib.cache import SimpleCache


SUMMARY_URL = 'http://www.espncricinfo.com/netstorage/summary.json'
MATCH_URL = 'http://www.espncricinfo.com/ci/engine/match/%(match_id)s.json'
SCORECARD_URL = 'http://www.espncricinfo.com/sdds/engine/match/' \
                '%(match_id)s.html?view=scorecard;wrappertype=none;xhr=1'

MATCH_ID_RE = re.compile('\/(\d+)\.html')


cache = SimpleCache()

def cached(duration):
    def decorator(func):
        def inner(*args, **kwargs):
            key_bits = [func.__name__]
            [key_bits.append(str(val)) for val in args]
            [key_bits.append(str(val)) for val in kwargs.iteritems()]
            full_key = '|'.join(key_bits)
            result = cache.get(full_key)
            if not result:
                result = func(*args, **kwargs)
                cache.set(full_key, result, duration)
            return result
        return inner
    return decorator


@cached(600)
def get_summary():
    data = json.loads(requests.get(SUMMARY_URL).content)
    
    for match in data['matches'].values():
        match['match_id'] = MATCH_ID_RE.search(match['url']).groups()[0]

    return data


def replace_links(html):
    soup = BeautifulSoup(html)
    for a in soup.findAll('a'):
        if a['href'].startswith('/'):
            a['href'] = 'http://www.espncricinfo.com' + a['href']
    return unicode(soup)


@cached(600)
def get_match(match_id):
    resp = requests.get(MATCH_URL % {'match_id': match_id})
    match = json.loads(resp.content)
    
    # match['match_card'] = replace_links(soup)
    
    match['teams'] = {}
    match['players'] = {}
    for team in match['team']:
        match['teams'][team['team_id']] = team
        if 'player' in team:
            for player in team['player']:
                match['players'][player['player_id']] = player
    
    resp = requests.get(SCORECARD_URL % {'match_id': match_id})
    match['scorecard'] = replace_links(resp.content.decode('utf-8', 'ignore'))

    return match
