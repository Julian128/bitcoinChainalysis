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
        self.blockHeight = lastBlock.height

        if len(self.lastBlocks) == 0:
            self.lastBlocks.append(lastBlock)
            return
        
        message = f"Block #{lastBlock.height} mined\n"

        if lastBlock.value > 3 * np.mean([block.value for block in self.lastBlocks]):
            message += f"Value transferred: {int(lastBlock.value)} BTC\n"

        if lastBlock.height % 2016 == 0:
            if lastBlock.difficulty != self.lastBlocks[-1].difficulty:
                percentalChange = round((lastBlock.difficulty/self.blocks[-1] - 1) * 100, 2)
                message += f"Difficulty adjusted: {percentalChange}%\n"
            else:
                message += f"Difficulty unchanged\n"

        if lastBlock.size < 0.5 * np.mean([block.size for block in self.lastBlocks]):
            message += f"Block size small: {lastBlock.size}\n"

        if lastBlock.size > 1.5 * np.mean([block.size for block in self.lastBlocks]):
            message += f"Block size large: {lastBlock.size}\n"

        # percentage supply
        # sizeOnDisk when not pruned
        # utxo set size
        # interesting utxos
        # public nodes
        # mempool size
        # fee inflow

        self.lastBlocks.append(lastBlock)
        self.message = message

    def resetMessage(self):
        self.message = ""


