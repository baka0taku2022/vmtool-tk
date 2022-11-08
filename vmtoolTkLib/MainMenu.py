"""
    Creates the Main Menu GUI - I tried to keep this as minimal as possible for speed.
    -=baka0taku=-
"""

from .CloneWin import CloneWin
from .PromoteDisk import PromoteDisk
from .FuncLib import *
from .PasteWin import PasteWin
from .VmStatusWindow import VmStatusWindow
from .HostStatusWindow import HostStatusWindow


class MainMenu:
    def __init__(self, data: DataTree):
        # define vars
        self.dataset = data

        # define new window
        self.mainMenu = Toplevel(master=self.dataset.rootwin)
        # define widgets
        self.menuFrame = LabelFrame(master=self.mainMenu, padx=10, pady=10, text="Main Menu")
        # define vars
        self.mm = IntVar()
        # define more widgets
        self.item1 = Radiobutton(master=self.menuFrame, text="Create linked clone(s)", variable=self.mm,
                                 value=1, command=self.menuhandle)
        self.item2 = Radiobutton(master=self.menuFrame, text="Create instant clone(s)", variable=self.mm,
                                 value=2, command=self.menuhandle)
        self.item3 = Radiobutton(master=self.menuFrame, text="Promote clone(s)", variable=self.mm,
                                 value=3, command=self.menuhandle)
        self.item4 = Radiobutton(master=self.menuFrame, text="Clone DVPortgroup", variable=self.mm,
                                 value=4, command=self.menuhandle)
        self.item5 = Radiobutton(master=self.menuFrame, text="Paste into VM", variable=self.mm,
                                 value=5, command=self.menuhandle)
        self.item6 = Radiobutton(master=self.menuFrame, text="VM Status Window", variable=self.mm,
                                 value=6, command=self.menuhandle)
        self.item7 = Radiobutton(master=self.menuFrame, text="Host Status Window", variable=self.mm,
                                 value=7, command=self.menuhandle)
        self.item8 = Radiobutton(master=self.menuFrame, text="Quit", variable=self.mm,
                                 value=8, command=self.menuhandle)
        # place widgets
        self.menuFrame.grid(row=0, column=0, padx=50, pady=50)
        self.item1.grid(row=0, column=0, padx=5, pady=5)
        self.item2.grid(row=1, column=0, padx=5, pady=5)
        self.item3.grid(row=2, column=0, padx=5, pady=5)
        self.item4.grid(row=3, column=0, padx=5, pady=5)
        self.item5.grid(row=4, column=0, padx=5, pady=5)
        self.item6.grid(row=5, column=0, padx=5, pady=5)
        self.item7.grid(row=6, column=0, padx=5, pady=5)
        self.item8.grid(row=7, column=0, padx=5, pady=5)
        # update canvas
        self.mainMenu.update_idletasks()

    # menu handling method
    def menuhandle(self) -> None:
        decision = self.mm.get()
        if decision == 8:
            cleanup(dataset=self.dataset, rootwin=self.dataset.rootwin)
        elif decision == 1:
            CloneWin(data=self.dataset, wintype="linked")
        elif decision == 2:
            CloneWin(data=self.dataset, wintype="instant")
        elif decision == 3:
            PromoteDisk(data=self.dataset, window_type="promote")
        elif decision == 4:
            PromoteDisk(data=self.dataset, window_type="dvclone")
        elif decision == 5:
            PasteWin(data=self.dataset)
        elif decision == 6:
            VmStatusWindow(dataset=self.dataset)
        elif decision == 7:
            HostStatusWindow(data=self.dataset)
        return
