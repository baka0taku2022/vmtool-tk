from tkinter.ttk import Combobox

from .FuncLib import *


class PasteWin:
    def __init__(self, data: DataTree) -> None:
        self.dataset: DataTree = data

        # create widgets
        self.top_window: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.vm_picker_label: Label = Label(master=self.top_window, text='Select a VM to paste into:')
        self.vm_picker: Combobox = Combobox(master=self.top_window, values=sorted(list(self.dataset.vmdict.keys())))
        self.pasted_text: Text = Text(master=self.top_window, width=80, height=24)
        self.paste_button: Button = Button(master=self.top_window, text='Paste to VM', command=lambda: self.click_handle())

        # place widgets
        self.vm_picker_label.grid(row=0, column=0)
        self.vm_picker.grid(row=1, column=0, padx=10)
        self.pasted_text.grid(row=2, column=0, padx=10, pady=10)
        self.paste_button.grid(row=3, column=0, columnspan=1, pady=10)

    def click_handle(self):
        print("button clicked")
        return
