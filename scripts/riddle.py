from mnemonic import Mnemonic
from itertools import combinations, chain
from collections import Counter
from itertools import product
from tqdm import tqdm
from multiprocessing import Pool
import math

mnemo = Mnemonic("english")
bip39_words = mnemo.wordlist

# Given list of letters
letters = [
    'p', 'q', 'n', 'i', 'e', 'o', 'e', 'u', 'o', 'e', 'h', 'e', 'i', 's',
    'f', 'p', 'p', 's', 'p', 'm', 'e', 'c', 's', 'a', 'c', 'a', 'o', 's',
    'o', 'h', 'e', 'g', 'n', 't', 'i', 'g', 'u', 'j', 'g', 'p', 'e', 'i',
    'a', 'f', 's', 's'
]


letter_frequency = Counter(letters)

# print(letter_frequency)

def can_form_word(word, available_letters):
    if len(word) > 4:
        return False
    letters_copy = available_letters.copy()
    for letter in word[:4]:
        if letter in letters_copy:
            letters_copy.remove(letter)
        else:
            return False
    return True

all_words = [word for word in bip39_words if can_form_word(word, letters)]
# print(len(all_words))
# input(len(bip39_words))
filtered_words = [word for word in all_words if 'j' not in word and 't' not in word and 'm' not in word and 'q' not in word]
words_without_q_and_t = [word for word in all_words if 't' not in word and 'q' not in word]
# filtered_words = [word for word in all_words if 't' not in word and 'q' not in word]

# print(len(filtered_words))

four_letter_words = [word for word in filtered_words if len(word) == 4]
three_letter_words = [word for word in filtered_words if len(word) == 3]

# print(len(four_letter_words))
# print(len(three_letter_words))

# sort words based on most common letters score
four_letter_words.sort(key=lambda word: sum(letters.count(letter) for letter in word), reverse=True)
three_letter_words.sort(key=lambda word: sum(letters.count(letter) for letter in word), reverse=True)



wordsWithJ = [word for word in words_without_q_and_t if 'j' in word]
wordsWithM = [word for word in words_without_q_and_t if 'm' in word]


initial_combinations = list(product(wordsWithJ, wordsWithM))
initial_combinations = [tuple(set(comb)) for comb in initial_combinations]
initial_combinations_cleaned = []

for comb in initial_combinations:
    letterList = list(''.join(word for word in comb))
    if letterList.count('j') == 1 and letterList.count('m') == 1:
        initial_combinations_cleaned.append(comb)

# remove duplicates
initial_combinations_cleaned = list(set(initial_combinations_cleaned))


def process_combinations(chunk):
    i = 0
    for init_comb in chunk:
        print(init_comb)
        four_letter_words_in_comb = len([word for word in init_comb if len(word) == 4])
        three_letter_words_in_comb = len([word for word in init_comb if len(word) == 3])
        
        for four_comb in combinations(four_letter_words, 9 - four_letter_words_in_comb):
            for three_comb in combinations(three_letter_words, 2 - three_letter_words_in_comb):

                combined_words = ["quit"] + list(init_comb) + list(four_comb) + list(three_comb)
                combined_letters = ''.join(combined_words)
                if Counter(combined_letters) == letter_frequency:
                    # check if comb already in results.txt
                    with open('result.txt', 'r') as f:
                        results = f.readlines()
                    results = [result.strip() for result in results]
                    if str(combined_words) in results:
                        continue
                    combined_words = sorted(combined_words)
                    print(f"found {len(results)+1} solutions")
                    print(combined_words)
                    
                    with open('result.txt', 'a') as f:
                        f.write(str(combined_words) + "\n")
                i += 4
                if i % 1000000 == 0:
                    print(i//1e6, "million combinations checked")

        print(f"finished chunk {chunk}")

def find_valid_combination_multi():
    n_cores = 4
    chunk_size = math.ceil(len(initial_combinations_cleaned) / n_cores)
    chunks = [initial_combinations_cleaned[i:i+chunk_size] for i in range(0, len(initial_combinations_cleaned), chunk_size)]
    with Pool(processes=n_cores) as pool:
        results = pool.map(process_combinations, chunks)
        
    return results
    

if __name__ == '__main__':
    valid_combination = find_valid_combination_multi()
    print(valid_combination)