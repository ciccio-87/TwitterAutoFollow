#!/usr/bin/python

from settings import USER
from settings import ACCOUNTS
import twitter
import time
import random
import sys


def twitter_unfollow(api, user):
    print 'unfollowing ' + user
    return api.friendships.destroy(user_id=user)


def twitter_unfollow_all(api, results):
    following = len(api.friends.ids()['ids'])
    for user in results:
        wait = random.randrange(15, 90)  # try not to be too spammy
        try:
            res = twitter_unfollow(api, user)
        except:
            print 'got twitter error trying to unfollow ' + user
            # print 'now sleeping for a while'
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
                    # if i == wait-1:
        #    sys.stdout.write('\n')
        #    sys.stdout.flush()
        # else:
        #    sys.stdout.write(' .')
        #    sys.stdout.flush()
    new_following = len(api.friends.ids()['ids'])
    if following - len(results) == new_following:
        print 'everything seems alright, you\'re now following ' + str(following) + ' users'
    else:
        print 'something went bad, some following not worked'

if __name__ == "__main__":
    i = 0
    for user in USER:
        username = user
        print 'USER = ' + username
        # print account
        ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET = ACCOUNTS[
            i]
        i += 1
        api = twitter.Twitter(
            auth=twitter.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
        friends = api.friends.ids(screen_name=username)
        print "fetched " + str(len(friends['ids'])) + " followings"
        time.sleep(1)
        followers = api.followers.ids(screen_name=username)
        print "fetched " + str(len(followers['ids'])) + " followers"

        nonmutual = []
        for user in friends['ids']:
            if user not in followers['ids']:
                nonmutual.append(str(user))

        # nonmutual.shuffle()
        random.shuffle(nonmutual)
        twitter_unfollow_all(api, nonmutual[:2])
