from .FuncLib import *

class SnapshotWindow:
    def __init__(self, data_set: DataTree, vm: vim.VirtualMachine) -> None:
        self.data = data_set
        self.memory_var = BooleanVar()
        self.quiesce_var = BooleanVar()
        self.virtual_machine = vm

        # define widgets
        self.top = Toplevel(master=self.data.rootwin)
        self.snapshot_name_label = Label(master=self.top, text="Name: ")
        self.snapshot_name = Entry(master=self.top)
        self.snapshot_description_label = Label(master=self.top, text="Description: ")
        self.snapshot_description = Text(master=self.top)
        self.snapshot_memory_label = Label(master=self.top, text="Memory?: ")
        self.snapshot_memory = Checkbutton(master=self.top, variable=self.memory_var)
        self.quiesce_disks_label = Label(master=self.top, text="Quiesce?: ")
        self.quiesce_disks = Checkbutton(master=self.top, variable=self.quiesce_var)
        self.send_button = Button(master=self.top, text="Create Snapshot", command=lambda: send_button_handler())

        # place widgets
        self.snapshot_name_label.grid(column=0, row=0, pady=10, padx=10)
        self.snapshot_description_label.grid(column=0, row=1, pady=10, padx=10)
        self.snapshot_memory_label.grid(column=0, row=2, pady=10, padx=10)
        self.quiesce_disks_label.grid(column=0, row=3, pady=10, padx=10)
        self.snapshot_name.grid(column=1, row=0, pady=10, padx=10)
        self.snapshot_description.grid(column=1, row=1, pady=10, padx=10)
        self.snapshot_memory.grid(column=1, row=2, pady=10, padx=10)
        self.quiesce_disks.grid(column=1, row=3, pady=10, padx=10)
        self.send_button.grid(column=0, row=4, padx=10, pady=10, columnspan=2)

        # button handler
        def send_button_handler() -> None:
            if self.snapshot_name.get() != "":
                create_snapshot(
                    snapshot_name=self.snapshot_name.get(), snapshot_desc=self.snapshot_description.get(1.0, END),
                    snapshot_memory=self.memory_var.get(), snapshot_quiesce=self.quiesce_var.get(),
                    vm=self.virtual_machine)
                self.top.destroy()
                showinfo(title="Info", message="Snapshot Created")
            else:
                showwarning(title="Error", message="Please enter a snapshot name.")
            return
