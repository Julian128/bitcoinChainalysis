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

        time.sleep(5)

    def sendMessage(self, message):

        # message = "#bitcoin\n" + message

        if SEND_IMSG: sendImessage(message)

        if SEND_TWEET: tweet(message)

        if PRINT_CONSOLE: print(f"############################################################\n{message}\n############################################################\n")

bitcoin = Bitcoin()

class FeeAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=20):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        print("LowFeesAlert")
        priorities = bitcoin.getFeePriorities()
        if priorities[0] <= self.threshold:
            self.sendAlert(f"#Bitcoin fee rate is low:\nPriorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")
        if priorities[0] >= self.threshold:
            self.sendAlert(f"#Bitcoin feerate is high\n Priorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")

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
            block = bitcoin.getBlockFromHeight(height)

            # difficulty adjustment
            if height % 2016 == 0:
                difficulty = block["difficulty"]
                lastBlockDifficulty = bitcoin.getBlockFromHeight(height-1)["difficulty"]
                percentalChange = round((difficulty/lastBlockDifficulty - 1) * 100, 2)
                self.sendAlert(f"#Bitcoin difficulty adjusted: {percentalChange}%")

            # whale alert
            utxoValues = bitcoin.getBlockUtxoValues(block)
            largestUtxo = max(utxoValues)
            if largestUtxo >= self.threshold:
                self.sendAlert(f"#Bitcoin whale alert:\n{(largestUtxo):.2f} BTC UTXO found in the latest block")        

            # empty block alert
            if len(block["tx"]) == 1:
                self.sendAlert(f"#Bitcoin empty block mined:\nBlock height: {height}")


feeAlert = FeeAlert(3600*24)
satsPerUsdAlert = SatsPerUsdAlert(60)
newBlockAlert = NewBlockAlert(60)

while True:
    newBlockAlert.checkAndAlert()
    feeAlert.checkAndAlert()
    satsPerUsdAlert.checkAndAlert()
    time.sleep(60)
