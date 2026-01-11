"""
PortgroupWindow.py - for functions related to portgroups.
"""
from .FuncLib import *

class PortgroupWindow:
    def __init__(self, data: DataTree):
        self.datatree = data

        # Create widgets
        self.top_window: Toplevel = Toplevel(master=self.datatree.rootwin)
        self.cleanup_button: Button = Button(master=self.top_window, text="Clean up DVPortgroups",
                                             command=lambda: self.clean_portgroups())

        # Place Widgets
        self.cleanup_button.grid(column=0, row=0, padx=10, pady=10)


    def clean_portgroups(self):
        portgroups: list[str] = self.datatree.dvportgroupdict.keys()
        temp_portgroups: list[str] = list()
        to_delete: list[vim.Network] = list()
        # create list of portgroups that start with prod_ or staging_
        for pg in portgroups:
            if pg.__contains__("prod_") or pg.__contains__("staging_"):
                temp_portgroups.append(pg)

        # filter list to only contain portgroups that have 0 VMs
        for pg in temp_portgroups:
            temp_obj: vim.Network = self.datatree.dvportgroupdict[pg]
            if len(temp_obj.vm) == 0:
                to_delete.append(temp_obj)

        # delete portgroups
        for obj in to_delete:
            obj.Destroy()
        return
