from .FuncLib import *
from tkinter.ttk import Combobox


# define class
class FreezeWindow:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define freeze scripts
        self.freeze_scripts: dict = {
            "Windows Restart Script": '"c:\\Program Files\\VMware\\VMware Tools\\rpctool.exe" "instantclone.freeze" && shutdown /r /t 001',
            "Windows Powershell Script": 'cd "c:\\Program Files\\VMware\\VMware Tools"; .\\rpctool.exe "instantclone.freeze"; ping 127.0.0.1; Enable-NetAdapter ethernet0; shutdown /l',
            "Linux/FreeBSD restart": 'vmware-rpctool "instantclone.freeze" && init 6'
        }
        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.freeze_label = Label(master=self.top, text="Freeze Script: ")
        self.freeze_combo = Combobox(master=self.top, values=list(self.freeze_scripts.keys()))
        self.freeze_button = Button(master=self.top, text="Send Freeze Script", command=lambda: freeze_button_handler())

        # place widgets
        self.freeze_label.grid(column=0, row=0, padx=10, pady=10)
        self.freeze_combo.grid(column=1, row=0, padx=10, pady=10)
        self.freeze_button.grid(column=0, row=1, padx=10, pady=10, rowspan=2)

        # handlers
        def freeze_button_handler() -> None:
            script_type: str = self.freeze_combo.get()
            script_text: str = self.freeze_scripts.get(script_type)
            usb_codes: vim.UsbScanCodeSpec = str_to_usb(input=script_text)
            self.vm_object.PutUsbScanCodes(usb_codes)
