"""
    Generates GUI for multiple menu options. Was able to reuse the same layout by adding very few lines of code.

    -=baka0taku=-
"""

from .FuncLib import *


class CloneWin:
    def __init__(self, data: DataTree, wintype: str) -> None:
        self.dataset = data
        self.typewin = wintype

        # create widgets
        self.win = Toplevel(master=self.dataset.rootwin)
        self.vmframe = Frame(master=self.win)
        self.vmbox = Listbox(master=self.vmframe, width=50, height=15, selectmode=MULTIPLE)
        self.vmscroll = Scrollbar(master=self.vmframe, orient=VERTICAL)
        self.search_box = Entry(master=self.win)
        self.search_box.bind(sequence='<KeyRelease>', func=self.scankey)

        # configure scrollbar for vmbox
        self.vmbox.config(yscrollcommand=self.vmscroll.set)
        self.vmscroll.config(command=self.vmbox.yview)

        # add vm list to vmbox
        self.vmbox.insert(END, *sorted(list(self.dataset.vmdict.keys())))

        # create more widgets
        self.linkframe = Frame(master=self.win)
        self.clonebox = Listbox(master=self.linkframe, width=50, height=15, selectmode=MULTIPLE)
        self.linkscroll = Scrollbar(master=self.linkframe, orient=VERTICAL)
        # configure scrollbar
        self.clonebox.config(yscrollcommand=self.linkscroll.set)
        self.linkscroll.config(command=self.clonebox.yview)
        self.tolink = Button(master=self.win, text='>>',
                             command=lambda: mv_lstbox(orig_list=self.vmbox, dest_list=self.clonebox))
        self.refresh = Button(master=self.win, text='Refresh VM List',
                              command=lambda: refresh_lists(orig_list=self.vmbox,
                                                            dest_list=self.clonebox, dataset=self.dataset,
                                                            list_type='vm'))
        self.tovm = Button(master=self.win, text='<<',
                           command=lambda: mv_lstbox(orig_list=self.clonebox, dest_list=self.vmbox))
        self.vmlabel = Label(master=self.win, text='Server VM list')
        if self.typewin == "linked":
            self.linklabel = Label(master=self.win, text='Linked Clone VM list')
        elif self.typewin == "instant":
            self.linklabel = Label(master=self.win, text='Instant Clone VM list')
        self.executebutton = Button(master=self.win, text='Send clone task to server.',
                                    command=self.exe_handle)

        # define spinbox in frame
        self.spin_frame = Frame(master=self.win)
        self.spin_label = Label(master=self.spin_frame, text="Number of clones")
        self.num_of_clones = Spinbox(master=self.spin_frame, from_=1, to=255)

        # place widgets for spin_frame and place spin frame
        self.spin_frame.grid(row=4, column=2)
        self.spin_label.pack(side=LEFT)
        self.num_of_clones.pack(side=RIGHT)

        # place widgets for vm list
        self.search_box.grid(row=1, column=0, padx=20, pady=5)
        self.vmlabel.grid(row=0, column=0, padx=20, pady=5)
        self.vmframe.grid(row=2, column=0, padx=20, pady=20, rowspan=3)
        self.vmbox.pack(side=LEFT, fill=BOTH)
        self.vmscroll.pack(side=RIGHT, fill=BOTH)

        # place widgets for clone list
        self.linkframe.grid(row=2, column=3, padx=20, pady=20, rowspan=3)
        self.linklabel.grid(row=0, column=3, padx=20, pady=5)
        self.clonebox.pack(side=LEFT, fill=BOTH)
        self.linkscroll.pack(side=RIGHT, fill=BOTH)

        self.tolink.grid(row=1, column=2, padx=20, pady=20)
        self.refresh.grid(row=2, column=2, padx=20, pady=20)
        self.tovm.grid(row=3, column=2, padx=20, pady=20)
        self.executebutton.grid(row=5, column=0, padx=20, pady=20, columnspan=5, sticky=W + E)

    def exe_handle(self) -> None:
        if self.typewin == "linked":
            multi_linked_clones(vm_names=list(self.clonebox.get(0, END)), num_of_clones=int(self.num_of_clones.get()),
                                data=self.dataset)
            self.win.destroy()
        else:
            multi_instant_clones(vm_names=list(self.clonebox.get(0, END)), num_of_clones=int(self.num_of_clones.get()),
                                 data=self.dataset)
            self.win.destroy()
        return

    def update_list(self, data):
        self.vmbox.delete(0, 'end')

        # put new data
        for item in data:
            self.vmbox.insert('end', item)
        return

    def scankey(self, event):
        val = event.widget.get()

        if val == '':
            data = self.dataset.vmdict.keys()
        else:
            data = list()
            for item in self.dataset.vmdict.keys():
                if val.lower() in item.lower():
                    data.append(item)
        self.update_list(data)




