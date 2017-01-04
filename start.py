#!/usr/bin/env python3

import time
from bot import Bot

if __name__ == "__main__":
    bot = Bot()
    counter = 0
    while True:
        counter += 1
        bot.log("Query " + str(counter))
        bot.run()
        bot.log("Sleeping for 5 min...")
        time.sleep(5 * 60)
    # api.retweet(tweet.id)
    # log("Retweeted: " + tweet.text)
    # tweet_text = create_tweet()
    # tweet(api, tweet_text)
