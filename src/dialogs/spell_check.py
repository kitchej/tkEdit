import tkinter as tk
import tkinter.ttk as ttk


class SpellChecker:
    def __init__(self, parent, spell_checker_helper):
        self.parent = parent
        self.spell_check_helper = spell_checker_helper
        self.padx = 5
        self.pady = 1

        self.preview_frame = ttk.Frame(self.parent)
        self.spell_check_preview_box = tk.Text(self.preview_frame, height=5, width=50, state=tk.DISABLED)
        self.ignore_btn = ttk.Button(self.preview_frame, text="Ignore", command=self.ignore)
        self.ignore_all_btn = ttk.Button(self.preview_frame, text="Ignore All", command=self.ignore_all)
        self.add_to_dict_btn = ttk.Button(self.preview_frame, text="Add to Dictionary", command=self.add_to_dict)

        self.suggest_frame = ttk.Frame(self.parent)
        self.suggestions_listbox = tk.Listbox(self.suggest_frame, width=67)
        self.suggestions_lab = tk.Label(self.suggest_frame, text="Suggestions:")
        self.replace_btn = ttk.Button(self.suggest_frame, text="Replace", command=self.replace)
        self._pack_widgets()


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

    def add_to_dict(self, *args):
        pass
        
    def ignore(self, *args):
        pass

    def ignore_all(self, *args):
        pass

    def replace(self, *args):
        pass
