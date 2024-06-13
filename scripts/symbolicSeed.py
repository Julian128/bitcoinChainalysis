import random
import matplotlib.pyplot as plt
from mnemonic import Mnemonic

def plot_lines(ax, bit_string, word):
    # Helper function to draw lines and shapes
    def draw_line(start, end, color='black', linestyle='-'):
        ax.plot(start, end, color=color, linestyle=linestyle, linewidth=2)

    # Define positions for squares and central line
    squares = {'first': {'left_bottom': (1, 1), 'right_top': (4, 4)},
               'second': {'left_bottom': (4, 1), 'right_top': (7, 4)}}

    # Mapping bit to its corresponding drawing action
    actions = [
        lambda: draw_line([squares['first']['left_bottom'][0], squares['first']['right_top'][0]], [squares['first']['right_top'][1], squares['first']['right_top'][1]]),  # Top line first square
        lambda: draw_line([squares['first']['right_top'][0], squares['first']['right_top'][0]], [squares['first']['left_bottom'][1], squares['first']['right_top'][1]]),  # Right line first square
        lambda: draw_line([squares['first']['left_bottom'][0], squares['first']['right_top'][0]], [squares['first']['left_bottom'][1], squares['first']['left_bottom'][1]]),  # Bottom line first square
        lambda: draw_line([squares['first']['left_bottom'][0], squares['first']['left_bottom'][0]], [squares['first']['left_bottom'][1], squares['first']['right_top'][1]]),  # Left line first square
        lambda: draw_line([squares['first']['left_bottom'][0], squares['first']['right_top'][0]], [squares['first']['left_bottom'][1], squares['first']['right_top'][1]]),  # Diagonal bottom-left to top-right first square
        lambda: draw_line([squares['first']['left_bottom'][0], squares['first']['right_top'][0]], [squares['first']['right_top'][1], squares['first']['left_bottom'][1]]),  # Diagonal top-left to bottom-right first square
        lambda: draw_line([squares['second']['left_bottom'][0], squares['second']['right_top'][0]], [squares['second']['right_top'][1], squares['second']['right_top'][1]]),  # Top line second square
        lambda: draw_line([squares['second']['right_top'][0], squares['second']['right_top'][0]], [squares['second']['left_bottom'][1], squares['second']['right_top'][1]]),  # Right line second square
        lambda: draw_line([squares['second']['left_bottom'][0], squares['second']['right_top'][0]], [squares['second']['left_bottom'][1], squares['second']['left_bottom'][1]]),  # Bottom line second square
        lambda: draw_line([squares['second']['left_bottom'][0], squares['second']['right_top'][0]], [squares['second']['left_bottom'][1], squares['second']['right_top'][1]]),  # Diagonal bottom-left to top-right second square
        lambda: draw_line([squares['second']['left_bottom'][0], squares['second']['right_top'][0]], [squares['second']['right_top'][1], squares['second']['left_bottom'][1]]),  # Diagonal top-left to bottom-right second square
    ]

    ax.set(xlim=(0, 9), ylim=(0, 5))
    ax.axis('off')

    for i, bit in enumerate(bit_string):
        if bit == '1':
            actions[i]()

    ax.text(4.5, 2.5, word, fontsize=12, ha='center', va='center')

# Create a large figure to hold all subplots
fig, axs = plt.subplots(6, 4, figsize=(20, 15))

mnemo = Mnemonic("english")
words = mnemo.wordlist
# transfrom each word to its corresponding 11-bit binary representation
seedphrase = (format(mnemo.wordlist.index(word), '011b') for word in words)

# Generate 24 random 11-bit sequences as strings and plot each
for i in range(24):
    # bit_string = ''.join(random.choice(['0', '1']) for _ in range(11))
    bit_string = next(seedphrase)
    word = words[int(bit_string, 2)]
    plot_lines(axs[i // 4, i % 4], bit_string, word)

plt.tight_layout()
plt.show()
