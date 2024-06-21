import pickle

from bitcoin import Bitcoin
from block import Block, BlockLight


bitcoin = Bitcoin()


def indexBlocks():
    batch_size = 10_000
    for i in range(210_000, 840_000, batch_size):
        blocks: list[BlockLight] = []
        for block in bitcoin.iterateBlocks(i, i+batch_size):
            print(block['height'])
            blocks.append(BlockLight(block))

        for block in blocks:
            block.priceUsd = block.getPriceUsdAtTimestamp()

        with open(f'blocksLight/blocks{i}_{i+batch_size}.pkl', 'wb') as f:
            pickle.dump(blocks, f)


if __name__ == "__main__":
    indexBlocks()