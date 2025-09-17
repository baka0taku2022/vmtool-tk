from .FuncLib import *

class DlFromVmWindow:
    def __init__(self, vm:vim.VirtualMachine, data:DataTree):
        self.vm = vm
        self.dataset = data
        self.local_path = StringVar()

        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.vm_file_label = Label(master=self.top, text="File path on VM")
        self.vm_file_entry = Entry(master=self.top, width=40)
        self.vm_username_label = Label(master=self.top, text="VM Username")
        self.vm_username_entry = Entry(master=self.top, width=40)
        self.vm_password_label = Label(master=self.top, text="VM Password")
        self.vm_password_entry = Entry(master=self.top, width=40, show="*")
        self.dl_button = Button(master=self.top, text="Download File", command=lambda: self.dl_file_handler())

        # place widgets
        self.vm_file_label.grid(column=0, row=0, padx=10, pady=10)
        self.vm_file_entry.grid(column=1, row=0, padx=10, pady=10)
        self.vm_username_label.grid(column=0,row=1, padx=10, pady=10)
        self.vm_username_entry.grid(column=1, row=1, padx=10, pady=10)
        self.vm_password_label.grid(column=0, row=2, padx=10, pady=10)
        self.vm_password_entry.grid(column=1, row=2, padx=10, pady=10)
        self.dl_button.grid(column=0, row=3, padx=10, pady=10, columnspan=3)

    def dl_file_handler(self) -> None:
        if self.vm_file_entry.get() != "" and self.vm_username_entry.get() != "" and self.vm_password_entry.get() != "":
            download_file_from_vm(vmobj=self.vm, data=self.dataset, vm_file=self.vm_file_entry.get(),
                                  username=self.vm_username_entry.get(), password=self.vm_password_entry.get(),
                                  parent_obj=self.top)
            self.top.destroy()
        return
