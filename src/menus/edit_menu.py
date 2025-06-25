from datetime import datetime
import tkinter as tk


class EditMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.editor_obj = self.parent.editor
        self.add_command(label='Cut', accelerator='Ctrl+X',
                         command=lambda: self.editor_obj.event_generate('<<Cut>>'))
        self.add_command(label='Copy', accelerator='Ctrl+C',
                         command=lambda: self.editor_obj.event_generate('<<Copy>>'))
        self.add_command(label='Paste', accelerator='Ctrl+V',
                         command=lambda: self.editor_obj.event_generate('<<Paste>>'))
        self.add_command(label='Add Timestamp', accelerator='F5', command=self.add_timestamp)
        self.add_command(label='Find and Replace', accelerator='Ctrl+F', command=self.find_and_replace)
        self.add_command(label='Check Spelling', command=self.spell_check)

    def add_timestamp(self, *args):
        self.editor_obj.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))
        self.editor_obj.edit_modified(True)
        self.parent.title(f'*{self.parent.filename}')

    def find_and_replace(self, *args):
        self.parent.create_find_and_replace_dialog()

    def spell_check(self, *args):
        self.parent.create_spell_check_dialog()

