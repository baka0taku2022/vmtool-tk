from tkinter.ttk import Combobox

import requests
from pyVmomi import vmodl

from .FuncLib import *


# define class
class FreezeWindow:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define script object
        class FreezeScript:
            def __init__(self):
                self.script_file_name = ''
                self.script_content = r''

        # instantiate script objects
        windows_reboot_script = FreezeScript()
        windows_fast_script = FreezeScript()
        linbsd_reboot_script = FreezeScript()

        # define scripts
        windows_reboot_script.script_file_name = "freeze.bat"
        windows_reboot_script.script_content = r'"C:\Program Files\VMware\VMware Tools\rpctool.exe" "instantclone.freeze" && shutdown /r /t 001'
        windows_fast_script.script_file_name = 'fast-freeze.ps1'
        windows_fast_script.script_content = r'cd "C:\Program Files\VMware\VMware Tools"; .\rpctool.exe "instantclone.freeze"; ping 127.0.0.1; Get-NetAdapter | Enable-NetAdapter; shutdown /l > output'
        linbsd_reboot_script.script_file_name = 'freeze.sh'
        linbsd_reboot_script.script_content = r'vmware-rpctool "instantclone.freeze" && init 6'

        # define script dictionary
        self.script_dictionary = {
            "Windows Restart Script": windows_reboot_script,
            "Windows Fast Script": windows_fast_script,
            "Linux/BSD Restart Script": linbsd_reboot_script
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
            script_file_obj: FreezeScript = self.script_dictionary.get(script_file_name)
            script_user: str = self.freeze_user.get()
            script_password: str = self.freeze_password.get()
            creds: vim.vm.guest.NamePasswordAuthentication = vim.vm.guest.NamePasswordAuthentication(
                username=script_user, password=script_password)
            # create File Attributes object
            file_attr_obj: vim.vm.guest.FileManager.FileAttributes = vim.vm.guest.FileManager.FileAttributes()
            # get file manager object
            file_manager: vim.vm.guest.FileManager = self.dataset.content.guestOperationsManager.fileManager
            # create temp directory on VM
            try:
                remote_dir = file_manager.CreateTemporaryDirectoryInGuest(vm=self.vm_object,
                                                                      auth=creds, prefix='', suffix='')
            except vim.fault.InvalidGuestLogin:
                showerror(title="Error", message="Invalid Login")
                return
            # make file path in guest
            vm_guest_id = self.vm_object.config.guestId
            vm_regex = r"win"
            if re.match(vm_regex, vm_guest_id):
                remote_path = remote_dir + '\\' + script_file_obj.script_file_name
            else:
                remote_path = remote_dir + '/' + script_file_obj.script_file_name
            # get file size
            file_size = len(script_file_obj.script_content)
            # initiate file transfer
            put_url = file_manager.InitiateFileTransferToGuest(vm=self.vm_object, auth=creds, guestFilePath=remote_path,
                                                               fileAttributes=file_attr_obj, fileSize=file_size,
                                                               overwrite=True)
            # push file to vm
            response = requests.put(url=put_url, data=script_file_obj.script_content, verify=False)
            if not response.status_code == 200:
                showerror(title="Error", message="File Transfer Failed.")

            # get process manager singleton
            process_manager = self.dataset.content.guestOperationsManager.processManager

            # set permissions for linux/bsd
            if not re.match(vm_regex, vm_guest_id):
                chmod_prog = "/bin/chmod"
                chmod_opts = "777 " + remote_path
                chmod_spec = vim.vm.guest.ProcessManager.ProgramSpec(programPath=chmod_prog, arguments=chmod_opts)
                process_manager.StartProgramInGuest(vm=self.vm_object, auth=creds, spec=chmod_spec)

            # define spec for program
            if script_file_name == "Windows Fast Script":
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=r"c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe", arguments=remote_path)
            else:
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(programPath=remote_path)

            # execute freeze script
            try:
                ret = process_manager.StartProgramInGuest(vm=self.vm_object, auth=creds, spec=program_spec)
            except vmodl.fault.SystemError:
                showerror(title="Error", message="Unknown system error in guest.")
                return
            except vim.fault.GuestPermissionDenied:
                showerror(title='Error', message='The guest authentication being used does not have sufficient permissions to perform the operation.')
                return
            if ret > 0:
                self.top.destroy()
                showinfo(title="Info", message="Freeze script started")
                return
