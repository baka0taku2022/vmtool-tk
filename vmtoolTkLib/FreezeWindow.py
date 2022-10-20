import urllib3.exceptions

from .FuncLib import *
from tkinter.ttk import Combobox
import requests

# define class
class FreezeWindow:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define script dictionary
        self.script_dictionary = {
            "Windows Restart Script": "windows_restart.bat"
        }

        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.freeze_label = Label(master=self.top, text="Freeze Script: ")
        self.freeze_combo = Combobox(master=self.top, values=list(self.script_dictionary.keys()))
        self.freeze_user_label = Label(master=self.top, text="Username: ")
        self.freeze_user = Entry(master=self.top, width=25)
        self.freeze_password_label = Label(master=self.top, text="Password: ")
        self.freeze_password = Entry(master=self.top, width=25, show='*')
        self.freeze_button = Button(master=self.top, text="Send Freeze Script", command=lambda: freeze_button_handler())

        # place widgets
        self.freeze_label.grid(column=0, row=0, padx=10, pady=10)
        self.freeze_combo.grid(column=1, row=0, padx=10, pady=10)
        self.freeze_user_label.grid(column=0, row=1, pady=10, padx=10)
        self.freeze_user.grid(column=1, row=1, padx=10, pady=10)
        self.freeze_password_label.grid(column=0, row=2, pady=10, padx=10)
        self.freeze_password.grid(column=1, row=2, padx=10, pady=10)
        self.freeze_button.grid(column=0, row=3, padx=10, pady=10, rowspan=2, sticky='E')

        # handlers
        def freeze_button_handler() -> None:
            script_file_name: str = self.freeze_combo.get()
            script_file_path: str = self.script_dictionary.get(script_file_name)
            with open(script_file_path,"rb") as freeze_file:
                data_blob = freeze_file.read()
            script_user: str = self.freeze_user.get()
            script_password: str = self.freeze_password.get()
            creds: vim.vm.guest.NamePasswordAuthentication = vim.vm.guest.NamePasswordAuthentication(
                username=script_user, password=script_password)
            # create File Attributes object
            file_attr_obj: vim.vm.guest.FileManager.FileAttributes = vim.vm.guest.FileManager.FileAttributes()
            # get file manager object
            file_manager: vim.vm.guest.FileManager = self.dataset.content.guestOperationsManager.fileManager
            # create temp directory on VM
            remote_dir = file_manager.CreateTemporaryDirectoryInGuest(vm=self.vm_object,
                                                                      auth=creds, prefix='', suffix='')
            # make file path in guest
            remote_path = remote_dir + '\\' + script_file_path
            # get file size
            file_size = len(data_blob)
            # initiate file transfer
            put_url = file_manager.InitiateFileTransferToGuest(vm=self.vm_object, auth=creds, guestFilePath=remote_path,
                                                     fileAttributes=file_attr_obj, fileSize=file_size, overwrite=True)
            # push file to vm
            response = requests.put(url=put_url, data=data_blob, verify=False)
            if not response.status_code == 200:
                showerror(title="Error", message="File Transfer Failed.")

            # get process manager singleton
            process_manager = self.dataset.content.guestOperationsManager.processManager

            # define spec for program
            program_spec = vim.vm.guest.ProcessManager.ProgramSpec(programPath=remote_path)

            # execute freeze script
            ret = process_manager.StartProgramInGuest(vm=self.vm_object, auth=creds, spec=program_spec)
            if ret > 0:
                self.top.destroy()
                showinfo(title="Info", message="Freeze script started")
            print()

