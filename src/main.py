import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from src.dialogs.find_and_replace import FindAndReplaceWin
from src.dialogs.font_chooser import FontChooser
from src.dialogs.spell_check import SpellChecker
from src.editor import Editor
from src.menus.file_menu import FileMenu
from src.menus.edit_menu import EditMenu
from src.menus.format_menu import FormatMenu
from src.status_bar import StatusBar
from src.syntax_highlighting.python import PythonSyntaxHighlighter


class Main(tk.Tk):
    def __init__(self, in_file=None):
        tk.Tk.__init__(self)

        self.FIND_AND_REP_WIN = None
        self.FONT_CHOOSE_WIN = None
        self.SPELL_CHECK_WIN = None
        self.filename = None

        self.geometry('1000x500')
        self.protocol('WM_DELETE_WINDOW', self.close)

        self.editor_frame = tk.Frame(self)
        self.editor_frame.pack_propagate(False)
        self.editor = Editor(self.editor_frame)

        self.scrollbar = ttk.Scrollbar(self, command=self.editor.yview, cursor='arrow')
        self.editor.configure(yscrollcommand=self.scrollbar.set, relief=tk.FLAT)

        self.status = StatusBar(self)

        self.main_menu = tk.Menu(self)
        self.file_menu = FileMenu(self)
        self.edit_menu = EditMenu(self)
        self.format_menu = FormatMenu(self)
        self.main_menu.add_cascade(menu=self.file_menu, label='File')
        self.main_menu.add_cascade(menu=self.edit_menu, label='Edit')
        self.main_menu.add_cascade(menu=self.format_menu, label='Format')
        self.configure(menu=self.main_menu)

        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.bind('<F5>', self.edit_menu.add_timestamp)
        self.bind('<Control_L>f', self.edit_menu.find_and_replace)
        self.bind('<Control_L>o', self.file_menu.open_from_filemanager)
        self.bind('<Control_L>s', self.file_menu.save)
        self.bind('<Control_L>n', self.file_menu.new_file)
        self.bind("<Key>", self.update_syntax_highlighting)

        self._syntax_highlighter = None
        self._syntax_highlighters = {"py": PythonSyntaxHighlighter(self.editor)}

        self.in_file = in_file
        if in_file:
            self.file_menu.open_file(self.in_file)
        self.title(self.file_menu.filename)
        self.update_gui()


    def quit_find_and_replace(self, *args):
        self.editor.clear_tags('found')
        if isinstance(self.FIND_AND_REP_WIN, tk.Toplevel):
            self.FIND_AND_REP_WIN.destroy()

    def create_find_and_replace_dialog(self):
        if isinstance(self.FIND_AND_REP_WIN, tk.Toplevel):
            self.quit_find_and_replace()
        self.FIND_AND_REP_WIN = tk.Toplevel()
        _ = FindAndReplaceWin(self.FIND_AND_REP_WIN, self.editor)
        self.FIND_AND_REP_WIN.resizable(False, False)
        self.FIND_AND_REP_WIN.title("Find and Replace")
        self.FIND_AND_REP_WIN.protocol('WM_DELETE_WINDOW', self.quit_find_and_replace)
        self.FIND_AND_REP_WIN.bind('<Destroy>', self.quit_find_and_replace)
        self.FIND_AND_REP_WIN.focus_set()

    def create_font_chooser_dialog(self):
        if isinstance(self.FONT_CHOOSE_WIN, tk.Toplevel):
            self.FONT_CHOOSE_WIN.destroy()
        self.FONT_CHOOSE_WIN = tk.Toplevel()
        _ = FontChooser(self.FONT_CHOOSE_WIN, self.editor)
        self.FONT_CHOOSE_WIN.resizable(False, False)
        self.FONT_CHOOSE_WIN.title("Select Font")
        self.FONT_CHOOSE_WIN.geometry("500x400")
        self.FONT_CHOOSE_WIN.focus_set()

    def create_spell_check_dialog(self):
        if isinstance(self.SPELL_CHECK_WIN, tk.Toplevel):
            self.SPELL_CHECK_WIN.destroy()
        self.SPELL_CHECK_WIN = tk.Toplevel()
        _ = SpellChecker(self.SPELL_CHECK_WIN, self.editor)
        self.SPELL_CHECK_WIN.resizable(False, False)
        self.SPELL_CHECK_WIN.title("Spell Check")
        self.SPELL_CHECK_WIN.focus_set()

    def set_syntax_highlighter(self, extension):
        try:
            self._syntax_highlighter = self._syntax_highlighters[extension]
        except KeyError:
            self._syntax_highlighter = None

    def update_syntax_highlighting(self, *args):
        if self._syntax_highlighter is not None:
            for tag in self._syntax_highlighter.get_tag_names():
                self.editor.clear_tags(tag)
            self._syntax_highlighter.highlight_syntax()
            self.update_idletasks()

    def update_gui(self):
        if self.editor.edit_modified():
            self.filename = os.path.split(self.file_menu.filepath)[-1]
            self.title(f'*{self.filename}')

        index = self.editor.index(tk.INSERT)
        index = index.split('.')
        self.status.update_line_and_col(index[0], index[1])
        # Update the GUI every 100 milliseconds
        self.after(100, self.update_gui)

    def close(self):
        self.file_menu.store_recent_files()
        if self.editor.edit_modified() == 0:
            self.editor.update_config()
            self.quit()
        else:
            answer = messagebox.askyesnocancel(title='Save?', message=f'Do you want to save {self.filename}'
                                                                      f' before quitting?')
            if answer:
                self.file_menu.save()
                self.editor.update_config()
                self.quit()
            elif answer is None:
                return
            else:
                self.editor.update_config()
                self.quit()
