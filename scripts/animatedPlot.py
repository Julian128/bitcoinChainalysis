import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pickle
from matplotlib.image import imread
from block import Block
from typing import List
from bitcoin import Bitcoin
import math

bitcoin = Bitcoin()

def getFigAx():
    fig, ax = plt.subplots()
    # ax.set_yscale('log')
    backgroundColor = 'black'
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors=backgroundColor)
    ax.tick_params(axis='y', colors=backgroundColor)
    ax.spines['bottom'].set_color(backgroundColor)
    ax.spines['top'].set_color('purple')
    ax.spines['right'].set_color(backgroundColor)
    ax.spines['left'].set_color(backgroundColor)    
    ax.xaxis.label.set_color(backgroundColor)
    ax.yaxis.label.set_color(backgroundColor)
    ax.title.set_color(backgroundColor)
    ax.set_xlim(left=0, right=840000)
    zone_boundaries = [0, 210000, 420000, 630000, 840000]
    roman_numerals = ['I', 'II', 'III', 'IV']

    color2 = 'green'
    ax2 = ax.twinx()
    ax2.set_yscale('log')
    ax2.set_facecolor('black')
    ax2.tick_params(axis='x', colors=color2)
    ax2.tick_params(axis='y', colors=color2)
    ax2.spines['top'].set_color('purple')
    ax2.spines['bottom'].set_color(backgroundColor)
    ax2.spines['right'].set_color(color2)
    ax2.spines['left'].set_color(backgroundColor)
    ax2.xaxis.label.set_color(color2)
    ax2.yaxis.label.set_color(color2)
    for i, boundary in enumerate(zone_boundaries[:-1]):
        next_boundary = zone_boundaries[i+1]
        center = (boundary + next_boundary) / 2
        ax2.axvline(x=boundary, color='purple', linestyle='--') if boundary != 0 else None
        ax2.text(center, ax2.get_ylim()[0] + (ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 10, roman_numerals[i],
                horizontalalignment='center', color='purple', fontsize=12)

    return fig, ax, ax2

def getFigAxBlackWhite():

    backgroundColor = 'black'
    frontColor = 'white'
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    ax.set_facecolor(frontColor)
    fig.patch.set_facecolor(frontColor)
    ax.tick_params(axis='x', colors=backgroundColor)
    ax.tick_params(axis='y', colors=backgroundColor)
    ax.spines['bottom'].set_color(backgroundColor)
    ax.spines['top'].set_color(backgroundColor)
    ax.spines['right'].set_color(backgroundColor)
    ax.spines['left'].set_color(backgroundColor)    
    ax.xaxis.label.set_color(backgroundColor)
    ax.yaxis.label.set_color(backgroundColor)
    ax.title.set_color(backgroundColor)

    return fig, ax

def getMovingAverage(y, window_size):
    moving_averages = [0 for _ in range(window_size)]
    for i in range(len(y) - window_size):
        window = y[i:i+window_size]
        window_average = sum(window) / window_size
        moving_averages.append(window_average)
    return np.array(moving_averages)


def animatedPlot():
    stepSize = 1000
    # import pickled data
    with open(f'plotdata/blocks_stepSize={stepSize}.pkl', 'rb') as f:
        blocks: List[Block] = pickle.load(f)

    y1 = [int(block.chainwork, 16) for block in blocks]
    y1 = [math.log2(y) for y in y1]
    
    y2 = [block.difficulty for block in blocks]
    x = [block.height for block in blocks]

    fig, ax, ax2 = getFigAx()

    ax.axes.xaxis.set_label_text('block height')

    ax.axes.yaxis.set_label_text('chainwork (log2)', fontsize=12)
    ax2.axes.yaxis.set_label_text('difficulty', fontsize=12)

    line, = ax.plot(x, y1, color="blue")
    line2, = ax2.plot(x, y2, color='green')

    # add text to image at bottom right
    plt.text(0.17, 0.95, '@staccSats', color="blue", fontsize=10, ha='right', va='bottom', alpha=1, transform=ax.transAxes)

    # plt.legend([line, line2], ['difficulty', 'price (usd)'], loc='upper left')

    # plt.show()
    # return
    def update(num, x, y1, y2, line):
        line.set_data(x[:num], y1[:num])
        line2.set_data(x[:num], y2[:num])
        return line, line2

    ani = animation.FuncAnimation(fig, update, len(x), fargs=[x, y1, y2, line],
                                interval=1, blit=True, repeat=False)


    # ani.save('plots/plot.mp4', writer='ffmpeg', fps=60)
    plt.show()


def utxoValuePlot():

    # values = []
    # blockheight = bitcoin.getBlockHeight()
    # for block in bitcoin.iterateBlocks(blockheight-10, blockheight):
    #     values.extend(bitcoin.getBlockUtxoValues(block))

    # # pickle values
    # with open('plotdata/utxo_values.pkl', 'wb') as f:
    #     pickle.dump(values, f)

    # load values
    with open('plotdata/utxo_values.pkl', 'rb') as f:
        values = pickle.load(f)
    
    values = [v for v in values if v > 0]

    values.sort()
    print(values[:10])
    print(len([v for v in values if v < 0.00100_000]) / len(values))
    print(len([v for v in values if v < 0.00010_000]) / len(values))
    print(len([v for v in values if v < 0.00001_000]) / len(values))
    print(len([v for v in values if v < 0.00000_100]) / len(values))

    # number of values between 0 and 0.005 btc

    # plot histogram of utxo values between 0 and 1 btc
    fig, ax = getFigAxBlackWhite()
    plt.hist(values, bins=50, range=(0, 0.005), color="black")
    ax.set_xlabel('UTXO Value (BTC)')
    # plt.ylabel('Count')
    ax.set_yscale('log')
    plt.title("UTXO Value Distribution (last 10 blocks)")
    plt.savefig('plots/utxo_values.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    # animatedPlot()
    utxoValuePlot()