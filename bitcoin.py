from bitcoinrpc.authproxy import AuthServiceProxy
import time
import configparser
import pycoingecko
import numpy as np
class Bitcoin():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("bitcoin.conf")
        self.user = self.config['settings']['user']
        self.password = self.config['settings']['password']
        self.host = self.config['settings']['host']
        self.port = self.config['settings']['port']

        self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}", timeout=300)

        self.printInfo()

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
                print(f"Exception in RPC call: {e}")
                time.sleep(5)
                self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}")

    def getBlockCount(self):
        return self.rpc("getblockcount")

    def getBlockFromHeight(self, blockHeight: int):
        blockHash = self.rpc("getblockhash", blockHeight)
        block = self.rpc("getblock", blockHash, 2)
        block["value"] = self.getBlockValue(block)
        return block

    def getLatestBlock(self):
        return self.getBlockFromHeight(self.getBlockCount())

    def iterateBlocks(self, start=0, stop=0, stepSize=1):
        for i in range(start, stop, stepSize):
            block = self.getBlockFromHeight(i)
            block["value"] = self.getBlockValue(block)  
            yield block

    def iterateLatestBlocks(self, nBlocks=100):
        start = self.getBlockCount()
        for i in range(nBlocks):
            block = self.getBlockFromHeight(start-i)
            block["value"] = self.getBlockValue(block)  
            yield block
    
    def getBlockValue(self, block):
        return sum([sum(out['value'] for out in tx['vout']) for tx in block['tx'][1:]])

    def getBlockUtxoValues(self, block):
        utxoValues = []
        for tx in block["tx"]:
            if len(tx["vout"]) > 2:
                continue
            for output in tx["vout"]:
                utxoValues.append(output["value"])
        return np.array(utxoValues)
    
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

    def findTx(self, value: int, epsilon=0.001):
        height = self.getBlockCount()
        for block in bitcoin.iterateBlocks(height, height-100, -1):
            for tx in block["tx"]:
                for output in tx["vout"]:
                    if value - epsilon < output["value"] < value + epsilon:
                        return output
                    
    def findUtxoOfAddress(self, address: str):
        txs = []
        height = self.getBlockCount()
        for block in bitcoin.iterateBlocks(height, height-100, -1):
            for tx in block["tx"]:
                for output in tx["vout"]:
                    try:
                        if address == output["scriptPubKey"]["address"]:
                            txs.append(tx)
                            print(txs)
                            input()
                    except:
                        pass

    def current_block_height(self):
        blockHeight = self.runCli(f"bitcoin-cli getblockcount")
        return blockHeight
    
    def getFeePriorities(self, nHighPriority=1500, nMediumPriority=2000, nLowPriority=3000) -> list[int]:
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

            priorities = [int(np.median(feeRates[:nLowPriority])), int(np.median(feeRates[:nMediumPriority])), int(np.median(feeRates[:nHighPriority]))]
            return priorities

    def getLeadingZeroesInBinary(self, block):
        binaryHash = bin(int(block["hash"], 16))[2:].zfill(256)
        leadingZeros = binaryHash.index("1")
        return leadingZeros
    
    def getPrice(self):
        coinGecko = pycoingecko.CoinGeckoAPI()
        btc_data = coinGecko.get_coin_market_chart_by_id('bitcoin', 'usd', '1minute')
        price = [data[1] for data in btc_data['prices']][-1]
        inversePrice = 1 / price

        return int(price), int(inversePrice*1e8)

    def getSupply(self):
        return self.rpc("gettxoutsetinfo")["total_amount"]


if __name__ == "__main__":
    bitcoin = Bitcoin()
    # print(bitcoin.getSupply())
    bitcoin.getBlockFromHeight(848800)
