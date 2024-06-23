import time
from datetime import datetime, timedelta

from bitcoin import Bitcoin
from scripts.tweeter import tweet, sendImessage


SEND_IMSG = True
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

        if PRINT_CONSOLE: print(f"{message}\n")


class FeeAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=20):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        priorities = bitcoin.getFeePriorities()
        if priorities[0] <= self.threshold:
            self.sendAlert(f"#Bitcoin fee rate is low:\nPriorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")
        if priorities[0] >= self.threshold:
            self.sendAlert(f"#Bitcoin feerate is high\n Priorities: {priorities[0]}, {priorities[1]}, {priorities[2]}")

class PriceAlert(BaseAlert):
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

    def checkAndAlert(self):
        bitcoin.updateData()
        message = bitcoin.getNewBlockMessage()
        if message:
            self.sendAlert(message)

feeAlert = FeeAlert(3600*24)
priceAlert = PriceAlert(60)
newBlockAlert = NewBlockAlert(60)


bitcoin = Bitcoin()
bitcoin.initData()

while True:
    feeAlert.checkAndAlert()
    priceAlert.checkAndAlert()
    newBlockAlert.checkAndAlert()
    time.sleep(60)