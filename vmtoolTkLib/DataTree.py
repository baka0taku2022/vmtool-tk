from tkinter import Tk

from pyVmomi import vim


class DataTree:
    """
    One dataset to rule them all. This object holds all of the common data used by the program. It is written in
    singleton format to avoid duplicating the data, and use of global variables.

    -=baka0taku=-
    """
    __instance__ = None

    def __init__(self) -> None:
        # constructor
        if DataTree.__instance__ is None:
            DataTree.__instance__ = self
            self.connection: vim.ServiceInstance
            self.connection = None
            self.content: vim.ServiceInstanceContent
            self.content = None
            self.rootwin: Tk
            self.rootwin = None
            self.vmobjlist: vim.view.ContainerView
            self.vmobjlist = None
            self.vmdict = dict()
            self.hostobjlist: vim.view.ContainerView
            self.hostobjlist = None
            self.hostdict = dict()
            self.datastoreobjlist: vim.view.ContainerView
            self.datastoreobjlist = None
            self.datastoredict = dict()
            self.networkobjlist: vim.view.ContainerView
            self.networkobjlist = None
            self.networkdict = dict()
            self.dvswitchobjlist: vim.view.ContainerView
            self.dvswitchobjlist = None
            self.dvswitchdict = dict()
            self.dvportgroupdict = dict()

        else:
            raise Exception("THERE CAN BE ONLY ONE!!!!")

    @staticmethod
    def get_instance():
        if not DataTree.__instance__:
            DataTree()
        return DataTree.__instance__
