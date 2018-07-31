"""
A server that responds with two pages, one showing the most recent
100 tweets for given user and the other showing the followers
of a given user (sorted by the number of followers those users have).

For authentication purposes, the server takes a commandline argument
that indicates the file containing Twitter data in a CSV file format:

    consumer_key, consumer_secret, access_token, access_token_secret

For example, I pass in my secrets via file name:

    /Users/parrt/Dropbox/licenses/twitter.csv

Please keep in mind the limits imposed by the twitter API:

    https://dev.twitter.com/rest/public/rate-limits

For example, you can only do 15 follower list fetches per
15 minute window, but you can do 900 user timeline fetches.
"""
import sys
from flask import Flask, render_template
from tweetie import *
from colour import Color
from numpy import median

app = Flask(__name__)

def add_color(tweets):
    """
    Given a list of tweets, one dictionary per tweet, add
    a "color" key to each tweets dictionary with a value
    containing a color graded from red to green. Pure red
    would be for -1.0 sentiment score and pure green would be for
    sentiment score 1.0.

    Use colour.Color to get 100 color values in the range
    from red to green. Then convert the sentiment score from -1..1
    to an index from 0..100. That index gives you the color increment
    from the 100 gradients.

    This function modifies the dictionary of each tweet. It lives in
    the server script because it has to do with display not collecting
    tweets.
    """
    colors = list(Color("red").range_to(Color("green"), 100))
    for t in tweets:
        score = t['score']
        # convert sentiment score from -1..1 to 0..100
        # https://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
        new_score = (((score - (-1)) * (100 - 0)) / (1 - (-1))) + 0
        color_index = int(round(new_score))

        # add a new key-value pair to the tweet dictionary
        t['color'] = str(colors[color_index])


@app.route("/<name>")
def tweets(name):
    "Display the tweets for a screen name color-coded by sentiment score"
    # first define variable in templates
    # then define variable here and put them in render_template function
    tweets = fetch_tweets(api, name)['tweet']
    add_color(tweets)

    all_score = []
    for i in range(len(tweets)):
        all_score.append(tweets[i]["score"])
    median_score = median(all_score)

    return render_template('tweets.html', name=name, median_score=median_score, tweets=tweets)



@app.route("/following/<name>")
def following(name):
    """
    Display the list of users followed by a screen name, sorted in
    reverse order by the number of followers of those users.
    """
    # first define variable in templates
    # then define variable here and put them in render_template function
    friends = fetch_following(api,name)

    return render_template('following.html', name=name, friends=friends)

i = sys.argv.index('server:app')
twitter_auth_filename = sys.argv[i+1] # e.g., "/Users/parrt/Dropbox/licenses/twitter.csv"
api = authenticate(twitter_auth_filename)

#app.run(host='0.0.0.0', port=80)
