import matplotlib.pyplot as plt
from bitcoin import Bitcoin
import pickle
from typing import List
import json

bitcoin = Bitcoin()

with open('data/btc_data.json', 'r') as f:
    priceByTimestamp = json.load(f)

class Block ():
    def __init__(self, block: dict):
        self.height = block['height']
        self.version = block['version']
        self.versionHex = block['versionHex']
        self.merkleroot = block['merkleroot']
        self.time = block['time']
        self.mediantime = block['mediantime']*1000
        self.nonce = block['nonce']
        self.bits = block['bits']
        self.size = block['size']
        self.time = block['time']
        self.txs = block['nTx']
        self.value = block['value']
        self.weight = block['weight']
        self.difficulty = block['difficulty']
        self.bits = block['bits']
        self.nonce = block['nonce']
        self.hash = block['hash']
        self.chainwork = block['chainwork']
        self.priceUsd = self.getPriceUsdAtTimestamp()

    def getPriceUsdAtTimestamp(self):
        closestTimestamp = min(priceByTimestamp, key=lambda x: abs(int(x) - self.mediantime))
        return int(priceByTimestamp[closestTimestamp])
    
    def __repr__(self) -> str:
        return f"Block {self.height} - {self.difficulty} - {self.priceUsd}"


def getBlockData(bitcoin: Bitcoin, num_blocks, stepSize=1):

    blocks: List[Block] = []
    for block in bitcoin.iterateBlocks(0, num_blocks, stepSize):
        blocks.append(Block(block))
        print(blocks[-1])

    for block in blocks:
        block.priceUsd = block.getPriceUsdAtTimestamp()

    with open(f'plotdata/blocks_stepSize={stepSize}.pkl', 'wb') as f:
        pickle.dump(blocks, f) 

    # load data
    # with open(f'plotdata/blocks_stepSize={stepSize}.pkl', 'rb') as f:
    #     blocks = pickle.load(f)

    y = [block.chainwork for block in blocks]

    plt.plot([block.height for block in blocks], y, marker='.')
    plt.grid(True)
    plt.yscale('log')
    plt.show()



if __name__ == "__main__":
    getBlockData(bitcoin, 847_000, 1)