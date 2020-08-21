"""
    Creates the Main Menu GUI - I tried to keep this as minimal as possible for speed.
    -=baka0taku=-
"""

from .CloneWin import CloneWin
from .PromoteDisk import PromoteDisk
# from .ShutdownWin import ShutdownWin
from .FuncLib import *


class MainMenu:
    def __init__(self, data: DataTree):
        # define vars
        self.dataset = data

        # define new window
        self.mainMenu = Toplevel(master=self.dataset.rootwin, bg='black')
        self.mainMenu.protocol("WM_DELETE_WINDOW", lambda: cleanup(dataset=self.dataset, rootwin=self.mainMenu.master))
        # define widgets
        self.menuFrame = LabelFrame(master=self.mainMenu, bg='black', padx=10, pady=10, text="Main Menu", fg='white')
        # define vars
        self.mm = IntVar()
        # define more widgets
        self.item1 = Radiobutton(master=self.menuFrame, text="Create linked clone(s)", variable=self.mm,
                                 value=1, bg='black', fg='white', command=self.menuhandle)
        self.item2 = Radiobutton(master=self.menuFrame, text="Create instant clone(s)", variable=self.mm,
                                 value=2, bg='black', fg='white', command=self.menuhandle)
        self.item3 = Radiobutton(master=self.menuFrame, text="Promote clone(s)", variable=self.mm,
                                 value=3, bg='black', fg='white', command=self.menuhandle)
        self.item4 = Radiobutton(master=self.menuFrame, text="Clone DVPortgroup", variable=self.mm,
                                 value=4, bg='black', fg='white', command=self.menuhandle)
        # self.item5 = Radiobutton(master=self.menuFrame, text="Graceful shutdown", variable=self.mm,
        #                         value=5, bg='black', fg='white', command=self.menuhandle)
        self.item6 = Radiobutton(master=self.menuFrame, text="Quit", variable=self.mm,
                                 value=6, bg='black', fg='white', command=self.menuhandle)
        # place widgets
        self.menuFrame.grid(row=0, column=0, padx=50, pady=50)
        self.item1.grid(row=0, column=0, padx=5, pady=5)
        self.item2.grid(row=1, column=0, padx=5, pady=5)
        self.item3.grid(row=2, column=0, padx=5, pady=5)
        self.item4.grid(row=3, column=0, padx=5, pady=5)
        # self.item5.grid(row=4, column=0, padx=5, pady=5)
        self.item6.grid(row=5, column=0, padx=5, pady=5)
        # update canvas
        self.mainMenu.update_idletasks()

    # menu handling method
    def menuhandle(self) -> None:
        decision = self.mm.get()
        if decision == 6:
            cleanup(dataset=self.dataset, rootwin=self.mainMenu.master)
        elif decision == 1:
            CloneWin(data=self.dataset, wintype="linked")
        elif decision == 2:
            CloneWin(data=self.dataset, wintype="instant")
        elif decision == 3:
            PromoteDisk(data=self.dataset, window_type="promote")
        elif decision == 4:
            PromoteDisk(data=self.dataset, window_type="dvclone")
        elif decision == 5:
            # ShutdownWin(data=self.dataset)
            pass
        return
