"""
Window to display critical VM stats for a selected VM
CPU usage, RAM usage, Disk Usage, Frozen?, Power state?, Snapshots?, VMDK Files
"""
from .SnapshotWindow import SnapshotWindow
from .FreezeWindow import FreezeWindow
from .FuncLib import *

class VmStatusWindow:
    def __init__(self, dataset: DataTree):
        self.data: DataTree = dataset
        self.vm_object: vim.VirtualMachine

        # define status variables
        self.cpuvar: StringVar = StringVar()
        self.ramvar: StringVar = StringVar()
        self.disknumvar: StringVar = StringVar()
        self.diskusevar: StringVar = StringVar()
        self.diskfilevar: StringVar = StringVar()
        self.frozenvar: StringVar = StringVar()
        self.powervar: StringVar = StringVar()
        self.snapvar: StringVar = StringVar()

        # define widgets
        self.top_level = Toplevel(master=self.data.rootwin)
        self.vm_frame = Frame(master=self.top_level)
        self.vm_list = Listbox(master=self.vm_frame, width=50, height=15)
        # event binding
        self.vm_list.bind('<<ListboxSelect>>', self.list_handle)
        self.vm_scroll = Scrollbar(master=self.vm_frame, orient=VERTICAL)
        self.cpu_label = Label(master=self.top_level, text="CPU Usage")
        self.cpu_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.cpuvar)
        self.mem_label = Label(master=self.top_level, text="Memory Usage")
        self.mem_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.ramvar)
        self.disk_usage_label = Label(master=self.top_level, text="Disk Usage")
        self.disk_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.diskusevar)
        self.power_label = Label(master=self.top_level, text="Powered on?")
        self.power = Label(master=self.top_level, relief=SUNKEN, textvariable=self.powervar)
        self.frozen_label = Label(master=self.top_level, text="Frozen?")
        self.frozen = Label(master=self.top_level, relief=SUNKEN, textvariable=self.frozenvar)
        self.num_disks_label = Label(master=self.top_level, text="Number of Disks")
        self.num_disks = Label(master=self.top_level, relief=SUNKEN, textvariable=self.disknumvar)
        self.num_snapshots_label = Label(master=self.top_level, text="Number of Snapshots")
        self.num_snapshots = Label(master=self.top_level, relief=SUNKEN, textvariable=self.snapvar)
        self.num_disk_files_label = Label(master=self.top_level, text="Number of Disk Files/Disk")
        self.num_disk_files = Label(master=self.top_level, relief=SUNKEN, textvariable=self.diskfilevar)
        self.power_on_button = Button(master=self.top_level, text="Power On", command=lambda: self.power_on_handler())
        self.power_off_button = Button(master=self.top_level, text="Power Off", command=lambda: self.power_off_handler())
        self.promote_button = Button(master=self.top_level, text="Promote", command=lambda: self.promote_handler())
        self.snapshot_button = Button(master=self.top_level, text="Create Snapshot", command=lambda: self.snapshot_handler())
        self.linked_clone_button = Button(master=self.top_level, text="Linked Clone",
                                          command=lambda: self.linked_clone_handler())
        self.instant_clone_button = Button(master=self.top_level, text="Instant Clone",
                                           command=lambda: self.instant_clone_handler())
        self.freeze_button = Button(master=self.top_level, text="Freeze", command=lambda: self.freeze_handler())
        self.boot_bios_button = Button(master=self.top_level, text="BIOS Boot", command= lambda: self.bios_boot_handler())
        self.search_box = Entry(master=self.vm_frame, width=50)
        self.search_box.bind(sequence='<KeyRelease>', func=self.search_vms)

        # define scrollbar properties
        self.vm_list.config(yscrollcommand=self.vm_scroll.set)
        self.vm_scroll.config(command=self.vm_list.yview)

        # add VMs to list
        self.vm_list.insert(END, *sorted(list(self.data.vmdict.keys())))

        # place widgets
        self.vm_frame.grid(column=0, row=0, padx=20, pady=20, rowspan=8)
        self.search_box.pack(side=TOP)
        self.vm_list.pack(side=LEFT)
        self.vm_scroll.pack(side=RIGHT, fill=BOTH)
        self.cpu_label.grid(column=1, row=0, padx=10, pady=10)
        self.cpu_usage.grid(column=2, row=0, padx=10, pady=10)
        self.mem_label.grid(column=1, row=1, padx=10, pady=10)
        self.mem_usage.grid(column=2, row=1, padx=10, pady=10)
        self.disk_usage_label.grid(column=1, row=2, padx=10, pady=10)
        self.disk_usage.grid(column=2, row=2, padx=10, pady=10)
        self.power_label.grid(column=1, row=3, padx=10, pady=10)
        self.power.grid(column=2, row=3, padx=10, pady=10)
        self.frozen_label.grid(column=1, row=4, padx=10, pady=10)
        self.frozen.grid(column=2, row=4, padx=10, pady=10)
        self.num_disks_label.grid(column=1, row=5, padx=10, pady=10)
        self.num_disks.grid(column=2, row=5, padx=10, pady=10)
        self.num_snapshots_label.grid(column=1, row=6, padx=10, pady=10)
        self.num_snapshots.grid(column=2, row=6, padx=10, pady=10)
        self.num_disk_files_label.grid(column=1, row=7, padx=10, pady=10)
        self.num_disk_files.grid(column=2, row=7, padx=10, pady=10)
        self.power_on_button.grid(column=3, row=0, padx=10, pady=10)
        self.power_off_button.grid(column=3, row=1, padx=10, pady=10)
        self.promote_button.grid(column=3, row=2, padx=10, pady=10)
        self.snapshot_button.grid(column=3, row=3, padx=10, pady=10)
        self.linked_clone_button.grid(column=3, row=4, padx=10, pady=10)
        self.instant_clone_button.grid(column=3, row=5, padx=10, pady=10)
        self.freeze_button.grid(column=3, row=6, padx=10, pady=10)
        self.boot_bios_button.grid(column=3, row=7, padx=10, pady=10)

        # event handler
    def list_handle(self, event) -> None:
        # get selected index
        selected_index: tuple = self.vm_list.curselection()

        if not selected_index:
            selected_name: str = ""
        # get vm name from listbox
        else:
            selected_name: str = self.vm_list.get(selected_index)
        # get vm object from dictionary
        self.vm_object: vim.VirtualMachine = self.data.vmdict.get(selected_name)

        # get data from object about VM
        self.cpuvar.set(get_cpu_usage(self.vm_object))
        self.ramvar.set(get_memory_usage(self.vm_object))
        self.diskusevar.set(get_disk_usage(self.vm_object))
        if is_powered_on(self.vm_object):
            self.powervar.set("Yes")
        else:
            self.powervar.set("No")
        if is_frozen(self.vm_object):
            self.frozenvar.set("Yes")
        else:
            self.frozenvar.set("No")
        self.disknumvar.set(get_num_disks(self.vm_object))
        self.snapvar.set(get_num_snapshots(self.vm_object))
        self.diskfilevar.set(get_num_disk_files(self.vm_object))

        return



    # button handling
    def power_on_handler(self) -> None:
        power_on_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="Power On Sent")
        return

    def power_off_handler(self) -> None:
        poweroff_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="Power Off Sent")
        return

    def promote_handler(self) -> None:
        promote_clone(self.vm_object)
        showinfo(title="Info", message="Promote task sent")
        return

    def snapshot_handler(self) -> None:
        SnapshotWindow(data_set=self.data, vm=self.vm_object)
        return

    def freeze_handler(self) -> None:
        FreezeWindow(data=self.data, vm=self.vm_object)
        return

    def bios_boot_handler(self) -> None:
        bios_boot(vm=self.vm_object)
        return

    def linked_clone_handler(self) -> None:
        make_linked_clone(vmobj=self.vm_object)
        return

    def instant_clone_handler(self) -> None:
        make_instant_clone(vmobj=self.vm_object)
        return

    def update_list(self, data):
        self.vm_list.delete(0, 'end')

        # put new data
        for item in data:
            self.vm_list.insert('end', item)
        return

    def search_vms(self, event):
        val = event.widget.get()

        if val == '':
            data = self.data.vmdict.keys()
        else:
            data = list()
            for item in self.data.vmdict.keys():
                if val.lower() in item.lower():
                    data.append(item)
        self.update_list(data)
        return
