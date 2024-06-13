from bitcoinrpc.authproxy import AuthServiceProxy
import time
import numpy as np
import configparser


class Bitcoin():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("bitcoin.conf")
        self.user = self.config['settings']['user']
        self.password = self.config['settings']['password']
        self.host = self.config['settings']['host']
        self.port = self.config['settings']['port']

        self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}")

    def getBlockCount(self):
        return self.rpcConnection.getblockcount()

    def getBlockFromHeight(self, blockHeight: int):
        blockHash = self.rpcConnection.getblockhash(blockHeight)
        return self.rpcConnection.getblock(blockHash, 2)

    def iterateBlocks(self, start=0, stop=0, stepSize=1):
        i = start
        stop = stop
        while i < stop:
            try:
                block = self.getBlockFromHeight(i)
                block["value"] = self.getBlockValue(block)  
                yield block
                i += stepSize
            except Exception as e:
                print(e)
                self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}")
                time.sleep(10)

    def iterateLatestBlocks(self, nBlocks=100):
        start = self.getBlockCount()
        for i in range(nBlocks):
            try:
                block = self.getBlockFromHeight(start-i)
                block["value"] = self.getBlockValue(block)  
                yield block
            except Exception as e:
                print(e)
                self.rpcConnection = AuthServiceProxy(f"http://{self.user}:{self.password}@{self.host}:{self.port}")
                time.sleep(10)
    
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
    
    def getFeePriorities(self, nHighPriority=1000, nMediumPriority=2000, nLowPriority=4000) -> list[int]:
        mempoolTxIds = self.rpcConnection.getrawmempool()
        feeRates = []

        for txid in mempoolTxIds[:nLowPriority+100]:
            tx = self.rpcConnection.getmempoolentry(txid)
            try:
                feeRates.append(float(tx["fees"]["base"] / tx["vsize"]) * 1e8)
            except:
                pass
        
        priorities = [int(np.median(feeRates[:nHighPriority])), int(np.median(feeRates[:nMediumPriority])), int(np.median(feeRates[:nLowPriority]))]

        # print(f"High priority: {priorities[0]} sats/vbyte")
        # print(f"Medium priority: {priorities[1]} sats/vbyte")
        # print(f"Low priority: {priorities[2]} sats/vbyte")

        return priorities

if __name__ == "__main__":
    bitcoin = Bitcoin()
    print("Connected to Bitcoin Core")
    print(f"Block height: {bitcoin.getBlockCount()}")
    print(bitcoin.getFeePriorities())




