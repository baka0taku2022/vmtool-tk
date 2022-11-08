"""
    GUI for Connection window. Was originally part of RootWindow but was removed into it's own class to promote code
    reuse.
    -=baka0taku=-
"""

from .FuncLib import *
from .MainMenu import MainMenu


class ConnectionWin:
    def __init__(self, data: DataTree, ctype: str) -> None:
        self.dataset = data
        self.conntype = ctype
        # build login screen
        self.connwin = Toplevel(master=self.dataset.rootwin)
        self.connwin.master.withdraw()
        self.connwin.protocol("WM_DELETE_WINDOW", lambda: cleanup(dataset=self.dataset, rootwin=self.dataset.rootwin))
        # set var for status bar
        self.stat = StringVar()
        self.stat.set('Idle...')

        # define widgets
        self.serverentry = Entry(master=self.connwin, width=50)
        if self.conntype == "vcenter":
            self.serverlabel = Label(master=self.connwin, text="Enter a FQDN or IP Address of vCenter", padx=5, pady=5)
            self.userlabel = Label(master=self.connwin, text="Enter Username", padx=5)
            self.userentry = Entry(master=self.connwin, width=50)
        elif self.conntype == "esxi":
            self.serverlabel = Label(master=self.connwin, text="Enter a FQDN or IP Address of ESXi", padx=5, pady=5)
            self.userlabel = Label(master=self.connwin, text="Username (change if not root)", padx=5)
            self.userentry = Entry(master=self.connwin, width=50)
            self.userentry.insert(0, "root")

        self.passlabel = Label(master=self.connwin, text="Enter Password", padx=5)
        self.passentry = Entry(master=self.connwin, width=50, show='*')
        self.statusBar = Label(master=self.connwin, textvariable=self.stat)
        self.loginbutton = Button(master=self.connwin, text="Login", width=10,
                                  command=lambda: self.login_button(fqdn=self.serverentry.get(),
                                                                    user=self.userentry.get(),
                                                                    passwd=self.passentry.get()))

        # place widgets
        self.serverlabel.grid(row=0, column=0, sticky=E)
        self.serverentry.grid(row=0, column=1, columnspan=2, pady=5)
        self.userlabel.grid(row=1, column=0, sticky=E)
        self.userentry.grid(row=1, column=1, columnspan=2, pady=5)
        self.passlabel.grid(row=2, column=0, sticky=E)
        self.passentry.grid(row=2, column=1, columnspan=2, pady=5)
        self.loginbutton.grid(row=3, column=1)
        self.statusBar.grid(row=4, column=0, columnspan=3, pady=10, sticky=W + E)

    def login_button(self, fqdn, user, passwd) -> None:
        # check to see if each entry has something in it
        if passwd == '' or user == '' or fqdn == '':
            showerror(title='Error', message='Please fill in all fields!')
            return

        self.stat.set("Connecting...")
        self.connwin.update()
        if make_connection(dataset=self.dataset, fqdn=self.serverentry.get(), user=self.userentry.get(),
                           passwd=self.passentry.get()):

            self.stat.set('Connected...')
            self.dataset.sw = StatWindow(data=self.dataset)
            if self.conntype == "vcenter":
                MainMenu(data=self.dataset)

        else:
            self.stat.set("Idle...")
            self.connwin.update()
