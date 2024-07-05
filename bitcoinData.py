import numpy as np
from collections import deque
import pickle

from block import Block
from plots import utxoValuePlot
from scripts.tweeter import Tweet

class BitcoinData:
    def __init__(self):
        self.lastBlocks: deque[Block] = deque(maxlen=100)
        self.blockHeight = 0
        # sizeOnDisk: float
        # utxos: int
        # interestingUtxos: int
        # publicNodes: int

        # mempool
        # mempoolSize: int
        # feeInflow: float
        # feePriorities: list[int]

        # # market
        # price: float
        # inversePrice: float
        # marketCap: float

    def checkIntegrity(self):
        if len(self.lastBlocks) != self.lastBlocks.maxlen:
            print("Last blocks deque does not have the correct length")
        if self.lastBlocks[-1].height != self.lastBlocks[0].height + self.lastBlocks.maxlen - 1:
            print("Last block height and first block height do not match")
        if self.blockHeight != self.lastBlocks[-1].height:
            print("Block height and last block height do not match")
        for i, block in enumerate(reversed(self.lastBlocks)):
            if block.height != self.blockHeight - i:
                print(f"Block height and last block height do not match at index {i}")
        

    def update(self, lastBlock: Block, initial=False) -> list[Tweet]:
        self.blockHeight = lastBlock.height

        if initial:
            self.lastBlocks.append(lastBlock)
            pickle.dump(self.lastBlocks, open("data/lastBlocks.pkl", "wb"))
            return
        
        print(f"Updating data with block {lastBlock.height}")

        message = ""

        # difficulty adjustment
        if lastBlock.height % 2016 == 0:
            if lastBlock.difficulty != self.lastBlocks[-1].difficulty:
                percentalChange = round((lastBlock.difficulty/self.lastBlocks[-1] - 1) * 100, 2)
                message += f"Difficulty adjusted: {percentalChange}%\n"
            else:
                message += f"Difficulty unchanged\n"

        # last 100 blocks summary
        if lastBlock.height % 100 == 0:
            message += f"Summary of last 100 #bitcoin blocks:\n"
            message += f"Total value transfer: {np.sum([block.value for block in self.lastBlocks])}\n"
            message += f"Average block size: {(np.mean([block.size for block in self.lastBlocks]) / 1e6)} MB\n"
            message += f"Median utxo value: {np.median(([block.utxoValues for block in self.lastBlocks]))}\n"

            # price changes
            relativePriceChange = lastBlock.price[0] / self.lastBlocks[0].price[0] - 1
            message += f"Price moved by: {relativePriceChange:.2%}\n"

            # largest utxo
            largestUtxo = max([np.max(block.utxoValues) for block in self.lastBlocks])
            message += f"Largest utxo: {largestUtxo:.2f} ₿\n"

            # plot
            utxos = []
            for block in self.lastBlocks:
                utxos.extend(block.utxoValues)
            utxoValuePlot(utxos)
            tweet(f"UTXO Value Distribution (Blocks: {self.lastBlocks[0].height} - {self.lastBlocks[-1].height})", "plots/tweet_img.png")
            
        # percentage supply reached next 0.01%
        if round(lastBlock.relativeSupply, 2) != round(self.lastBlocks[-1].relativeSupply, 2):
            message += f"Supply reached {lastBlock.relativeSupply:.3%}\n"
            message += f"Only {(1 - lastBlock.relativeSupply):.3%} left\n"

        self.lastBlocks.append(lastBlock)
        pickle.dump(self.lastBlocks, open("data/lastBlocks.pkl", "wb"))
        self.checkIntegrity()

        if message:
            return [Tweet(message, "plots/tweet_img.png")]
        
        return [Tweet(str(lastBlock))]

