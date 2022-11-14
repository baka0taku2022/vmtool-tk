"""
Simple window for a normal clone operation
"""

# imports
from .FuncLib import *

class CloneRegWin:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.clone_label = Label(master=self.top, text="Enter Clone Name: ")
        self.clone_name = Entry(master=self.top, width=50)
        self.clone_button = Button(master=self.top, text="Clone VM", width=67, command=lambda: self.button_handler())

        # Add original name to Entry box
        self.clone_name.insert(index=END, string=self.vm_object.name)

        # place widgets
        self.clone_label.grid(column=0, row=0, padx=10, pady=10)
        self.clone_name.grid(column=1, row=0, padx=10, pady=10)
        self.clone_button.grid(column=0, row=1, padx=10, pady=10, columnspan=2)

    # button Handler
    def button_handler(self):
        clone_vm(vmobj=self.vm_object, vm_name=self.clone_name.get())
        showinfo(title="Info", message="Clone Task Sent")
        self.top.destroy()
        return
