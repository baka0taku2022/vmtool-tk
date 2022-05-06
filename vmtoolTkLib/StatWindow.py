"""
    GUI for status window - for the most part just creates the GUI window. Most of the heavy lifting is done in FuncLib.
    This file contains an exception. For some reason that I haven't ferreted out yet attempting to move the data parsing
    to FuncLib causes it to break with circular dependencies. Have to ignore errors where, on a production system, the
    landscape of Managed Objects is constantly changing. I know it is a hack, but it is best for now.

    -=baka0taku=-
"""
import threading

from .FuncLib import *


class StatWindow:
    def __init__(self, data: DataTree) -> None:
        # assign data to object
        self.dataset: DataTree = data

        # StringVar for dynamic text in window
        self.tvar: StringVar = StringVar()
        self.tvar.set("Getting content from vCenter...")
        # create new window
        self.statWin: Toplevel = Toplevel(master=self.dataset.rootwin)

        # define widgets
        self.container: Frame = Frame(master=self.statWin, padx=20, pady=20)
        self.statlab: Label = Label(master=self.container, textvariable=self.tvar)
        # place widgets
        self.statlab.grid(row=0, column=0, pady=20, sticky=E + W)
        self.container.pack(expand=True, fill=BOTH, padx=30, pady=30)
        self.statWin.update()
        self.parse_data()
        sleep(1)
        self.statWin.destroy()

    def parse_data(self) -> None:
        # get all content
        self.dataset.content = self.dataset.connection.RetrieveContent()

        # get all Data Sets
        self.tvar.set("Getting Views From Server...")
        self.statlab.update()

        # VM set
        self.dataset.vmobjlist = self.dataset.content.viewManager.CreateContainerView(self.dataset.content.rootFolder,
                                                                                      [vim.VirtualMachine], True)
        # Hosts set
        self.dataset.hostobjlist = self.dataset.content.viewManager.CreateContainerView(self.dataset.content.rootFolder,
                                                                                        [vim.HostSystem], True)
        # Datastore set
        self.dataset.datastoreobjlist = self.dataset.content.viewManager.CreateContainerView(
            self.dataset.content.rootFolder,
            [vim.Datastore], True)

        # Network set
        self.dataset.networkobjlist = self.dataset.content.viewManager.CreateContainerView(
            self.dataset.content.rootFolder,
            [vim.Network], True)

        # DVSwitch set
        self.dataset.dvswitchobjlist = self.dataset.content.viewManager.CreateContainerView(
            self.dataset.content.rootFolder,
            [vim.DistributedVirtualSwitch], True)

        # build dictionaries
        self.tvar.set("Building Host dictionary...")
        self.statlab.update()
        for host in self.dataset.hostobjlist.view:
            self.dataset.hostdict[host.name] = host

        self.tvar.set("Building Dataset dictionary...")
        self.statlab.update()

        for ds in self.dataset.datastoreobjlist.view:
            self.dataset.datastoredict[ds.name] = ds

        self.tvar.set("Building DVswitch dictionary...")
        self.statlab.update()

        for dvs in self.dataset.dvswitchobjlist.view:
            self.dataset.dvswitchdict[dvs.name] = dvs

        # build VM dict
        def vmdict_builder(vmobjlst: list, new_dict: dict):
            for vm in vmobjlst:
                try:
                    new_dict[vm.name] = vm
                except pyVmomi.vmodl.fault.ManagedObjectNotFound:
                    pass

        # build net dict
        def netdict_builder(net_obj_lst: list, new_dvpg_dict: dict, new_net_dict: dict):
            for net in net_obj_lst:
                if type(net) is vim.dvs.DistributedVirtualPortgroup:
                    try:
                        new_dvpg_dict[net.name] = net
                    except pyVmomi.vmodl.fault.ManagedObjectNotFound:
                        pass
                else:
                    try:
                        new_net_dict[net.name] = net
                    except pyVmomi.vmodl.fault.ManagedObjectNotFound:
                        pass

        # define threads
        t1 = threading.Thread(target=vmdict_builder, args=(self.dataset.vmobjlist.view, self.dataset.vmdict))
        t2 = threading.Thread(target=netdict_builder, args=(self.dataset.networkobjlist.view,
                                                            self.dataset.dvportgroupdict, self.dataset.networkdict))

        self.tvar.set("Building Dictionaries for Portgroups and VMs...")
        self.statlab.update()

        # start threads
        t1.start()
        t2.start()

        # wait for threads to finish
        t1.join()
        t2.join()

        return
