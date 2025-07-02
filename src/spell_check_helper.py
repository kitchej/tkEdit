import json
import os
import string
import threading
from tkinter import END as EDITOR_END

from Levenshtein import distance

from src.editor import Editor

class SpellCheckerHelper:
    def __init__(self, editor_obj: Editor):
        self.editor_obj = editor_obj

        self.word_dict = {}
        self.word_list = []
        self.suggestions = {}

        self._lexicon_available_con = threading.Condition()
        self._lexicon_available = False
        self._kill_spell_check = False
        self._kill_spell_check_lock = threading.Lock()

    @staticmethod
    def sort_key(x):
        return x[1], (x[2]) * -1

    @staticmethod
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

    def kill_spell_check(self):
        with self._kill_spell_check_lock:
            self._kill_spell_check = True

    def reset_kill_sig(self):
        with self._kill_spell_check_lock:
            self._kill_spell_check = False

    def check_kill_sig(self):
        with self._kill_spell_check_lock:
            return self._kill_spell_check

    def load_dict(self):
        print("load_dict(): Loading lexicon...")
        word_files = os.listdir(os.path.join("spell_check", "words"))
        for word_file in word_files:
            with open(os.path.join("spell_check", "words", word_file), 'r') as file:
                for line in file.readlines():
                    self.word_dict.update({line.strip("\n"): 1})

        self.word_list = self.word_dict.keys()
        print("load_dict(): Lexicon loaded, notifying threads")
        with self._lexicon_available_con:
            self._lexicon_available = True
            self._lexicon_available_con.notify_all()

    def get_spelling_suggest(self, word):
        suggestions = []
        for i, possible_word in enumerate(self.word_list):
            if self.check_kill_sig():
                return []
            if abs(len(word) - len(possible_word)) > 3:
                continue
            dst = distance(word, possible_word)
            if dst <= 3:
                # sim = self.similarity(word, possible_word)
                # if sim >= 7:
                #     suggestions.append((possible_word, dst, sim))
                suggestions.append((possible_word, dst, 0))

        return sorted(suggestions, key=self.sort_key)

    def check_spelling(self):
        text_words = self.editor_obj.get(0.0, EDITOR_END).split(' ')
        misspelled_words = []

        print("check_spelling(): Waiting for lexicon to be available")
        with self._lexicon_available_con:
            while not self._lexicon_available:
                self._lexicon_available_con.wait()

        for word in text_words:
            if self.check_kill_sig():
                return
            word = word.strip("\n.,\"\':;><?!$%^&*()=+/\\|][{}`~")
            # word.translate(str.maketrans('', '', string.punctuation))
            try:
                self.word_dict[word.lower()]
            except KeyError:
                misspelled_words.append(word)

        with open("misspelled.txt", 'w') as file:
            for w in misspelled_words:
                file.write(w + '\n')

        print("check_spelling(): Lexicon available, initiating spell check")
        for i, misspelled_word in enumerate(misspelled_words):
            if self.check_kill_sig():
                return
            suggestions = self.get_spelling_suggest(misspelled_word)
            self.suggestions.update({misspelled_word: suggestions})
            print(f"check_spelling(): Checked {i + 1}/{len(misspelled_words)} words")

        print(f"check_spelling(): Completed spell check")

        results = json.dumps(self.suggestions, indent=4)
        with open("spell_check_results.txt", 'w') as file:
            file.write(results)