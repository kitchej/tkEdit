"""
TEXT EDITOR FOR TKINTER
Written by Joshua Kitchen - March 2021, revised March 2023
A text editor app implemented in Tkinter.
"""
import sys
from src.main import Main

if len(sys.argv) > 2:
    print("Usage: tkEdit.py [filepath]")
    sys.exit(-1)
elif len(sys.argv) == 1:
    m = Main()
else:
    m = Main(sys.argv[1])
    m.mainloop()
