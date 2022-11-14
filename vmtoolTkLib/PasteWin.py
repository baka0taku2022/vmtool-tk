from .FuncLib import *


class PasteWin:
    def __init__(self, data: DataTree) -> None:
        self.dataset: DataTree = data

        # create widgets
        self.top_window: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.vm_frame = Frame(master=self.top_window)
        self.search_box = Entry(master=self.vm_frame)
        self.search_box.bind(sequence='<KeyRelease>', func=self.search)
        self.vm_list: Listbox = Listbox(master=self.vm_frame, width=50, height=10)
        self.vm_list.insert(END, *sorted(list(self.dataset.vmdict.keys()), key=str.lower))
        self.vm_scroll = Scrollbar(master=self.vm_frame, orient=VERTICAL)
        self.vm_list.config(yscrollcommand=self.vm_scroll.set)
        self.pasted_text: Text = Text(master=self.top_window, width=80, height=24)
        self.paste_button: Button = Button(master=self.top_window, text='Paste to VM',
                                           command=lambda: self.click_handle())

        # place widgets
        self.search_box.pack(side=TOP)
        self.vm_list.pack(side=LEFT, fill=BOTH)
        self.vm_scroll.pack(side=RIGHT, fill=BOTH)
        self.vm_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10)
        self.pasted_text.grid(row=2, column=0, padx=10, pady=10)
        self.paste_button.grid(row=3, column=0, columnspan=1, pady=10)

    def click_handle(self):
        # get VM name
        selected_index: tuple = self.vm_list.curselection()
        vm_name: str = self.vm_list.get(selected_index)
        # lookup VM Object
        vm_object: vim.VirtualMachine = self.dataset.vmdict.get(vm_name)
        # get text from box
        raw_text: str = self.pasted_text.get(1.0, END)
        # translate text to usb_code
        trans_text: vim.UsbScanCodeSpec = str_to_usb(raw_text)
        # send codes to VM
        if trans_text is not None:
            vm_object.PutUsbScanCodes(trans_text)
        else:
            showerror(title="Error", message="Nothing to send.")
        return

    def search(self, event):
        val = event.widget.get()
        if val == '':
            data = self.dataset.vmdict.keys()
        else:
            data = list()
            for item in self.dataset.vmdict.keys():
                if val.lower() in item.lower():
                    data.append(item)
        self.update_list(sorted(list(data), key=str.lower))
        return

    def update_list(self, data):
        self.vm_list.delete(0, 'end')

        # put new data
        for item in data:
            self.vm_list.insert('end', item)
        return
