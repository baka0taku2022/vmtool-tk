"""
    Builds a GUI for a shutdown log.

"""

from .FuncLib import *


class ShutdownWin:
    def __init__(self, data: DataTree) -> None:
        self.dataset = data

        # create widgets
        self.win = Toplevel(master=self.dataset.rootwin)
        self.logframe = Frame(master=self.win)
        self.logtext = Text(master=self.logframe, width=80, height=24, state=DISABLED)
        self.logscroll = Scrollbar(master=self.logframe, orient=VERTICAL)
        self.shutbutton = Button(master=self.win, text='Begin Shutdown', command=self.shut_handle)
        self.logtext.config(yscrollcommand=self.logscroll.set)
        self.logscroll.config(command=self.logtext.yview)

        # place widgets
        self.logtext.pack(side=LEFT, fill=BOTH)
        self.logscroll.pack(side=RIGHT, fill=BOTH)
        self.logframe.grid(row=0, column=0, padx=20, pady=5, rowspan=2)
        self.shutbutton.grid(row=2, column=0, padx=20, pady=20, sticky=W+E)

        # button handler
    def shut_handle(self) ->None:
        if askyesno(title='Shut Down?', message='Are you sure you want to shut down?'):
            print("not implemented")
        return
