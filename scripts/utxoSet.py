from __future__ import annotations
import pickle
from bitcoin import Bitcoin
from block import Block
import matplotlib.pyplot as plt
import numpy as np


class Utxo:
    def __init__(self, txid, vout, value, inputs: list[Utxo]=[]):
        self.txid = txid
        self.vout = vout
        self.value = value
        self.inputs: list[Utxo] = inputs

    def __str__(self):
        return f"Utxo(txid={self.txid}, vout={self.vout}, value={self.value}, inputs={self.inputs})"

    def __repr__(self):
        return self.__str__()

bitcoin = Bitcoin()

utxoSetByTxId = {}
utxoSetSizeByBlockHeight = {}



with open(f'blocks/blocks{0}_{100000}.pkl', 'rb') as f:
    blocks = pickle.load(f)

for block in blocks[:100000]:
    for tx in block.transactions:
        for output in tx["vout"]:
            inputs = []
            for txInput in tx["vin"]:
                for utxo in utxoSetByTxId.values():
                    if "coinbase" in txInput:
                        continue
                    if utxo.txid == txInput["txid"] and utxo.vout == txInput["vout"]:
                        inputs.append(utxo)
                        break

            utxoSetByTxId[(tx["txid"], output["n"])] = Utxo(tx["txid"], output["n"], output["value"], inputs)

            # remove spent outputs
            for txInput in tx["vin"]:
                if "coinbase" in txInput:
                    continue
                if (txInput["txid"], txInput["vout"]) in utxoSetByTxId:
                    del utxoSetByTxId[(txInput["txid"], txInput["vout"])]


            utxoSetSizeByBlockHeight[block.height] = len(utxoSetByTxId)
            # print(utxoSet[-1])
            # input()

print(len(utxoSetByTxId))
print(sum(utxo.value for utxo in utxoSetByTxId.values()))

# histogram of utxo values

bins = np.logspace(-8, 4, base=10)
print(bins)

plt.hist([utxo.value for utxo in utxoSetByTxId.values()], bins=bins)
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Utxo value')
plt.ylabel('Count')
plt.title('Histogram of utxo values')
plt.show()