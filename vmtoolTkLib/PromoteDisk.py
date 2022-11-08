"""
    General GUI for a smaller window. This also was a great reuse of code. Covers a couple of menu items.

    -=baka0taku=-
"""

from .FuncLib import *


class PromoteDisk:
    def __init__(self, data: DataTree, window_type: str) -> None:
        # define class variables
        self.dataset = data
        self.win_type = window_type

        # define widgets
        self.win = Toplevel(master=self.dataset.rootwin)
        if window_type == "promote":
            self.vmlabel = Label(master=self.win, text='Choose VMs to promote')
        elif window_type == "dvclone":
            self.vmlabel = Label(master=self.win, text='Choose DVPortgroup to clone')
        self.vmframe = Frame(master=self.win)
        if window_type == "promote":
            self.vmbox = Listbox(master=self.vmframe, bg='black', fg='white', width=50, height=15, selectmode=MULTIPLE)
        elif window_type == "dvclone":
            self.vmbox = Listbox(master=self.vmframe, bg='black', fg='white', width=50, height=15)
        self.vmscroll = Scrollbar(master=self.vmframe, orient=VERTICAL)
        self.vmbox.config(yscrollcommand=self.vmscroll.set)
        self.vmscroll.config(command=self.vmbox.yview)
        if window_type == "promote":
            self.vmbox.insert(END, *sorted(list(self.dataset.vmdict.keys())))
            self.refresh = Button(master=self.win, text='Refresh VM List',
                                  command=lambda: refresh_lists(orig_list=self.vmbox,
                                                                dest_list=None, dataset=self.dataset, list_type='vm'))
            self.executebutton = Button(master=self.win, text='Send promote task to server.',
                                        command=lambda: self.exe_handle(window_type=window_type))
        elif window_type == "dvclone":
            self.vmbox.insert(END, *sorted(list(self.dataset.dvportgroupdict.keys())))
            self.refresh = Button(master=self.win, text='Refresh DVPortgroup List',
                                  command=lambda: refresh_lists(orig_list=self.vmbox,
                                                                dest_list=None, dataset=self.dataset, list_type='pg'))
            self.executebutton = Button(master=self.win, text='Send clone task to server.',
                                        command=lambda: self.exe_handle(window_type=window_type))

        self.search_box = Entry(master=self.vmframe)
        self.search_box.bind(sequence='<KeyRelease>', func=self.search)
        # place widgets
        self.vmlabel.grid(row=0, column=0, padx=20, pady=5)
        self.vmframe.grid(row=1, column=0, padx=20, pady=20, rowspan=2)
        self.search_box.pack(side=TOP)
        self.vmbox.pack(side=LEFT, fill=BOTH)
        self.vmscroll.pack(side=RIGHT, fill=BOTH)
        self.refresh.grid(row=4, column=0, padx=20, pady=20)
        self.executebutton.grid(row=5, column=0, padx=20, pady=20, sticky=W + E)

    def exe_handle(self, window_type: str) -> None:
        if window_type == "promote":
            vmnames = list()
            selected = self.vmbox.curselection()
            for item in selected:
                vmnames.append(self.vmbox.get(item))
            if send_promote_task(names=vmnames, data=self.dataset):
                self.win.destroy()
            else:
                showinfo(title="Error", message="Something went wrong. Please check vcenter log for cause of failure.")
            return
        elif window_type == "dvclone":
            selected = self.vmbox.curselection()
            pgname = self.vmbox.get(selected)
            if send_portgroup_clone_task(name=pgname, data=self.dataset):
                self.win.destroy()
            else:
                showinfo(title="Error", message="Something went wrong. Please check vcenter log for cause of failure.")
            return

    def search(self, event):
        data = None
        val = event.widget.get()
        if self.win_type == "promote":
            if val == '':
                data = self.dataset.vmdict.keys()
            else:
                data = list()
                for item in self.dataset.vmdict.keys():
                    if val.lower() in item.lower():
                        data.append(item)
        elif self.win_type == "dvclone":
            if val == '':
                data = self.dataset.dvportgroupdict.keys()
            else:
                data = list()
                for item in self.dataset.dvportgroupdict.keys():
                    if val.lower() in item.lower():
                        data.append(item)
        self.update_list(data)
        return

    def update_list(self, data):
        self.vmbox.delete(0, 'end')

        # put new data
        for item in data:
            self.vmbox.insert('end', item)
        return
