import os
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk

from Levenshtein import distance

from src.editor import Editor


class SpellChecker:
    def __init__(self, parent, editor_obj: Editor):
        self.parent = parent
        self.editor_obj = editor_obj
        self.padx = 5
        self.pady = 1

        self.word_dict = {}
        word_files = os.listdir("words")
        if '0-Copyright' in word_files:
            word_files.remove('0-Copyright')
        for word_file in word_files:
            with open(os.path.join("words", word_file), 'r') as file:
                for line in file.readlines():
                    self.word_dict.update({line.strip("\n"): 1})

        self.word_list = self.word_dict.keys()
        self.suggestions = {}
        self.preview_frame = ttk.Frame(self.parent)
        self.spell_check_preview_box = tk.Text(self.preview_frame, height=5, width=50, state=tk.DISABLED)
        self.ignore_btn = ttk.Button(self.preview_frame, text="Ignore", command=self.ignore)
        self.ignore_all_btn = ttk.Button(self.preview_frame, text="Ignore All", command=self.ignore_all)
        self.add_to_dict_btn = ttk.Button(self.preview_frame, text="Add to Dictionary", command=self.add_to_dict)

        self.suggest_frame = ttk.Frame(self.parent)
        self.suggestions_listbox = tk.Listbox(self.suggest_frame, width=67)
        self.suggestions_lab = tk.Label(self.suggest_frame, text="Suggestions:")
        self.replace_btn = ttk.Button(self.suggest_frame, text="Replace", command=self.replace)

        self.analyzing_var = tk.StringVar()
        self.analyzing_var.set(f"Spell check in progress... 0/0")
        self.analyzing_label = tk.Label(self.parent, textvariable=self.analyzing_var, font=('Arial', 20))
        self.analyzing_label.pack()
        threading.Thread(target=self._check_spelling).start()


    def _pack_widgets(self):
        self.preview_frame.pack(anchor=tk.W)
        self.suggest_frame.pack(anchor=tk.W, pady=1)

        self.spell_check_preview_box.pack(side=tk.LEFT, padx=self.padx, pady=self.pady)
        self.ignore_btn.pack(side=tk.TOP, padx=self.padx, pady=self.pady, anchor=tk.W)
        self.ignore_all_btn.pack(side=tk.TOP, padx=self.padx, pady=self.pady, anchor=tk.W)
        self.add_to_dict_btn.pack(side=tk.TOP, padx=self.padx, pady=self.pady, anchor=tk.W)

        self.suggestions_lab.pack(side=tk.TOP, anchor=tk.W)
        self.suggestions_listbox.pack(side=tk.LEFT, padx=self.padx, pady=self.pady)
        self.replace_btn.pack(side=tk.RIGHT, padx=self.padx, pady=self.pady, anchor=tk.W)

    @staticmethod
    def _sort_key(x):
        return x[1], (x[2]) * -1

    @staticmethod
    def _similarity(str1, str2):
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

    def _get_spelling_suggest(self, word):
        suggestions = []
        for possible_word in self.word_list:
            # possible_word = possible_word.lower()
            if abs(len(word) - len(possible_word)) > 3:
                continue
            dst = distance(word, possible_word)
            if dst <= 3:
                sim = self._similarity(word, possible_word)
                if sim >= 7:
                    suggestions.append((possible_word, dst, sim))

        return sorted(suggestions, key=self._sort_key)

    def _check_spelling(self):
        text_words = self.editor_obj.get(0.0, tk.END).split(' ')
        self.misspelled_words = []

        for word in text_words:
            word = word.strip("\n.,\"\':;><?!$%^&*()=+/\\|][{}`~")
            try:
                self.word_dict[word]
            except KeyError:
                self.misspelled_words.append(word)
        count = 0
        for misspelled_word in self.misspelled_words:
            start = time.perf_counter()
            suggestions = self._get_spelling_suggest(misspelled_word)
            end = time.perf_counter()
            self.suggestions.update({misspelled_word: suggestions})
            count += 1
            self.analyzing_var.set(f"Spell check in progress... {count}/{len(self.misspelled_words)}")

        self.analyzing_label.pack_forget()
        self._pack_widgets()

    def add_to_dict(self, *args):
        pass
        
    def ignore(self, *args):
        pass

    def ignore_all(self, *args):
        pass

    def replace(self, *args):
        pass
