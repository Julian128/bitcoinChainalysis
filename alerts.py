from bitcoin import Bitcoin
import numpy as np
import time
import subprocess

from datetime import datetime, timedelta

class BaseAlert:
    def __init__(self, cooldownPeriod):
        self.cooldownPeriod = timedelta(seconds=cooldownPeriod)
        self.lastAlertTime = None

    def canSendAlert(self):
        return not self.lastAlertTime or datetime.now() >= self.lastAlertTime + self.cooldownPeriod

    def sendAlert(self, message):
        if self.canSendAlert():
            self.sendMessage(message)
            print(f"Alert sent: {message}")
            self.lastAlertTime = datetime.now()
        else:
            print(f"Cooldown in effect, alert not sent: {message}")

    def sendMessage(self, message):
        phone_number=""
        script = f'tell application "Messages" to send "{message}" to buddy "{phone_number}"'
        subprocess.run(["osascript", "-e", script])


bitcoin = Bitcoin()

class LowFeesAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=20):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        priorities = bitcoin.getFeePriorities()
        if priorities[1] <= self.threshold:
            self.sendAlert(f"Bitcoin feerate is low: {priorities}")

class HighFeesAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=200):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        priorities = bitcoin.getFeePriorities()
        if priorities[1] >= self.threshold:
            self.sendAlert(f"Bitcoin feerate is high: {priorities}")


class WhaleAlert(BaseAlert):
    def __init__(self, cooldownPeriod, threshold=10000):
        super().__init__(cooldownPeriod)
        self.threshold = threshold

    def checkAndAlert(self):
        for block in bitcoin.iterateLatestBlocks(3):
            utxoValues = bitcoin.getBlockUtxoValues(block)
            utxoValues = utxoValues[utxoValues > self.threshold]
            utxoValues = [int(value) for value in utxoValues]
            if len(utxoValues) > 0:
                self.sendAlert(f"Whale alert: {utxoValues}")

lowFeesAlert = LowFeesAlert(3600)
highFeesAlert = HighFeesAlert(3600)
whaleAlert = WhaleAlert(3600)

while True:
    lowFeesAlert.checkAndAlert()
    highFeesAlert.checkAndAlert()
    whaleAlert.checkAndAlert()
    time.sleep(60)
