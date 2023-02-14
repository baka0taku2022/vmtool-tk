from .FuncLib import *

class MigrateWindow:
    def __init__(self, data:DataTree, vmobj: vim.VirtualMachine):
        self.dataset = data
        self.vm = vmobj
        self.button_var: StringVar = StringVar()
        self.button_var.set("Next")
        self.label_var: StringVar = StringVar()
        self.label_var.set("Cluster:")
        self.host_object = None
        self.resource_pool = None
        self.dsdict = dict()

        # Define widgets
        self.top: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.host_frame = Frame(master=self.top)
        self.host_list_label: Label = Label(master=self.top, textvariable=self.label_var, padx=10, pady=10)
        self.host_list: Listbox = Listbox(master=self.host_frame, width=50, height=15)
        self.host_scroll = Scrollbar(master=self.host_frame, orient=VERTICAL)
        self.migrate_button = Button(master=self.top, width=50, textvariable=self.button_var, command=lambda: self.migrate_handler1())

        # add hosts
        self.host_list.insert(END, *sorted(list(self.dataset.resourcepooldict.keys())))

        # Place widgets
        self.host_list_label.grid(column=0, row=0, padx=10, pady=10)
        self.host_frame.grid(column=1, row=0, padx=10, pady=10, rowspan=5)
        self.host_list.pack(side=LEFT)
        self.host_scroll.pack(side=RIGHT, fill=BOTH)
        self.migrate_button.grid(column=0, columnspan=2, row=5, padx=10, pady=10)


    def migrate_handler1(self):
        selected_index: tuple = self.host_list.curselection()
        selected_name: str = self.host_list.get(selected_index)
        self.resource_pool = self.dataset.resourcepooldict.get(selected_name)
        self.label_var.set("Hosts:")
        self.host_list.delete(0, END)
        for h in self.resource_pool.parent.host:
            self.host_list.insert(END, h.name)
        self.migrate_button.config(command=lambda: self.migrate_handler2())
        self.top.update_idletasks()
        return

    def migrate_handler2(self):
        selected_index: tuple = self.host_list.curselection()
        selected_name: str = self.host_list.get(selected_index)
        self.host_object = self.dataset.hostdict.get(selected_name)
        self.button_var.set("Migrate VM")
        self.label_var.set("Datastores:")
        self.host_list.delete(0, END)
        for ds in self.host_object.datastore:
            self.dsdict[ds.name] = ds
            self.host_list.insert(END, ds.name)
        self.migrate_button.config(command=lambda: self.migrate_handler3())
        self.top.update_idletasks()
    def migrate_handler3(self):
        selected_index: tuple = self.host_list.curselection()
        selected_name: str = self.host_list.get(selected_index)
        datastore = self.dsdict.get(selected_name)
        result = migrate_vm(vmobj=self.vm, hostobj=self.host_object, dsobj=datastore, pool=self.resource_pool)
        if result:
            showinfo(title="Info", message="Migration Task Sent")
        self.top.destroy()
        return