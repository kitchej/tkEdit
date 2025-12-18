import json
import os
import threading
import time

import TCPLib.tcp_client as tcp_client
from Levenshtein import distance

class SpellCheckerHelper:
    def __init__(self):
        self.word_dict = {}
        self.word_list = []
        self.suggestions = {}

        self._lexicon_available_con = threading.Condition()
        self._lexicon_available = False
        self._kill_spell_check = False
        self._kill_spell_check_lock = threading.Lock()

        threading.Thread(target=self.load_dict).start()

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

        for pos, (i, j) in enumerate(zip(str1, str2)):
            if i == j:
                score += 2
            elif pos < (len(str2) - 1) and str2[pos + 1] == i:
                score += 1
            elif pos > 0 and str2[pos - 1] == i:
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

    def check_spelling(self, text_words):
        misspelled_words = []

        print("check_spelling(): Waiting for lexicon to be available")
        with self._lexicon_available_con:
            while not self._lexicon_available:
                self._lexicon_available_con.wait()

        text_words = text_words.split()

        for word in text_words:
            if self.check_kill_sig():
                return
            word = word.strip("\n.,\"\':;><?!$%^&*()=+/\\|][{}`~")
            # word.translate(str.maketrans('', '', string.punctuation))
            try:
                self.word_dict[word.lower()]
            except KeyError:
                misspelled_words.append(word)

        with open("misspelled.txt", 'w', encoding='utf-8') as file:
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
        with open("spell_check_results.txt", 'w', encoding='utf-8') as file:
            file.write(results)

        return results


def start_spell_check_server():
    spell_checker = SpellCheckerHelper()
    client = tcp_client.TCPClient()

    client.connect(('127.0.0.1', 5000))
    print("Connected to host, starting spell check server")
    time.sleep(0.1)
    client.send(b'ready')
    while True:
        msg = client.receive()
        print(f"CHILD: {msg}")
        if msg == b'kill':
            spell_checker.kill_spell_check()
            client.disconnect()
            break
        elif msg == b'stop':
            spell_checker.kill_spell_check()
        else:
            threading.Thread(target=spell_checker.check_spelling, args=[str(msg, encoding='utf-8')]).start()
