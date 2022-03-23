'''
Window to display critical VM stats for a selected VM
CPU usage, RAM usage, Disk Usage, Frozen?, Power state
'''
from .FuncLib import *


class VmStatusWindow:
    def __init__(self, dataset: DataTree):
        self.data: DataTree = dataset
        self.cpuvar: StringVar = str()

        # define widgets
        self.top_level = Toplevel(master=self.data.rootwin)
        self.vm_frame = Frame(master=self.top_level)
        self.vm_list = Listbox(master=self.vm_frame, width=50, height=15)
        self.vm_scroll = Scrollbar(master=self.vm_frame, orient=VERTICAL)
        self.cpu_label = Label(master=self.top_level, text="CPU Usage")
        self.cpu_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.cpuvar)

        # define scrollbar properties
        self.vm_list.config(yscrollcommand=self.vm_scroll.set)
        self.vm_scroll.config(command=self.vm_list.yview)

        # add VMs to list
        self.vm_list.insert(END, *sorted(list(self.data.vmdict.keys())))

        # place widgets
        self.vm_frame.grid(column=0, row=0, padx=20, pady=20)
        self.vm_list.pack(side=LEFT)
        self.vm_scroll.pack(side=RIGHT, fill=BOTH)
        self.cpu_label.grid(column=1, row=0, padx=10, pady=10)
        self.cpu_usage.grid(column=2, row=0, padx=10, pady=10)