from bitcoinrpc.authproxy import AuthServiceProxy
import time
import configparser
import pycoingecko
import numpy as np
import tqdm
import pickle
import os

from bitcoinData import BitcoinData
from block import Block
from scripts.tweeter import Tweet
from plots import utxoValuePlot


class Bitcoin():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("bitcoin.conf")
        self.user = self.config['settings']['user']
        self.password = self.config['settings']['password']
        self.host = self.config['settings']['host']
        self.port = self.config['settings']['port']

        self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}", timeout=30)

        self.printInfo()
        self.data = BitcoinData()

    def initData(self):
        if (os.path.exists("data/lastBlocks.pkl")):
            self.data.lastBlocks = pickle.load(open("data/lastBlocks.pkl", "rb"))
            self.data.lastBlocks.pop()
            self.data.blockHeight = self.data.lastBlocks[-1].height

        currentHeight = self.getBlockCount()

        if (currentHeight - self.data.blockHeight) > self.data.lastBlocks.maxlen:
            self.data.lastBlocks.clear()
            self.data.blockHeight = currentHeight - self.data.lastBlocks.maxlen

        if currentHeight > self.data.blockHeight:
            for block in tqdm.tqdm(self.iterateBlocks(self.data.blockHeight+1, currentHeight), desc="Initializing data", total=currentHeight - self.data.blockHeight - 1):
                self.data.update(block, initial=True)

    def updateData(self) -> list[Tweet]:
        blockHeight = self.getBlockCount()
        messages = []
        if blockHeight > self.data.blockHeight:
            blocksToUpdate = range(self.data.blockHeight + 1, blockHeight + 1)
            for height in blocksToUpdate:
                messages.extend(self.data.update(self.getBlockFromHeight(height)))

        return messages

    def getNewBlockMessage(self):
        message = self.data.message
        self.data.resetMessage()
        return message

    def printInfo(self):
            print("Connecting to Bitcoin Core...\n############################################################")
            info = self.rpc("getblockchaininfo")
            print(f"Chain: {info['chain']}")
            print(f"Block height: {info['blocks']}")
            print(f"Chainwork: {info['chainwork']}")
            print(f"Pruned: {info['pruned']}")
            print(f"Size on disk in GB: {info['size_on_disk'] / 1024**3}")
            print(f"Block download progress: {info['blocks'] / info['headers']}")
            # print(f"Verification progress: {info['verificationprogress']}")
            # print(self.getFeePriorities())
            print(f"Price: {self.getPrice()}")
            print("############################################################")

    def rpc(self, method: str, *args):
        for _ in range(3):
            try:
                return self.rpcConnection.__getattr__(method)(*args)
            except Exception as e:
                if str(e).startswith("-5"):
                    return
                print(f"Exception in RPC call: {e}")
                time.sleep(2)
                self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}")

    def getBlockCount(self):
        return self.rpc("getblockcount")

    def getBlockFromHeight(self, blockHeight: int) -> Block:
        blockHash = self.rpc("getblockhash", blockHeight)
        block = self.rpc("getblock", blockHash, 2)
        if block:
            block = Block(block, self.getBlockValue(block), self.getBlockUtxoValues(block), self.getPrice(), self.getFeePriorities())
            return block

        raise("Block not found")

    def getLatestBlock(self):
        return self.getBlockFromHeight(self.getBlockCount())

    def iterateBlocks(self, start=0, stop=0, stepSize=1):
        if stop == 0:
            stop = self.getBlockCount()
        for i in range(start, stop, stepSize):
            block = self.getBlockFromHeight(i)
            yield block

    def iterateLatestBlocks(self, nBlocks=100):
        start = self.getBlockCount()
        for i in range(nBlocks):
            block = self.getBlockFromHeight(start-i)
            yield block
    
    def getBlockValue(self, block: Block):
        return sum([sum(out['value'] for out in tx['vout']) for tx in block['tx'][1:]])

    def getBlockUtxoValues(self, block) -> list[int]:
        utxoValues = []
        for tx in block["tx"]:
            if len(tx["vout"]) > 2:
                continue
            for output in tx["vout"]:
                utxoValues.append(float(output["value"]))
        return utxoValues
    
    def getUtxosFromBlock(self, block):
        utxos = []
        for tx in block["tx"]:
            for output in tx["vout"]:
                utxos.append(output)
        return utxos
    
    def getInputsFromBlock(self, block):
        inputs = []
        for tx in block["tx"]:
            for input in tx["vin"]:
                inputs.append(input)
        return inputs

    def findTxByValue(self, value: int, epsilon=0.001):
        height = self.getBlockCount()
        for block in bitcoin.iterateBlocks(height, height-100, -1):
            for tx in block["tx"]:
                for output in tx["vout"]:
                    if value - epsilon < output["value"] < value + epsilon:
                        return output
                    
    def getFeePriorities(self, nHighPriority=1250, nMediumPriority=1750, nLowPriority=2500) -> tuple[int]:
        priorities = []
        while True:
            mempoolTxIds = self.rpc("getrawmempool")
            feeRates = []

            for txid in mempoolTxIds[:nLowPriority+100]:
                try:
                    tx = self.rpc("getmempoolentry", txid)
                    feeRates.append(float(tx["fees"]["base"] / tx["vsize"]) * 1e8)
                except:
                    pass

            priorities = tuple([int(np.median(feeRates[:nLowPriority])), int(np.median(feeRates[:nMediumPriority])), int(np.median(feeRates[:nHighPriority]))])
            return priorities

    def getLeadingZeroesInBinary(self, block):
        binaryHash = bin(int(block["hash"], 16))[2:].zfill(256)
        leadingZeros = binaryHash.index("1")
        return leadingZeros
    
    def getPrice(self) -> tuple[int, int]:
        coinGecko = pycoingecko.CoinGeckoAPI()
        btc_data = coinGecko.get_coin_market_chart_by_id('bitcoin', 'usd', '1minute')
        price = [data[1] for data in btc_data['prices']][-1]
        inversePrice = 1 / price

        return int(price), int(inversePrice*1e8)

    def getBlockFees(self, block):
        fees = 0
        for tx in block["tx"]:
            fees += sum([input["value"] for input in tx["vin"]]) - sum([output["value"] for output in tx["vout"]])
        return fees

    def getTransaction(self, txid):
        return self.rpc("gettransaction", txid)


if __name__ == "__main__":
    bitcoin = Bitcoin()


