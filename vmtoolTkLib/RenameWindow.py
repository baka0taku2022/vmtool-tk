# window for renaming VMs
from .FuncLib import *


class RenameWindow:
    def __init__(self, vmobj:vim.VirtualMachine, data:DataTree):
        self.vm = vmobj
        self.dataset = data

        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.rename_label = Label(master=self.top, text="New VM Name")
        self.rename_name = Entry(master=self.top, width=30)
        self.rename_button = Button(master=self.top, text="Rename", command=lambda: self.button_handler())

        # place widgets
        self.rename_label.grid(column=0, row=0, padx=10, pady=10)
        self.rename_name.grid(column=1, row=0, padx=10, pady=10)
        self.rename_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    # handler
    def button_handler(self):
        rename_obj(obj=self.vm, new_name=self.rename_name.get(), data=self.dataset)
        self.top.destroy()
        return
