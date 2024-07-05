import json
import numpy as np


with open('data/priceByTimestamp.json', 'r') as f:
    priceByTimestamp = json.load(f)


class Block:
    def __init__(self, block: dict, value: float, utxoValues: list[float], price: tuple[int], feePriorities: tuple[int]):
        self.height = block['height']
        self.version = block['version']
        self.versionHex = block['versionHex']
        self.merkleroot = block['merkleroot']
        self.time = block['time']
        self.mediantime = block['mediantime']*1000
        self.nonce = block['nonce']
        self.bits = block['bits']
        self.size = block['size']  # bytes
        self.txs = block['nTx']
        self.weight = block['weight']
        self.difficulty = block['difficulty']
        self.hash = block['hash']
        self.chainwork = block['chainwork']

        self.utxoValues = np.array(utxoValues)
        self.value = value
        self.price = price
        self.relativeSupply = self.getSupply()
        self.feePriorities = feePriorities

        self.subsidy = 0
        self.fees = 0

    def getPriceUsdAtTimestamp(self):
        closestTimestamp = min(priceByTimestamp, key=lambda x: abs(int(x) - self.mediantime))
        return int(priceByTimestamp[closestTimestamp])
    
    def __repr__(self) -> str:
        string = ""
        string += f"#Bitcoin block #{self.height} mined\n"
        string += f"{(self.value):.0f} ₿ transferred\n"
        string += f"{self.txs} txs ({self.size/1e6:.2f} MB)\n"
        string += f"median utxo value: {round(int(np.median(self.utxoValues)*1e8), -3)}\n"
        string += f"{self.relativeSupply:.3%} circulating\n"
        string += f"$1 = {self.price[1]} sats\n"
        string += f"fees: {self.feePriorities}"
        return string
        
    def getSupply(self):
        # TODO: replace with RPC call to get supply from UTXO set
        subsidy = 5_000_000_000 # 50 BTC
        subsidyInterval = 210000
        totalSupply = 0
        summationHeight = 0

        for _ in range(self.height):
            totalSupply += subsidy
            summationHeight += 1
            if summationHeight % subsidyInterval == 0:
                subsidy = subsidy >> 1

        return round(totalSupply / 21_000_000 / 1e8, 5)
    

