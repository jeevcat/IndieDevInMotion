#!/usr/bin/env python

import os
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
                self.log(e.message)
            else:
                for tweet in results:
                    if tweet.id not in self.history:
                        lowest_id = min(lowest_id, tweet.id)
                        highest_id = max(highest_id, tweet.id)
                        if not hasattr(tweet, 'retweeted_status'):
                            # not a retweet
                            # print(tweet.text.encode('utf-8'))
                            try:
                                media_type = tweet.extended_entities['media'][0]['type']
                                if media_type == 'animated_gif':
                                    valid_tweets.append(tweet)
                            except AttributeError:
                                pass
                                # Doesn't have extended_entities
                if len(results) < 100:
                    # we've reached tweets that we've seen before
                    break
        self.most_recent_id = max(highest_id, self.most_recent_id)
        return valid_tweets

    def tweet(self, api, text):
        """Send out the text as a tweet."""

        # Send the tweet and log success or failure
        try:
            self.api.update_status(text)
        except tweepy.error.TweepError as e:
            self.log(e.message)
        else:
            self.log("Tweeted: " + text)

    def retweet(self, tweet):
        """ Retweet given ID"""
        try:
            self.api.retweet(tweet.id)
            self.log("Retweeted: " + tweet.text)
        except tweepy.error.TweepError as e:
            # Probably already retweeted
            self.log(e.message[0]['message'])
        self.history.append(tweet.id)

    def log(self, message):
        """Log message to logfile."""
        path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(path, logfile_name), 'a+') as f:
            t = strftime("%d %b %Y %H:%M:%S", gmtime())
            string = message if type(message) is str else message.decode('utf-8')
            f.write("\n" + t + " " + string)

    def run(self):
        self.log("Finding tweets with #indiedev or #gamedev...")
        retweetable = self.find_tweets(
            '#indiedev OR #gamedev OR #procjam OR #pixelart', 5)

        for tweet in retweetable:
            if tweet.id not in self.history:
                self.retweet(tweet)
