"""
Simple window to give an option of freeze scripts and login credentials to freeze a VM
"""

from tkinter.ttk import Combobox

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
        windows_fast_script.script_content = r'cd "C:\Program Files\VMware\VMware Tools"; .\rpctool.exe "instantclone.freeze"; ping 127.0.0.1; Get-NetAdapter | Enable-NetAdapter > output'
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
            script_type: str = self.freeze_combo.get()
            script_file_obj: FreezeScript = self.script_dictionary.get(script_type)
            script_user: str = self.freeze_user.get()
            script_password: str = self.freeze_password.get()

            ret = freeze_vm(script_type=script_type,
                            user=script_user,
                            password=script_password,
                            file_name=script_file_obj.script_file_name,
                            file_content=script_file_obj.script_content,
                            data=self.dataset,
                            vm=self.vm_object)
            # a return value greater than 0 means success
            if ret > 0:
                self.top.destroy()
                showinfo(title="Info", message="Freeze script started")
                return
