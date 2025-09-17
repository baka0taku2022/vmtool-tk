"""
A window to facilitate executing a script in a VM
"""
from .FuncLib import *

class ScriptExecuteWindow:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.script_label = Label(master=self.top, text="Enter a script path: ")
        self.script_entry = Entry(master=self.top, width=25)
        self.user_label = Label(master=self.top, text="Enter a Username: ")
        self.user_entry = Entry(master=self.top, width=25)
        self.password_label = Label(master=self.top, text="Enter a Password: ")
        self.password_entry = Entry(master=self.top, width=25, show="*")
        self.run_button = Button(master=self.top, text="Run Script >>", command=lambda: run_button_handler())

        # place widgets
        self.script_label.grid(column=0, row=0, padx=10, pady=10)
        self.script_entry.grid(column=1, row=0, pady=10, padx=10)
        self.user_label.grid(column=0, row=1, padx=10, pady=10)
        self.user_entry.grid(column=1, row=1, padx=10, pady=10)
        self.password_label.grid(column=0, row=2, padx=10, pady=10)
        self.password_entry.grid(column=1, row=2, padx=10, pady=10)
        self.run_button.grid(column=0, columnspan=2, row=3, pady=10, padx=10)

        def run_button_handler():
            execute_script(vm_object=self.vm_object, username=self.user_entry.get(), password=self.password_entry.get(),
                           script_name=self.script_entry.get(), data=self.dataset)
            self.top.destroy()
            return
