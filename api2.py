from flask import Flask, jsonify, request
from urllib.parse import unquote
import random

app = Flask(__name__)


#http://127.0.0.1:5000/reddit_api?topic=india
#http://127.0.0.1:5000/twitter_api?topic=india

def fetch_twitter_api(topic='indiana', post_counts=20):
    import tweepy
    #from tweepy import *
    
    # Tokens and keys
    consumer_key = "hWNSgkUWzODJLEu4WpM2NvmnS"
    consumer_secret = "wLEw59J7Kmo17ExFN9QfuBjRDqq2vRAErHerrFu61MFFdy70CO"
    access_token = "1478233626093359106-WJIRpHgBzooci9Dt3P7A8YPtMTMtBZ"
    access_token_secret = "2TtQ87dKkp0d9gqG86qqAYLuwHpGa9VJxTDShoP7vOaK4"
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAKyOmwEAAAAAqGTUk3N2%2FZGYBK5vOYCJNZ44fyE%3D5dpekUvurkENJ6JQvONDteN8TznSFVWGexcKabs41e2tJS3LnM"
    callback_uri = 'oob'

    # Configure the Twitter API credentials
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # get api data
    #topic = 'indiana'
    tweets = api.search_tweets(q=topic, count=post_counts, lang = 'en', tweet_mode="extended")
    
    return tweets

def twitter_api(topic='indiana', post_counts=20):
    post_counts = random.randint(30,45)
    tweets = fetch_twitter_api(topic, post_counts)
    # scrap tweets from api raw data
    data_tweets = []
    for tweet in tweets:
        try:
            # tweet data
            try:
                data = tweet.retweeted_status.full_text.replace('\n', ' ')
                #print('try')
            except:
                data = tweet.full_text
                #print('except')

            #post time    
            try:
                post_date = str(tweet.created_at.replace(tzinfo=None))
            except:
                post_date = None

            # user_id
            try:
                user_id = tweet.entities['user_mentions'][0]['screen_name']
            except:
                try:
                    user_id = tweet['user']['screen_name']
                except:
                    user_id = None

            data_tweets.append({'data':data, 'post_date':post_date, 'user_id':user_id, 'platform':'twitter'})
        except:
            #print('fail')
            pass        
    return data_tweets


def fetch_reddit_api(topic='indiana', post_counts=20):
    import praw
    
    reddit = praw.Reddit(
        client_id="TqrrKYVBmnJxhRRmsFb1jA",
        client_secret="nEX6xZ-CSZ82KnL3qTu7R1G00dRRgw",
        password="Password@123",
        user_agent="testscript by u/Simple_Pin4470",
        username="Simple_Pin4470",
    )

    search_results = reddit.subreddit('all').search(topic, limit=post_counts)

    return search_results


def reddit_api(topic='indiana', post_counts=20):
    import datetime
    import json
    
    post_counts = random.randint(30,45)
    search_results = fetch_reddit_api(topic, post_counts)

    data_reddit = []
    for post in search_results:
        try:
            try:
                data = post.selftext+post.title
                data = data.replace('\n', ' ').replace('\t', ' ')
            except:
                data = None

            try:
                user_id = post.author.name
            except:
                user_id = None

            try:
                post_date = str(datetime.datetime.fromtimestamp(post.created_utc))
            except:
                post_date = None


            data_reddit.append({'data':data, 'post_date':post_date, 'user_id':user_id, 'platform':'reddit'})
        except:
            pass

    return data_reddit


@app.route('/reddit_api')
def run_program_reddit():
    topic = unquote(request.query_string.decode())
    return jsonify(reddit_api(topic))

@app.route('/twitter_api')
def run_program_twitter():
    topic = unquote(request.query_string.decode())
    return jsonify(twitter_api(topic))

@app.route('/get_data')
def run_program_all_data():
    topic = unquote(request.query_string.decode())
    data = reddit_api(topic)
    data.extend(twitter_api(topic))
    random.shuffle(data)
    return jsonify(data)

@app.route('/test')
def run_program_test():
    #topic = request.args.get('topic', 'indiana')
    topic = unquote(request.query_string.decode())
    return topic

if __name__ == '__main__':
    app.run(debug=True)