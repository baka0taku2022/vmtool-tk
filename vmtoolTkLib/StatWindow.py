"""
    GUI for status window - for the most part just creates the GUI window. Most of the heavy lifting is done in FuncLib.
    This file contains an exception. For some reason that I haven't ferreted out yet attempting to move the data parsing
    to FuncLib causes it to break with circular dependencies. Have to ignore errors where, on a production system, the
    landscape of Managed Objects is constantly changing. I know it is a hack, but it is best for now.

    -=baka0taku=-
"""
from pyVmomi import vmodl
from .FuncLib import *
from tkinter.ttk import Progressbar


class StatWindow:
    def __init__(self, data: DataTree) -> None:
        # assign data to object
        self.dataset: DataTree = data

        # StringVar for dynamic text in window
        self.tvar: StringVar = StringVar()
        self.tvar.set("Getting content from vCenter...")
        self.progress_var = DoubleVar()
        self.progress_var.set(0.0)

        # define widgets
        self.statWin: Toplevel = Toplevel(master=self.dataset.rootwin)
        self.container: Frame = Frame(master=self.statWin, padx=20, pady=20)
        self.statlab: Label = Label(master=self.container, textvariable=self.tvar)
        self.progress_bar = Progressbar(master=self.container, length=100, orient=HORIZONTAL, maximum=1,
                                        variable=self.progress_var,)
        # place widgets
        self.statlab.grid(row=0, column=0, pady=10, padx=10, sticky=E + W)
        self.progress_bar.grid(column=0, row=1, padx=10, pady=10)
        self.container.pack(expand=True, fill=BOTH, padx=30, pady=30)

        self.statWin.update()
        self.parse_data()
        self.statWin.destroy()

    def parse_data(self) -> None:
        # get all content
        self.dataset.content = self.dataset.connection.RetrieveContent()
        self.progress_var.set(1/7)
        self.statWin.update_idletasks()
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

        # Resource Pool set
        self.dataset.resourcepoollist = self.dataset.content.viewManager.CreateContainerView(self.dataset.content.rootFolder,
                                                                                             [vim.ResourcePool], True)

        self.progress_var.set(2 / 7)
        self.statWin.update_idletasks()
        # build dictionaries
        self.tvar.set("Building Host dictionary...")
        self.statlab.update()
        for host in self.dataset.hostobjlist.view:
            self.dataset.hostdict[host.name] = host
        self.progress_var.set(3 / 7)
        self.statWin.update_idletasks()
        self.tvar.set("Building Dataset dictionary...")
        self.statlab.update()

        for ds in self.dataset.datastoreobjlist.view:
            self.dataset.datastoredict[ds.name] = ds
        self.progress_var.set(4 / 7)
        self.statWin.update_idletasks()
        self.tvar.set("Building DVswitch dictionary...")
        self.statlab.update()

        for dvs in self.dataset.dvswitchobjlist.view:
            self.dataset.dvswitchdict[dvs.name] = dvs
        self.progress_var.set(5/7)
        self.statWin.update_idletasks()
        # build VM dict
        self.tvar.set("Building Dictionary for VMs...")
        self.statlab.update()
        obj_specs: list = list()

        for pool in self.dataset.resourcepoollist.view:
            self.dataset.resourcepooldict[pool.parent.name] = pool

        for vm in self.dataset.vmobjlist.view:
            obj_spec = vmodl.query.PropertyCollector.ObjectSpec(obj=vm)
            obj_specs.append(obj_spec)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        prop_set = vmodl.query.PropertyCollector.PropertySpec(all=False)
        prop_set.type = vim.VirtualMachine
        prop_set.pathSet = ['name']
        filter_spec.propSet = [prop_set]
        prop_collector = self.dataset.content.propertyCollector
        options = vmodl.query.PropertyCollector.RetrieveOptions()
        results = list()
        try:
            result = prop_collector.RetrievePropertiesEx([filter_spec], options)
            results.append(result)
            while result.token is not None:
                result = prop_collector.ContinueRetrievePropertiesEx(result.token)
                results.append(result)
            for result in results:
                for obj in result.objects:
                    self.dataset.vmdict[obj.propSet[0].val] = obj.obj
        except vmodl.fault.ManagedObjectNotFound:
            pass
        self.progress_var.set(6 / 7)
        self.statWin.update_idletasks()
        # build net dict
        self.tvar.set("Building Dictionary for Portgroups...")
        self.statlab.update()
        net_specs = list()
        for net in self.dataset.networkobjlist.view:
            net_spec = vmodl.query.PropertyCollector.ObjectSpec(obj=net)
            net_specs.append(net_spec)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = net_specs
        prop_set = vmodl.query.PropertyCollector.PropertySpec(all=False)
        prop_set.pathSet = ['name']
        prop_set.type = vim.Network
        filter_spec.propSet = [prop_set]
        prop_collector = self.dataset.content.propertyCollector
        options = vmodl.query.PropertyCollector.RetrieveOptions()
        try:
            result = prop_collector.RetrievePropertiesEx([filter_spec], options)
            results.clear()
            results.append(result)
            while result.token is not None:
                result = prop_collector.ContinueRetrievePropertiesEx(result.token)
                results.append(result)
            for result in results:
                for obj in result.objects:
                    self.dataset.dvportgroupdict[obj.propSet[0].val] = obj.obj
        except vmodl.fault.ManagedObjectNotFound:
            pass
        self.progress_var.set(7 / 7)
        self.statWin.update_idletasks()
        return
