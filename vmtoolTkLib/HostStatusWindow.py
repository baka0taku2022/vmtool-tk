"""
This window is a set of status variables and tools for ESXi Hosts.
"""
from .FuncLib import *
from tkinter.ttk import Progressbar


class HostStatusWindow:
    def __init__(self, data: DataTree):
        # define class vars
        self.dataset = data
        self.hostdict: dict = self.dataset.hostdict
        self.host_object = None

        # define status vars
        self.powered_on: StringVar = StringVar()
        self.maintenance_mode: StringVar = StringVar()
        self.cpu_usage: StringVar = StringVar()
        self.memory_usage: StringVar = StringVar()
        self.storage_usage: StringVar = StringVar()
        self.cpu_usage_var: IntVar = IntVar()
        self.memory_usage_var: IntVar = IntVar()
        self.storage_usage_var: IntVar = IntVar()

        # define widgets
        self.top: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.host_frame = Frame(master=self.top)
        self.host_list_label: Label = Label(master=self.top, text="Hosts:", padx=10, pady=10)
        self.host_list: Listbox = Listbox(master=self.host_frame, width=50, height=15)
        self.host_scroll = Scrollbar(master=self.host_frame, orient=VERTICAL)
        self.powered_on_label: Label = Label(master=self.top, text="Powered On?")
        self.powered_on_stat: Label = Label(master=self.top, textvariable=self.powered_on, relief=SUNKEN)
        self.maintenance_mode_label: Label = Label(master=self.top, text="Maintenance Mode?")
        self.maintenance_mode_stat: Label = Label(master=self.top, textvariable=self.maintenance_mode, relief=SUNKEN)
        self.cpu_usage_label: Label = Label(master=self.top, text="CPU Usage")
        self.cpu_usage_stat: Label = Label(master=self.top, textvariable=self.cpu_usage, relief=SUNKEN)
        self.memory_usage_label: Label = Label(master=self.top, text="Memory Usage")
        self.memory_usage_stat: Label = Label(master=self.top, textvariable=self.memory_usage, relief=SUNKEN)
        self.storage_usage_label: Label = Label(master=self.top, text="Storage Free")
        self.storage_usage_stat: Label = Label(master=self.top, textvariable=self.storage_usage, relief=SUNKEN)
        self.cpu_bar: Progressbar = Progressbar(master=self.top, maximum=100, orient=HORIZONTAL,
                                                variable=self.cpu_usage_var)
        self.memory_bar: Progressbar = Progressbar(master=self.top, maximum=100, orient=HORIZONTAL,
                                                   variable=self.memory_usage_var)
        self.storage_bar: Progressbar = Progressbar(master=self.top, maximum=100, orient=HORIZONTAL,
                                                    variable=self.storage_usage_var)

        # place widgets
        self.host_list_label.grid(column=0, row=0, padx=10, pady=10)
        self.host_frame.grid(column=1, row=0, padx=10, pady=10, rowspan=5)
        self.host_list.pack(side=LEFT)
        self.host_scroll.pack(side=RIGHT, fill=BOTH)
        self.powered_on_label.grid(column=2, row=0, padx=10, pady=10)
        self.maintenance_mode_label.grid(column=2, row=1, padx=10, pady=10)
        self.cpu_usage_label.grid(column=2, row=2, padx=10, pady=10)
        self.memory_usage_label.grid(column=2, row=3, padx=10, pady=10)
        self.storage_usage_label.grid(column=2, row=4, padx=10, pady=10)
        self.powered_on_stat.grid(column=3, row=0, padx=10, pady=10)
        self.maintenance_mode_stat.grid(column=3, row=1, padx=10, pady=10)
        self.cpu_usage_stat.grid(column=3, row=2, padx=10, pady=10)
        self.memory_usage_stat.grid(column=3, row=3, padx=10, pady=10)
        self.storage_usage_stat.grid(column=3, row=4, padx=10, pady=10)
        self.cpu_bar.grid(column=4, row=2, padx=10, pady=10)
        self.memory_bar.grid(column=4, row=3, padx=10, pady=10)
        self.storage_bar.grid(column=4, row=4, padx=10, pady=10)

        # define scrollbar properties
        self.host_list.config(yscrollcommand=self.host_scroll.set)
        self.host_scroll.config(command=self.host_list.yview)

        # populate list
        self.host_list.insert(END, *sorted(list(self.hostdict.keys())))

        # bind events
        self.host_list.bind('<<ListboxSelect>>', self.list_handle)

    def list_handle(self, event):
        # get selected index
        selected_index: tuple = self.host_list.curselection()

        # get text from selection
        if not selected_index:
            selected_name: str = ""
        # get host name from listbox
        else:
            selected_name: str = self.host_list.get(selected_index)
        # get host object from dictionary
        self.host_object: vim.HostSystem = self.hostdict.get(selected_name)
        # get values from host
        self.powered_on.set(str(is_host_powered_on(hostobj=self.host_object)))
        self.maintenance_mode.set(str(is_host_in_maint_mode(hostobj=self.host_object)))
        cpu_usage = get_host_cpu_usage(hostobj=self.host_object)
        mem_usage = get_host_memory_usage(hostobj=self.host_object)
        storage_usage = get_host_storage_usage(hostobj=self.host_object)
        self.cpu_usage.set(str(cpu_usage) + '%')
        self.memory_usage.set(str(mem_usage) + '%')
        self.storage_usage.set(str(storage_usage) + '% Free')
        self.cpu_usage_var.set(cpu_usage)
        self.memory_usage_var.set(mem_usage)
        self.storage_usage_var.set(storage_usage)
        self.top.update_idletasks()
        return
