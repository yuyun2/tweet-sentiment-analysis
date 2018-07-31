import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret, access_token, access_token_secret = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    #public_tweets = api.home_timeline()auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    #auth.set_access_token(access_token, access_token_secret)

    #api = tweepy.API(auth)

    #public_tweets = api.home_timeline()
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    #make request for 100 most recent tweets
    new_tweets = api.user_timeline(screen_name = name, count = 100)

    dic_tweet = {}
    dic_tweet['user'] = name 
    dic_tweet['count'] = len(new_tweets)
    
    list_of_tweet = []

    for tweet in new_tweets:

      inner_dic = {}

      keys = ['id', 'created', 'retweeted', 'text','hashtags','urls','mentions','score']

      # for score 
      sentence = tweet.text
      analyser = SentimentIntensityAnalyzer()
      score = analyser.polarity_scores(sentence)['compound']

      inner_dic['id'] = tweet.id_str
      inner_dic['created'] = tweet.created_at
      inner_dic['retweeted'] = tweet.retweet_count
      inner_dic['text'] = tweet.text
      inner_dic['hashtags'] = tweet.entities.get('hashtags')
      inner_dic['url'] = 'https://twitter.com/' + name +'/status/' + str(tweet.id)
      inner_dic['score'] = score

      list_of_tweet.append(inner_dic)

    dic_tweet['tweet'] = list_of_tweet

    return dic_tweet



def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    # get list friends IDs
    #https://stackoverflow.com/questions/26792734/get-all-friends-of-a-given-user-on-twitter-with-tweepy
    #https://codereview.stackexchange.com/questions/101905/get-all-followers-and-friends-of-a-twitter-user

    ids = []
    for page in tweepy.Cursor(api.friends_ids, screen_name = name).pages():
      ids.extend(page)
      #time.sleep(60)

    screen_names = [user.screen_name for user in api.lookup_users(user_ids=ids)]

    # once we get full list of friends id, we go to each friend's page and fetch their information
    friends = []

    for name in screen_names:

      user = api.get_user(screen_name = name)

      # initilize a dictionary
      dic_friend = {}

      dic_friend['name'] = user.name
      dic_friend['screen_name'] = name
      dic_friend['followers'] = user.followers_count
      dic_friend['created'] = user.created_at.strftime("%Y-%m-%d")
      dic_friend['image'] = user.profile_image_url_https

      friends.append(dic_friend)

      friends = sorted(friends, key=lambda x: x['followers'], reverse=True)


    return friends











