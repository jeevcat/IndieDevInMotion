#!/usr/bin/env python

import os
import json
import time
import datetime
import tweepy
from secrets import *
from time import gmtime, strftime


# ====== Individual bot configuration ==========================
bot_username = 'IndieInMotion'
logfile_name = bot_username + ".log"

# ==============================================================


class Bot(object):
    def __init__(self):
        self.api = self.auth()
        self.history = list()
        self.most_recent_id = 0

    def create_tweet(self):
        """Create the text of the tweet you want to send."""
        # Replace this with your code!
        text = "Bleep blop bloop. Second test tweet from the bot's API."
        return text

    def auth(self):
        """ Authenticate. Returns tweepy api object"""
        # Twitter authentication
        auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
        auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
        return tweepy.API(auth)

    def find_tweets(self, q, iterations):
        lowest_id = float("Inf")
        highest_id = 0
        valid_tweets = list()
        count = 0

        for i in range(iterations):
            try:
                # first time requesting tweets
                if lowest_id == float('Inf'):
                    results = self.api.search(q,
                                              lang='en',
                                              result_type='recent',
                                              since_id=self.most_recent_id,
                                              count=100)
                else:
                    results = self.api.search(q,
                                              lang='en',
                                              result_type='recent',
                                              count=100,
                                              since_id=self.most_recent_id,
                                              max_id=lowest_id - 1)
            except tweepy.error.TweepError as e:
                self.log(e.reason)
            else:
                for tweet in results:
                    if tweet.id not in self.history:
                        lowest_id = min(lowest_id, tweet.id)
                        highest_id = max(highest_id, tweet.id)
                        if not hasattr(tweet, 'retweeted_status'):
                            # not a retweet
                            # print(tweet.text.encode('utf-8'))
                            try:
                                for media in tweet.extended_entities['media']:
                                    if media['type'] == 'animated_gif':
                                        h = media['sizes']['large']['h']
                                        w = media['sizes']['large']['w']
                                        if(h*w > 50000):
                                            # gif is not crappy and small
                                            valid_tweets.append(tweet)
                                        if(h*w > 200000):
                                            # gif is especially nice
                                            self.like(tweet)
                            except AttributeError:
                                pass
                                # Doesn't have extended_entities
                count += len(results)
                if len(results) < 100:
                    # we've reached tweets that we've seen before
                    break
        self.most_recent_id = max(highest_id, self.most_recent_id)
        self.log("Processed " + str(count) + " tweets, "
                 "of which " + str(len(valid_tweets)) + " are valid.")
        return valid_tweets

    def tweet(self, api, text):
        """Send out the text as a tweet."""

        # Send the tweet and log success or failure
        try:
            self.api.update_status(text)
        except tweepy.error.TweepError as e:
            self.log(e.reason)
        else:
            self.log("Tweeted: " + text)

    def retweet(self, tweet):
        """ Retweet given ID"""
        try:
            self.api.retweet(tweet.id)
            self.log("Retweeted: " + tweet.text)

            self.api.create_friendship(tweet.user.id)
            self.log("Followed : " + tweet.user.name)
        except tweepy.error.TweepError as e:
            # Probably already retweeted
            self.log(e.reason)
        self.history.append(tweet.id)

    def like(self, tweet):
        try:
            self.api.create_favorite(tweet.id)
            self.log("Liked: " + tweet.text)
        except tweepy.error.TweepError as e:
            # Probably already liked
            self.log(e.reason)

    def unfollow_inactive(self):
        for friend in self.limit_handled(
                tweepy.Cursor(self.api.friends, count=200).items()):
            if not hasattr(friend, 'status'):
                continue
            if not hasattr(friend.status, 'created_at'):
                continue
            date = friend.status.created_at
            days_ago = (datetime.datetime.now() - date).days
            if days_ago > 7:
                self.log(friend.screen_name + "'s last tweet was " +
                         str(days_ago) + " days ago. Unfollowing.")
                self.api.destroy_friendship(friend.id)

    def limit_handled(self, cursor):
        """Wrap a cursor with this function to auto sleep
           for 15 min if rate limit reached"""
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                self.log("Rate limit reached. Skipping unfollow_inactive.")
                return
            except tweepy.error.TweepError:
                self.log("Read timeout. Skipping...")
                return

    def log(self, message):
        """Log message to logfile."""
        path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(path, logfile_name), 'a+') as f:
            t = strftime("[%d %b %Y %H:%M:%S]", gmtime())
            string = message if type(message) is str else message.encode('utf-8')
            f.write("\n" + t + " " + string)

    def run(self):
        self.unfollow_inactive()

        self.log("Finding tweets with #indiedev or #gamedev...")
        retweetable = self.find_tweets(
            "#indiedev OR #gamedev OR #procjam OR #pixelart "
            "-RT -buy -AssetStore filter:media", 5)

        for tweet in retweetable:
            if tweet.id not in self.history:
                self.retweet(tweet)
            else:
                self.log("Not retweeting as retweet is in history: " +
                         len(history))
