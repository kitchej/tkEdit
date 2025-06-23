import sys
import os
import time

from Levenshtein import distance


def sort_key(x):
    return x[1], (x[2]) * -1


def similarity(str1, str2):
    str1_len = len(str1)
    str2_len = len(str2)
    score = 0

    if str1_len < str2_len:
        str1 = f"{str1}{' ' * (str2_len - str1_len)}"
    elif str1_len > str2_len:
        str2 = f"{str2}{' ' * (str1_len - str2_len)}"

    for k, (i, j) in enumerate(zip(str1, str2)):
        if i == j:
            score += 2
        elif k < (len(str2) - 1) and str2[k + 1] == i:
            score += 1
        elif k > 0 and str2[k - 1] == i:
            score += 1

    return score - abs(str1_len - str2_len)


def get_spelling_suggest(word):
    suggestions = []
    for possible_word in WORD_LIST:
        # possible_word = possible_word.lower()
        if abs(len(word) - len(possible_word)) > 3:
            continue
        dst = distance(word, possible_word)
        if dst <= 3:
            sim = similarity(word, possible_word)
            if sim >= 7:
                suggestions.append((possible_word, dst, sim))

    return sorted(suggestions, key=sort_key)

IS_FILE = False

if len(sys.argv) < 2:
    print("Please supply a word or a file to check")
    sys.exit(-1)

if os.path.exists(sys.argv[1]):
    IS_FILE = True

WORD_DICT = {}
root_dir = "words"
word_files = os.listdir(root_dir)
if '0-Copyright' in word_files:
    word_files.remove('0-Copyright')

for word_file in word_files:
    with open(os.path.join(root_dir, word_file), 'r') as file:
        for line in file.readlines():
            WORD_DICT.update({line.strip("\n"): 1})

WORD_LIST = WORD_DICT.keys()
print(f"TOTAL WORDS IN DATABASE: {len(WORD_LIST):,}\n")

if IS_FILE:
    with open(sys.argv[1], 'r') as file:
        text = file.read()
        text = text.strip("\n")

    text_words = text.split(' ')
    misspelled_words = []

    for word in text_words:
        word = word.strip("\n.,\"\':;><?!$%^&*()=+/\\|][{}`~")
        try:
            WORD_DICT[word]
        except KeyError:
            misspelled_words.append(word)

    total_time = 0
    print(f"RESULTS FOR FILE {sys.argv[1]}\n")
    for misspelled_word in misspelled_words:

        start = time.perf_counter()
        suggestions = get_spelling_suggest(misspelled_word)
        end = time.perf_counter()
        total_time += (end - start)

        print(f"Original Word: {misspelled_word}\n{'':->50}")
        if len(suggestions) == 0:
            print("No suggestions")
        else:
            for i in suggestions[0:5]:
                print(f"Word: {i[0]:<10} Dist: {i[1]:<3} Sim: {i[2]}")
        print('')

    print(f"TOTAL COMPUTATION TIME = {round(total_time, 2)} seconds")
else:
    suggestions = get_spelling_suggest(sys.argv[1])
    print(f"Original Word: {sys.argv[1]}\n{'':->50}")
    if len(suggestions) == 0:
        print("No suggestions")
    else:
        for i in suggestions[0:5]:
            print(f"Word: {i[0]:<10} Dist: {i[1]:<3} Sim: {i[2]}")
