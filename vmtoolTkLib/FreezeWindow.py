from .FuncLib import *
from tkinter.ttk import Combobox


# define class
class FreezeWindow:
    def __init__(self, data: DataTree, vm: vim.VirtualMachine):
        self.dataset = data
        self.vm_object = vm

        # define script object
        class ScriptObj:
            def __init__(self):
                self.name: str = ""
                self.path: str = ""
                self.args: str = ""

        # define objects
        win_restart = ScriptObj()
        win_pwsh = ScriptObj()
        linux_freebsd = ScriptObj()

        win_restart.name = "Windows Restart"
        win_restart.path = 'C:\\Program Files\\VMware\\VMware Tools\\rpctool.exe'
        win_restart.args = '"instantclone.freeze" && shutdown /r /t 001'

        self.freeze_scripts = {win_restart.name: win_restart}
        # define widgets
        self.top = Toplevel(master=self.dataset.rootwin)
        self.freeze_label = Label(master=self.top, text="Freeze Script: ")
        self.freeze_combo = Combobox(master=self.top, values=list(self.freeze_scripts.keys()))
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
            script_name: str = self.freeze_combo.get()
            script_obj: ScriptObj = self.freeze_scripts.get(script_name)
            script_user: str = self.freeze_user.get()
            script_password: str = self.freeze_password.get()
            creds = vim.vm.guest.NamePasswordAuthentication(username=script_user, password=script_password)
            process_manager = self.dataset.content.guestOperationsManager
            program_spec: vim.vm.guest.ProcessManager.ProgramSpec = vim.vm.guest.ProcessManager.ProgramSpec()
            program_spec.programPath: str = script_obj.path
            program_spec.arguments: str = script_obj.args
            result_code = process_manager.processManager.StartProgramInGuest(vm=self.vm_object, auth=creds, spec=program_spec)
            if result_code > 0:
                showinfo(title="Info", message="Freeze Submitted")
            return
