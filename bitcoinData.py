import numpy as np
from collections import deque

from block import Block


class BitcoinData:
    
    # chainstate
    lastBlocks: deque[Block] = deque(maxlen=100)
    blockHeight: int = 0
    # supply: float
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

    message: str = ""


    def update(self, lastBlock: Block):
        # print(f"adding block {lastBlock.height}")
        self.blockHeight = lastBlock.height
        self.message = f"Block #{lastBlock.height} mined\n"

        if len(self.lastBlocks) == 0:
            self.lastBlocks.append(lastBlock)
            return
        

        if lastBlock.value > 4 * np.mean([block.value for block in self.lastBlocks]):
            self.message += f"Value transferred: {int(lastBlock.value)} BTC\n"

        if lastBlock.height % 2016 == 0:
            if lastBlock.difficulty != self.lastBlocks[-1].difficulty:
                percentalChange = round((lastBlock.difficulty/self.blocks[-1] - 1) * 100, 2)
                self.message += f"Difficulty adjusted: {percentalChange}%\n"
            else:
                self.message += f"Difficulty unchanged\n"

        if lastBlock.size < 0.5 * np.mean([block.size for block in self.lastBlocks]):
            self.message += f"Block size small: {lastBlock.size}\n"

        if lastBlock.size > 1.5 * np.mean([block.size for block in self.lastBlocks]):
            self.message += f"Block size large: {lastBlock.size}\n"

        if lastBlock.feePriorities[0] > 2 * np.mean([block.feePriorities[1] for block in self.lastBlocks]):
            self.message += f"Higher fees: {lastBlock.feePriorities}\n"
    
        if lastBlock.feePriorities[0] < 0.5 * np.mean([block.feePriorities[1] for block in self.lastBlocks]):
            self.message += f"Lower fees: {lastBlock.feePriorities}\n"

        if len(self.lastBlocks) > self.lastBlocks.maxlen:
            self.lastBlocks.pop(0)
        self.lastBlocks.append(lastBlock)

    def resetMessage(self):
        self.message = ""


