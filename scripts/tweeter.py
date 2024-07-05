import tweepy
import configparser
import subprocess
from dataclasses import dataclass

config = configparser.ConfigParser()
config.read("bitcoin.conf")
CONSUMER_KEY = config['twitter']['CONSUMER_KEY']
CONSUMER_SECRET = config['twitter']['CONSUMER_SECRET']
ACCESS_KEY = config['twitter']['ACCESS_KEY']
ACCESS_SECRET = config['twitter']['ACCESS_SECRET']

IMSG_ADDRESS = config['settings']['email']


client_V2 = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_KEY, access_token_secret=ACCESS_SECRET)
client_V1 = tweepy.API(tweepy.OAuth1UserHandler(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_KEY, access_token_secret=ACCESS_SECRET))

@dataclass
class Tweet():
    text: str
    image: str = None

def sendTweet(tweet: Tweet):
    print(tweet)
    try:
        if tweet.image is None:
            return client_V2.create_tweet(text=tweet.text)
        else:
            media = client_V1.media_upload(filename=tweet.image)
            return client_V2.create_tweet(text=tweet.text, media_ids=[media.media_id])
    except Exception as e:
        print(e)

    
def sendImessage(text):
    script = f'tell application "Messages" to send "{text}" to buddy "{IMSG_ADDRESS}"'
    subprocess.run(["osascript", "-e", script])
