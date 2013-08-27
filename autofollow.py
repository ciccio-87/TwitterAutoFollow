#!/usr/bin/python

import twitter
import urllib2
from bs4 import BeautifulSoup
import sys
import argparse
import time
import random


def scrape_twitaholic(place):
    url = 'http://twitaholic.com/top100/followers/bylocation/' + place + '/'
    print 'opening url'
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    res = []
    print 'scraping'
    for tr in soup.findAll('tr', {'style': 'border-top:1px solid black;'}):
        temp = tr.find('td', {'class': 'statcol_name'})
        res.append(temp.a['title'].split('(')[1][4:-1])
    return res


def name2geo(place):
    url = 'http://en.wikipedia.org/w/index.php?search=' + \
        '_'.join(place.split())
    # print url
    headers = {'User-agent': 'Mozilla/5.0'}
    req = urllib2.Request(url, None, headers)
    try:
        soup = BeautifulSoup(urllib2.urlopen(req).read())
    except:
        print 'Got troubles opening wikipedia page, exiting'
        sys.exit(1)
    for anchor in soup.findAll('a', {'class': 'external text'}):
        if anchor['href'].startswith('//tools.wmflabs.org'):
            link = anchor['href']
    try:
        link = 'http:' + link
    except NameError, e:
        print 'link not found'
        sys.exit(1)
    # print link
    # req = urllib2.Request(link,None,headers)
    try:
        soup = BeautifulSoup(urllib2.urlopen(link).read())
    except:
        print 'troubles opening link, exiting'
        sys.exit(1)
    snip = soup.find('span', {'class': 'geo'})
    temp = []
    for span in snip.findAll('span'):
        temp.append(span.string)
    coordinates = ','.join(temp)
    return coordinates


def start_api(keys):
    ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET = keys
    try:
        return twitter.Twitter(
            auth=twitter.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET))
    except:
        print 'errors connecting to Twitter, exiting'
        sys.exit(1)


def twitter_geo_search(api, coord, lang, q='', count=50):
    geocode = coord + ',15mi'
    if lang is None:
        tweets = api.search.tweets(q=q, geocode=geocode, count=count)
    else:
        tweets = api.search.tweets(
            q=q, geocode=geocode, count=count, lang=lang)
    users = []
    for status in tweets['statuses']:
        users.append(status['user']['screen_name'])
    users = list(set(users))
    print 'found ' + str(len(users)) + ' unique users'
    return users


def twitter_name_search(api, q='', lang='', count=50):
    if lang is None:
        tweets = api.search.tweets(q=q, count=count)
    else:
        tweets = api.search.tweets(q=q, count=count, lang=lang)
    users = []
    for status in tweets['statuses']:
        users.append(status['user']['screen_name'])
    users = list(set(users))
    print 'found ' + str(len(users)) + ' unique users'
    return users


def twitter_follow(api, username):
    print 'following ' + username
    return api.friendships.create(screen_name=username)


def twitter_follow_all(api, results, n=20):
    following = len(api.friends.ids()['ids'])
    for user in results[:n]:
        wait = random.randrange(15, 90)  # try not to be too spammy
        try:
            res = twitter_follow(api, user)
        except:
            print 'got twitter error trying to follow ' + user
        print 'now sleeping for ' + str(wait) + ' seconds'
        temp = range(wait)
        temp.reverse()
        # for i in xrange(wait):
        for i in temp:
            time.sleep(1)
            sys.stdout.write('\r   ')
            sys.stdout.flush()
            sys.stdout.write('\r%d' % i)
            sys.stdout.flush()

        sys.stdout.write('\n')
        # print 'now sleeping for a while'
        # for i in xrange(wait):
            # time.sleep(1)
            # if i == wait-1:
                        # print '.'
        # sys.stdout.write('\n')
        # sys.stdout.flush()
    # else:
            # else:
            # print '.',
        # sys.stdout.write(' .')
        # sys.stdout.flush()
    new_following = len(api.friends.ids()['ids'])
    if following + len(results) == new_following:
        print 'everything seems alright, you\'re now following ' + str(following) + ' users'
    else:
        print 'something went bad, some following not worked'

parser = argparse.ArgumentParser(
    description='Follow Twitter user near to a place of your choice')
parser.add_argument('place', metavar='place', type=str, nargs=1,
                    help='the place to look for')
parser.add_argument(
    '-m', '--mode', metavar='mode', type=int, nargs='?', default=1,
    help='search mode:\n\t1: place name search on Twitter\n\t2: scrape Twitaholic\n\t3: search nearby tweets (hard guesses on coordinates)')
parser.add_argument('-f', '--file', action='store_true',
                    help='enable use of a "settings.py" conf file (see example)')
parser.add_argument('-l', '--lang', type=str, metavar='LANG',
                    nargs='?', help='Language for statuses search')
parser.add_argument('--access_token', type=str,
                    metavar='ACCESS_TOKEN', nargs='?', help='Twitter API access token')
parser.add_argument('--access_token_secret', type=str,
                    metavar='ACCESS_TOKEN_STRING', nargs='?', help='Twitter API access token secret')
parser.add_argument('--consumer_key', type=str,
                    metavar='CONSUMER_KEY', nargs='?', help='Twitter API consumer key')
parser.add_argument('--consumer_secret', type=str,
                    metavar='CONSUMER_SECRET', nargs='?', help='Twitter API consumer secret')
parser.add_argument('--print-only', action='store_true',
                    help='Just print results, no real follow')
parser.add_argument('-n','--max-follow', nargs='?', type=int, metavar='max_follow',
                    help='Maximun number of users to follow')
parser.add_argument('-b','--blacklist', action='store_true',
                    help='Use blacklist file')
parser.add_argument('-bf','--blacklist-file', nargs='?', type=str, metavar='blacklist_file',
                    help='Blacklist file')

args = vars(parser.parse_args())

#print '\n\n' + str(args) + '\n\n'

# if args['f'] is None and ((args['access_token'] is None) or (args['access_token_secret'] is None) or (args['consumer_secret'] is None) or (args['consumer_key'] is None)):
#	if not args['print_only'] and args['m'] == 2:
#		print 'Twitter API credentials not given, exiting'
#		print parser.print_help()
#		sys.exit(0)

if args['file']:
    try:
        from settings import USER
        from settings import USE_BLACKLIST,BLACKLIST_FILE
        if not args['blacklist']:
	    args['blacklist'] = USE_BLACKLIST
	    args['blacklist_file'] = BLACKLIST_FILE
	    print str(args)
    except:
        print 'bad file given, exiting'
        sys.exit(1)

elif args['access_token'] and args['access_token_secret'] and args['consumer_key'] and args['consumer_secret']:
    USER = args['access_token'], args['access_token_secret'], args[
        'consumer_key'], args['consumer_secret']

else:
    print 'Twitter API credentials not given, exiting'
    print parser.print_help()
    sys.exit(0)
    
if args['print_only']:
    print '\nprint-only mode enabled\n'

    
if args['max_follow']:
    n = args['max_follow']
else:
    n = 20
results = []
if args['mode'] == 1:
    results = twitter_name_search(
        start_api(USER), args['place'][0], args['lang'])
   
elif args['mode'] == 2:
    results = scrape_twitaholic(args['place'][0])
    
elif args['mode'] == 3:
    results = twitter_geo_search(
        start_api(USER), name2geo(args['place'][0]), args['lang'])

else:
    print 'mode not recognized'
    sys.exit(0)

if args['blacklist']:
    print 'Reading BlackList from file'
    try:
	bl = open(args['blacklist_file']).readlines()
    except:
	print 'troubles reading blacklist file'
	sys.exit(0)
    print 'found ' + str(len(bl)) + ' users in blacklist'
    temp = []
    for u in results:
	if u not in bl:
	    temp.append(u)
    results = temp
    
if args['print_only']:
    print results
else:
    twitter_follow_all(start_api(USER), results, n)