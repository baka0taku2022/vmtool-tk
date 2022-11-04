"""
    GUI for login window - for the most part just creates the GUI window.
    -=baka0taku=-
"""
from tkinter.font import *

from .FuncLib import *
from .ConnectionWin import ConnectionWin


class RootWindow:

    def __init__(self, data: DataTree) -> None:
        # build root window
        self.dataset = data
        self.dataset.rootwin = self.root = Tk()
        self.root.title('vmtoolTk 0.6')
        self.default_font: Font
        self.default_font = nametofont("TkDefaultFont")
        self.default_font.configure(size=12)
        self.root.option_add("*Font", self.default_font)
        ConnectionWin(data=self.dataset, ctype="vcenter")

    def start(self) -> None:
        self.root.mainloop()
