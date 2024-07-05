import time
from datetime import datetime, timedelta

from bitcoin import Bitcoin
from scripts.tweeter import sendTweet, sendImessage, Tweet


SEND_IMSG = False
SEND_TWEET = True
PRINT_CONSOLE = True

class BaseAlert:
    def __init__(self, cooldownPeriod):
        self.cooldownPeriod = timedelta(seconds=cooldownPeriod)
        self.lastAlertTime = None

    def canSendAlert(self):
        return not self.lastAlertTime or datetime.now() >= self.lastAlertTime + self.cooldownPeriod

    def sendAlert(self, tweet: Tweet):
        if self.canSendAlert():
            self.sendMessage(tweet)
            self.lastAlertTime = datetime.now()

        time.sleep(5)

    def sendMessage(self, tweet: Tweet):

        if SEND_IMSG: sendImessage(tweet.text)

        if SEND_TWEET: sendTweet(tweet)

        if PRINT_CONSOLE: print(f"##########\nNew tweet\n##########\n{tweet.text}\n")

class NewBlockAlert(BaseAlert):
    def __init__(self, cooldownPeriod=0):
        super().__init__(cooldownPeriod)

    def checkAndAlert(self):
        tweets = bitcoin.updateData()
        if len(tweets) > 1:
            print("Multiple tweets")
        for tweet in tweets:
            if tweet:
                self.sendAlert(tweet)
            else:
                print(tweet)
newBlockAlert = NewBlockAlert()

bitcoin = Bitcoin()
bitcoin.initData()

while True:
    newBlockAlert.checkAndAlert()
    time.sleep(60)