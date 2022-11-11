from .FuncLib import *

class MigrateWindow:
    def __init__(self, data:DataTree, vmobj: vim.VirtualMachine):
        self.dataset = data
        self.vm = vmobj

        # Define widgets
        self.top: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.host_frame = Frame(master=self.top)
        self.host_list_label: Label = Label(master=self.top, text="Hosts:", padx=10, pady=10)
        self.host_list: Listbox = Listbox(master=self.host_frame, width=50, height=15)
        self.host_scroll = Scrollbar(master=self.host_frame, orient=VERTICAL)
        self.migrate_button = Button(master=self.top, width=50, text="Migrate VM", command=lambda: self.migrate_handler())

        # add hosts
        self.host_list.insert(END, *sorted(list(self.dataset.hostdict.keys())))

        # Place widgets
        self.host_list_label.grid(column=0, row=0, padx=10, pady=10)
        self.host_frame.grid(column=1, row=0, padx=10, pady=10, rowspan=5)
        self.host_list.pack(side=LEFT)
        self.host_scroll.pack(side=RIGHT, fill=BOTH)
        self.migrate_button.grid(column=0, columnspan=2, row=5, padx=10, pady=10)


    def migrate_handler(self):
        selected_index: tuple = self.host_list.curselection()
        selected_name: str = self.host_list.get(selected_index)
        host_object = self.dataset.hostdict.get(selected_name)
        migrate_vm(vmobj=self.vm, hostobj=host_object)
        showinfo(title="Info", message="Migration Task Sent")
        return
