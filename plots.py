import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pickle
from matplotlib.image import imread
from block import Block
# from bitcoin import Bitcoin
import math

# bitcoin = Bitcoin()

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

    return fig, ax

def getFigAxBlackWhite():

    backgroundColor = 'black'
    frontColor = 'white'
    fig, ax = plt.subplots()
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


def utxoValuePlot(utxos: list[float]):
    utxos = [float(v)*1e8 for v in utxos if v > 0]
    utxos.sort()

    fig, ax = getFigAxBlackWhite()
    plt.hist(utxos, bins=np.logspace(2, 11, 20), color="black")
    ax.set_xlabel('UTXO Value (sats)')
    ax.set_xscale('log')
    ax.set_xlim(left=1e2, right=1e11)
    # ax.set_yscale('log')
    # plt.title("UTXO Value Distribution (last 10 blocks)")
    plt.savefig('plots/tweet_img.png', dpi=300)
    # plt.show()


if __name__ == "__main__":
    with open('plotdata/utxo_values.pkl', 'rb') as f:
        utxos = pickle.load(f)
    utxoValuePlot(utxos)