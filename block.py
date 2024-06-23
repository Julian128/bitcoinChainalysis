import json


with open('data/priceByTimestamp.json', 'r') as f:
    priceByTimestamp = json.load(f)

class Block:
    def __init__(self, block: dict, value: float, feePriorities: list[int]):
        self.height = block['height']
        self.transactions = block['tx']
        self.version = block['version']
        self.versionHex = block['versionHex']
        self.merkleroot = block['merkleroot']
        self.time = block['time']
        self.mediantime = block['mediantime']*1000
        self.nonce = block['nonce']
        self.bits = block['bits']
        self.size = block['size']
        self.txs = block['nTx']
        self.weight = block['weight']
        self.difficulty = block['difficulty']
        self.hash = block['hash']
        self.chainwork = block['chainwork']

        self.value = value
        self.feePriorities = feePriorities
        self.priceUsd = self.getPriceUsdAtTimestamp()

        self.subsidy = 0
        self.fees = 0

    def getPriceUsdAtTimestamp(self):
        closestTimestamp = min(priceByTimestamp, key=lambda x: abs(int(x) - self.mediantime))
        return int(priceByTimestamp[closestTimestamp])
    
    def __repr__(self) -> str:
        return f"Block {self.height} - {self.difficulty} - {self.priceUsd}"


class BlockLight:
    def __init__(self, block: dict):
        self.height = block['height']
        self.merkleroot = block['merkleroot']
        self.time = block['time']
        self.mediantime = block['mediantime']*1000
        self.nonce = block['nonce']
        self.bits = block['bits']
        self.size = block['size']
        self.txs = block['nTx']
        self.value = block['value']
        self.weight = block['weight']
        self.difficulty = block['difficulty']
        self.hash = block['hash']
        self.chainwork = block['chainwork']
        self.priceUsd = self.getPriceUsdAtTimestamp()

    def getPriceUsdAtTimestamp(self):
        closestTimestamp = min(priceByTimestamp, key=lambda x: abs(int(x) - self.mediantime))
        return int(priceByTimestamp[closestTimestamp])
    
    def __repr__(self) -> str:
        return f"Block {self.height} - {self.difficulty} - {self.priceUsd}"


