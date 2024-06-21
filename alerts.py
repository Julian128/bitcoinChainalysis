import time
from datetime import datetime, timedelta

from bitcoin import Bitcoin
from scripts.tweeter import tweet, sendImessage


SEND_IMSG = False
SEND_TWEET = False
PRINT_CONSOLE = True

class BaseAlert:
    def __init__(self, cooldownPeriod):
        self.cooldownPeriod = timedelta(seconds=cooldownPeriod)
        self.lastAlertTime = None

    def canSendAlert(self):
        return not self.lastAlertTime or datetime.now() >= self.lastAlertTime + self.cooldownPeriod

    def sendAlert(self, message):
        if self.canSendAlert():
            self.sendMessage(message)
            self.lastAlertTime = datetime.now()

        time.sleep(10)

    def sendMessage(self, message):

        # message = "#bitcoin\n" + message

        if SEND_IMSG: sendImessage(message)

        if SEND_TWEET: tweet(message)

        if PRINT_CONSOLE: print(f"############################################################\n{message}\n############################################################\n")

bitcoin = Bitcoin()

class LowFeesAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=20):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        priorities = bitcoin.getFeePriorities()
        if priorities[0] <= self.threshold:
            self.sendAlert(f"#Bitcoin fee rate is low:\nPriorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")

class HighFeesAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=200):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        priorities = bitcoin.getFeePriorities()
        if priorities[0] >= self.threshold:
            self.sendAlert(f"#Bitcoin feerate is high\n Priorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")

class WhaleAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=10_000):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        utxoValues = bitcoin.getBlockUtxoValues(bitcoin.getLatestBlock())
        largestUtxo = max(utxoValues)
        if largestUtxo >= self.threshold:
            self.sendAlert(f"#Bitcoin whale alert:\n{(largestUtxo):.2f} BTC UTXO found in the latest block")        

class SatsPerUsdAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=25):
        super().__init__(cooldownPeriod)
        self.threshold = threshold
        self.lastPrice = 0

    def checkAndAlert(self):
        _, satsPerUsd = bitcoin.getPrice()
        if self.lastPrice == 0:
            self.lastPrice = satsPerUsd
            return
        if abs(satsPerUsd - self.lastPrice) >= self.threshold:
            self.lastPrice = round(satsPerUsd, -1)
            self.sendAlert(f"#Bitcoin price update:\nSats per USD: {self.lastPrice}")

class DifficultyAdjustmentAlert(BaseAlert):
    def __init__(self, cooldownPeriod):
        super().__init__(cooldownPeriod)

    def checkAndAlert(self):
        height = bitcoin.getBlockCount()
        if height % 2016 == 0:
            difficulty = bitcoin.getBlockFromHeight(height)["difficulty"]
            lastBlockDifficulty = bitcoin.getBlockFromHeight(height-1)["difficulty"]
            percentalChange = round((difficulty/lastBlockDifficulty - 1) * 100, 2)
            self.sendAlert(f"#Bitcoin difficulty adjusted: {percentalChange}%")

class NewBlockAlert(BaseAlert):
    def __init__(self, cooldownPeriod):
        super().__init__(cooldownPeriod)
        self.blockHeight = 0

    def checkAndAlert(self):
        if self.blockHeight == 0:
            self.blockHeight = bitcoin.getBlockCount()
            return
        height = bitcoin.getBlockCount()
        if height > self.blockHeight:
            self.blockHeight = height
            if height % 100 == 0:
                block = bitcoin.getBlockFromHeight(height)
                self.sendAlert(f"#Bitcoin block #{height} was mined:\nTotal block value: {int(block['value'])} BTC")


lowFeesAlert = LowFeesAlert(3600*10)
highFeesAlert = HighFeesAlert(3600*10)
whaleAlert = WhaleAlert(3600)
satsPerUsdAlert = SatsPerUsdAlert(60)
difficultyAdjustmentAlert = DifficultyAdjustmentAlert(3600)
newBlockAlert = NewBlockAlert(60)

while True:
    newBlockAlert.checkAndAlert()
    lowFeesAlert.checkAndAlert()
    highFeesAlert.checkAndAlert()
    whaleAlert.checkAndAlert()
    satsPerUsdAlert.checkAndAlert()
    difficultyAdjustmentAlert.checkAndAlert()
    time.sleep(60)
