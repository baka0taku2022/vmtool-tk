"""
Window to display critical VM stats for a selected VM
CPU usage, RAM usage, Disk Usage, Frozen?, Power state?, Snapshots?, VMDK Files
"""
from .FreezeWindow import FreezeWindow
from .FuncLib import *
from .RenameWindow import RenameWindow
from .SnapshotWindow import SnapshotWindow
from .VmTaskWindow import VmTaskWindow
from .CloneRegWin import CloneRegWin
from .MigrateWindow import MigrateWindow


class VmStatusWindow:
    def __init__(self, dataset: DataTree):
        self.vm_object = None
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
        self.swapped_memory_var: StringVar = StringVar()
        self.host_name_var: StringVar = StringVar()
        self.num_processors_var: StringVar = StringVar()
        self.total_ram_var: StringVar = StringVar()
        self.perf_counters: StringVar = StringVar()
        self.evc_mode: StringVar = StringVar()

        # define widgets
        self.top_level = Toplevel(master=self.data.rootwin)
        self.vm_frame = Frame(master=self.top_level)
        self.vm_list = Listbox(master=self.vm_frame, width=50, height=15)
        # event binding
        self.vm_list.bind('<<ListboxSelect>>', self.list_handle)
        self.vm_scroll = Scrollbar(master=self.vm_frame, orient=VERTICAL)
        self.cpu_label = Label(master=self.top_level, text="CPU Usage")
        self.cpu_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.cpuvar, width=15)
        self.mem_label = Label(master=self.top_level, text="Memory Usage")
        self.mem_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.ramvar, width=15)
        self.disk_usage_label = Label(master=self.top_level, text="Disk Usage")
        self.disk_usage = Label(master=self.top_level, relief=SUNKEN, textvariable=self.diskusevar, width=15)
        self.power_label = Label(master=self.top_level, text="Powered on?")
        self.power = Label(master=self.top_level, relief=SUNKEN, textvariable=self.powervar, width=15)
        self.frozen_label = Label(master=self.top_level, text="Frozen?")
        self.frozen = Label(master=self.top_level, relief=SUNKEN, textvariable=self.frozenvar, width=15)
        self.num_disks_label = Label(master=self.top_level, text="Number of Disks")
        self.num_disks = Label(master=self.top_level, relief=SUNKEN, textvariable=self.disknumvar, width=15)
        self.num_snapshots_label = Label(master=self.top_level, text="Number of Snapshots")
        self.num_snapshots = Label(master=self.top_level, relief=SUNKEN, textvariable=self.snapvar, width=15)
        self.num_disk_files_label = Label(master=self.top_level, text="Number of Disk Files/Disk")
        self.num_disk_files = Label(master=self.top_level, relief=SUNKEN, textvariable=self.diskfilevar, width=15)
        self.swapped_memory_label = Label(master=self.top_level, text="Swapped Memory")
        self.swapped_memory = Label(master=self.top_level, relief=SUNKEN, textvariable=self.swapped_memory_var, width=15)
        self.host_name_label = Label(master=self.top_level, text="Host Name")
        self.host_name = Label(master=self.top_level, relief=SUNKEN, textvariable=self.host_name_var, width=15)
        self.num_processors_label = Label(master=self.top_level, text="Number of CPU")
        self.num_processors = Label(master=self.top_level, relief=SUNKEN, textvariable=self.num_processors_var, width=15)
        self.total_ram_label = Label(master=self.top_level, text="Total RAM")
        self.total_ram = Label(master=self.top_level, relief=SUNKEN, textvariable=self.total_ram_var, width=15)
        self.perf_counters_label = Label(master=self.top_level, text="Performance Counters")
        self.perf_counters_val = Label(master=self.top_level, relief=SUNKEN, textvariable=self.perf_counters, width=15)
        self.evc_mode_label = Label(master=self.top_level, text="EVC Mode")
        self.evc_mode_val = Label(master=self.top_level, relief=SUNKEN, textvariable=self.evc_mode, width=15)

        self.power_on_button = Button(master=self.top_level, text="Power On", command=lambda: self.power_on_handler(),
                                      width=20)
        self.power_off_button = Button(master=self.top_level, text="Power Off",
                                       command=lambda: self.power_off_handler(), width=20)
        self.promote_button = Button(master=self.top_level, text="Promote", command=lambda: self.promote_handler(),
                                     width=20)
        self.snapshot_button = Button(master=self.top_level, text="Create Snapshot",
                                      command=lambda: self.snapshot_handler(), width=20)
        self.linked_clone_button = Button(master=self.top_level, text="Linked Clone",
                                          command=lambda: self.linked_clone_handler(), width=20)
        self.instant_clone_button = Button(master=self.top_level, text="Instant Clone",
                                           command=lambda: self.instant_clone_handler(), width=20)
        self.freeze_button = Button(master=self.top_level, text="Freeze", command=lambda: self.freeze_handler(),
                                    width=20)
        self.boot_bios_button = Button(master=self.top_level, text="BIOS Boot",
                                       command=lambda: self.bios_boot_handler(), width=20)
        self.reset_button = Button(master=self.top_level, text="Reset", command=lambda: self.reset_button_handler(),
                                   width=20)
        self.reboot_button = Button(self.top_level, text="Reboot Guest", command=lambda: self.reboot_button_handler,
                                    width=20)
        self.shutdown_button = Button(self.top_level, text="Shutdown Guest",
                                      command=lambda: self.shutdown_button_handler, width=20)
        self.screen_resolution_button = Button(self.top_level, text="Screen Resolution",
                                               command=lambda: self.screen_resolution_handler(), width=20)
        self.tasks_button = Button(master=self.top_level, text="Recent Tasks", command=lambda: self.tasks_handler(),
                                   width=20)
        self.rename_button = Button(master=self.top_level, text="Rename", command=lambda: self.rename_handler(),
                                    width=20)
        self.search_box = Entry(master=self.vm_frame, width=50)
        self.search_box.bind(sequence='<KeyRelease>', func=self.search_vms)
        self.refresh_button = Button(master=self.top_level, text="Refresh VMs", width=50,
                                     command=lambda: self.refresh_handle())
        self.clone_button = Button(master=self.top_level, text="Clone", width=20, command=lambda: self.clone_handler())
        self.migrate_button = Button(master=self.top_level, text="Migrate", width=20,
                                     command=lambda: self.migrate_handler())
        self.delete_button = Button(master=self.top_level, text="Delete", width=20,
                                    command=lambda: self.delete_handler())
        self.console_button = Button(master=self.top_level, text="VMRC Console", command=lambda: self.console_handler(),
                                     width=20)

        # define scrollbar properties
        self.vm_list.config(yscrollcommand=self.vm_scroll.set)
        self.vm_scroll.config(command=self.vm_list.yview)

        # add VMs to list
        self.vm_list.insert(END, *sorted(list(self.data.vmdict.keys())))

        # place widgets
        self.vm_frame.grid(column=0, row=0, padx=20, pady=20, rowspan=10)
        self.search_box.pack(side=TOP)
        self.vm_list.pack(side=LEFT)
        self.vm_scroll.pack(side=RIGHT, fill=BOTH)
        self.refresh_button.grid(column=0, row=11, padx=10, pady=10)
        self.cpu_label.grid(column=1, row=0, padx=10, pady=10)
        self.cpu_usage.grid(column=2, row=0, padx=10, pady=10)
        self.num_processors_label.grid(column=1, row=1, padx=10, pady=10)
        self.num_processors.grid(column=2, row=1, padx=10, pady=10)
        self.mem_label.grid(column=1, row=2, padx=10, pady=10)
        self.mem_usage.grid(column=2, row=2, padx=10, pady=10)
        self.total_ram_label.grid(column=1, row=3, padx=10, pady=10)
        self.total_ram.grid(column=2, row=3, padx=10, pady=10)
        self.disk_usage_label.grid(column=1, row=4, padx=10, pady=10)
        self.disk_usage.grid(column=2, row=4, padx=10, pady=10)
        self.power_label.grid(column=1, row=5, padx=10, pady=10)
        self.power.grid(column=2, row=5, padx=10, pady=10)
        self.frozen_label.grid(column=1, row=6, padx=10, pady=10)
        self.frozen.grid(column=2, row=6, padx=10, pady=10)
        self.num_disks_label.grid(column=1, row=7, padx=10, pady=10)
        self.num_disks.grid(column=2, row=7, padx=10, pady=10)
        self.num_snapshots_label.grid(column=1, row=8, padx=10, pady=10)
        self.num_snapshots.grid(column=2, row=8, padx=10, pady=10)
        self.num_disk_files_label.grid(column=1, row=9, padx=10, pady=10)
        self.num_disk_files.grid(column=2, row=9, padx=10, pady=10)
        self.swapped_memory_label.grid(column=1, row=10, padx=10, pady=10)
        self.swapped_memory.grid(column=2, row=10, padx=10, pady=10)
        self.host_name_label.grid(column=1, row=11, padx=10, pady=10)
        self.host_name.grid(column=2, row=11, padx=10, pady=10)
        self.perf_counters_label.grid(column=1, row=12, padx=10, pady=10)
        self.perf_counters_val.grid(column=2, row=12, padx=10, pady=10)
        self.evc_mode_label.grid(column=1, row=13, padx=10, pady=10)
        self.evc_mode_val.grid(column=2, row=13, padx=10, pady=10)
        self.power_on_button.grid(column=3, row=0, padx=10, pady=10)
        self.power_off_button.grid(column=3, row=1, padx=10, pady=10)
        self.promote_button.grid(column=3, row=2, padx=10, pady=10)
        self.snapshot_button.grid(column=3, row=3, padx=10, pady=10)
        self.linked_clone_button.grid(column=3, row=4, padx=10, pady=10)
        self.instant_clone_button.grid(column=3, row=5, padx=10, pady=10)
        self.freeze_button.grid(column=3, row=6, padx=10, pady=10)
        self.boot_bios_button.grid(column=3, row=7, padx=10, pady=10)
        self.reset_button.grid(column=3, row=8, padx=10, pady=10)
        self.reboot_button.grid(column=3, row=9, pady=10, padx=10)
        self.shutdown_button.grid(column=3, row=10, padx=10, pady=10)
        self.screen_resolution_button.grid(column=3, row=11, padx=10, pady=10)
        self.tasks_button.grid(column=4, row=0, padx=10, pady=10)
        self.rename_button.grid(column=4, row=1, padx=10, pady=10)
        self.clone_button.grid(column=4, row=2, padx=10, pady=10)
        self.migrate_button.grid(column=4, row=3, padx=10, pady=10)
        self.delete_button.grid(column=4, row=4, padx=10, pady=10)
        self.console_button.grid(column=4, row=5, padx=10, pady=10)

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
        try:
            self.cpuvar.set(get_cpu_usage(self.vm_object))
        except vmodl.fault.ManagedObjectNotFound:
            showerror(title="Error", message="Object not found. Refresh Window")
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
        self.swapped_memory_var.set(get_swapped_ram(vmobj=self.vm_object))
        self.host_name_var.set(get_host_name(vmobj=self.vm_object))
        self.num_processors_var.set(get_num_processors(vmobj=self.vm_object))
        self.total_ram_var.set(get_total_mem(vmobj=self.vm_object))
        self.perf_counters.set(get_performance_counters(vmobj=self.vm_object))
        self.evc_mode.set(get_evc_mode(vmobj=self.vm_object))

        return

    # button handling
    def power_on_handler(self) -> None:
        if self.vm_object is None:
            return
        power_on_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="Power On Sent")
        return

    def power_off_handler(self) -> None:
        if self.vm_object is None:
            return
        poweroff_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="Power Off Sent")
        return

    def promote_handler(self) -> None:
        if self.vm_object is None:
            return
        promote_clone(self.vm_object)
        showinfo(title="Info", message="Promote task sent")
        return

    def snapshot_handler(self) -> None:
        if self.vm_object is None:
            return
        SnapshotWindow(data_set=self.data, vm=self.vm_object)
        return

    def freeze_handler(self) -> None:
        if self.vm_object is None:
            return
        FreezeWindow(data=self.data, vm=self.vm_object)
        return

    def bios_boot_handler(self) -> None:
        if self.vm_object is None:
            return
        bios_boot(vm=self.vm_object)
        showinfo(title="Info", message="BIOS Boot Sent")
        return

    def linked_clone_handler(self) -> None:
        if self.vm_object is None:
            return
        make_linked_clone(vmobj=self.vm_object)
        showinfo(title="Info", message="Linked Clone Task Sent")
        return

    def instant_clone_handler(self) -> None:
        if self.vm_object is None:
            return
        make_instant_clone(vmobj=self.vm_object)
        showinfo(title="Info", message="Instant Clone Task Sent")
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
        self.update_list(sorted(data))
        return

    def reset_button_handler(self):
        if self.vm_object is None:
            return
        reset_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="VM Reset Sent")
        return

    def reboot_button_handler(self):
        if self.vm_object is None:
            return
        reboot_vm_guest(vmobj=self.vm_object)
        showinfo(title="Info", message="Guest Reboot Sent")
        return

    def shutdown_button_handler(self):
        if self.vm_object is None:
            return
        shutdown_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="Guest Shutdown Sent")
        return

    def screen_resolution_handler(self):
        if self.vm_object is None:
            return
        try:
            set_screen_resolution(vmobj=self.vm_object, width=1280, height=960)
            showinfo(title="Info", message="Resolution Set")
            return
        except vim.fault.ToolsUnavailable:
            showerror(title="Error", message="VM Tools not available.")
        except vmodl.fault.SystemError:
            showerror(title="Error", message="System Error")
        except vmodl.fault.NotSupported:
            showerror(title="Error", message='The operation is not supported on the object.')

    def tasks_handler(self) -> None:
        if self.vm_object is None:
            return
        VmTaskWindow(data=self.data, vmobj=self.vm_object)
        return

    def rename_handler(self):
        if self.vm_object is None:
            return
        RenameWindow(vmobj=self.vm_object, data=self.data)
        self.search_box.delete(0, END)
        self.vm_list.delete(0, END)
        for item in sorted(list(self.data.vmdict.keys())):
            self.vm_list.insert(END, item)
        return

    def refresh_handle(self):
        self.data.clear_data()
        StatWindow(data=self.data).parse_data()
        self.search_box.delete(0, END)
        self.vm_list.delete(0, END)
        for item in sorted(list(self.data.vmdict.keys())):
            self.vm_list.insert(END, item)
        return


    def clone_handler(self):
        if self.vm_object is None:
            return
        CloneRegWin(data=self.data, vm=self.vm_object)
        return


    def migrate_handler(self):
        if self.vm_object is None:
            return
        MigrateWindow(data=self.data, vmobj=self.vm_object)
        return


    def delete_handler(self):
        if self.vm_object is None:
            return
        delete_vm(vmobj=self.vm_object)
        showinfo(title="Info", message="VM Deleted")
        return

    def console_handler(self):
        get_vmrc_url(vmobj=self.vm_object, data=self.data)
        pass