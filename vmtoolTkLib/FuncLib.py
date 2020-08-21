"""
The purpose of this file is to house all of the general functions for the program so that things only have to be
written once.

-=baka0taku=-
"""
import random
import ssl
from socket import gaierror
from time import sleep
from tkinter import *
from tkinter.messagebox import *

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from .DataTree import DataTree
from .StatWindow import StatWindow


# establish connection
def make_connection(dataset: DataTree, fqdn: str, user: str, passwd: str) -> bool:
    try:
        s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        dataset.connection = SmartConnect(host=fqdn, user=user, pwd=passwd, sslContext=s)
        return True
    except (gaierror, vim.fault.InvalidLogin):
        showerror(title='Error', message='Failed to connect. Please check entries and try again...')
        dataset.connection = None
        return False
    except Exception as e:
        showerror(title='Error', message=e)
        dataset.connection = None
        return False


# cleanup
def cleanup(dataset: DataTree, rootwin: Tk) -> None:
    # disconnect from server
    if dataset.connection:
        Disconnect(dataset.connection)
    # quit program
    rootwin.quit()
    return


# move boxes
def mv_lstbox(orig_list: Listbox, dest_list: Listbox) -> None:
    vms = list()
    # get all selected items
    selected = orig_list.curselection()
    for item in selected:
        vms.append(orig_list.get(item))
    # delete all selected items from original list
    contents = list(orig_list.get(0, END))
    for vm in vms:
        contents.remove(vm)
    # clear contents of listbox and insert trimmed list
    orig_list.delete(0, END)
    orig_list.insert(END, *contents)
    dest_list.insert(END, *vms)
    return


# refresh lists
def refresh_lists(orig_list: Listbox, dataset: DataTree, list_type: str, dest_list: Listbox = None) -> None:
    # clear both lists
    orig_list.delete(0, END)
    if dest_list is not None:
        dest_list.delete(0, END)
    # parse server data
    StatWindow(data=dataset).parse_data()
    # refresh datasets
    if list_type == "vm":
        orig_list.insert(END, *sorted(list(dataset.vmdict.keys())))
    elif list_type == "pg":
        orig_list.insert(END, *sorted(list(dataset.dvportgroupdict.keys())))
    return


# send cloning tasks
def send_clone_task(names: list, data: DataTree, typeclone: str) -> bool:
    dataset = data
    vmnames = names
    vmobjs = list()
    # get vm objects from dataset
    for name in vmnames:
        vmobjs.append(dataset.vmdict[name])
    # check for existing clones

    # send clone task(s) to vCenter
    if typeclone == "linked":
        alreadyclones = list()
        for vm in vmobjs:
            if is_clone(vm=vm):
                alreadyclones.append(vm.name)
        if len(alreadyclones) > 0:
            dowecontinue = askyesno(title='Warning',
                                    message=",\n".join(
                                        alreadyclones) + '\nThese machines are already clones. Continue?')
            if not dowecontinue:
                return False
        for cl in vmobjs:
            if not make_linked_clone(cl):
                return False
    elif typeclone == "instant":
        # check powered on
        for vm in vmobjs:
            if not is_powered_on(vm=vm):
                showerror(title="Error",
                          message=vm.name + " is not powered on. VMs must be powered on to Instant Clone")
                return False
        # check frozen
        notfrozen = list()
        cont = None
        for vm in vmobjs:
            if not is_frozen(vm=vm):
                notfrozen.append(vm.name)
        if len(notfrozen) > 0:
            cont = askyesno(title="Continue?",
                            message=",\n".join(notfrozen) + "\n These machines are not frozen. Continue?")
            # make instant clones
            if cont:
                for vm in vmobjs:
                    if not make_instant_clone(vmobj=vm):
                        return False
        # make instant clones
        else:
            for vm in vmobjs:
                if not make_instant_clone(vmobj=vm):
                    return False

    showinfo(title='Information', message=str(len(vmobjs)) + ' clone jobs sent to server.')
    return True


# send promote tasks
def send_promote_task(names: list, data: DataTree) -> bool:
    vmnames = names
    dataset = data
    vmobjs = list()
    for name in vmnames:
        vmobjs.append(dataset.vmdict[name])
    # check for power on
    for vm in vmobjs:
        if not str(vm.runtime.powerState) == "poweredOff":
            showerror(title='Error',
                      message=vm.name + ' is not in a Powered Off state. Power it off before attempting to promote')
            return False
        if not promote_clone(vmobj=vm):
            return False
    return True


# send clone portgroup task
def send_portgroup_clone_task(name: str, data: DataTree) -> bool:
    parentname = name
    dataset = data
    parentobj = dataset.dvportgroupdict[parentname]
    if not clone_dvportgroup(pgobj=parentobj):
        return False
    return True


# create linked clone
def make_linked_clone(vmobj: vim.VirtualMachine) -> bool:
    clonefolder = vmobj.parent
    clonename = vmobj.name + 'LC-' + str(random.randint(100000, 999999))
    clonespec = vim.VirtualMachineCloneSpec()
    try:
        clonespec.snapshot = vmobj.snapshot.currentSnapshot
    except AttributeError:
        showerror(title="Error", message="The VM " + vmobj.name + " does not have a snapshot. Please remove from list.")
        return False
    clonespec.location = vim.VirtualMachineRelocateSpec()
    movetype = vim.VirtualMachineRelocateDiskMoveOptions()
    clonespec.location.diskMoveType = movetype.createNewChildDiskBacking
    tsk = vmobj.CloneVM_Task(clonefolder, clonename, clonespec)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# create instant clone
def make_instant_clone(vmobj: vim.VirtualMachine) -> bool:
    # set InstantClone Specifications
    inst_spec = vim.VirtualMachineInstantCloneSpec()
    inst_spec.name = vmobj.name + "IC-" + str(random.randint(100000, 999999))
    inst_spec.location = vim.VirtualMachineRelocateSpec()
    # make Instant Clone
    inst_spec.location.folder = vmobj.parent
    tsk = vmobj.InstantClone_Task(inst_spec)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# promote VM
def promote_clone(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.PromoteDisks_Task(unlink=True, disks=None)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# clone dvportgroup
def clone_dvportgroup(pgobj: vim.dvs.DistributedVirtualPortgroup) -> bool:
    parentcfg = pgobj.config
    clonecfg = vim.DVPortgroupConfigSpec()
    randnumext = str(random.randint(100000, 999999))
    clonename = parentcfg.name + '-' + randnumext
    # get DVPortgroupConfigSpec from parent
    clonecfg.autoExpand = parentcfg.autoExpand
    clonecfg.backingType = parentcfg.backingType
    clonecfg.configVersion = parentcfg.configVersion
    clonecfg.defaultPortConfig = parentcfg.defaultPortConfig
    clonecfg.description = parentcfg.description
    clonecfg.dynamicProperty = parentcfg.dynamicProperty
    clonecfg.dynamicType = parentcfg.dynamicType
    clonecfg.logicalSwitchUuid = parentcfg.logicalSwitchUuid
    clonecfg.name = clonename
    clonecfg.numPorts = parentcfg.numPorts
    clonecfg.policy = parentcfg.policy
    clonecfg.portNameFormat = parentcfg.portNameFormat
    clonecfg.scope = parentcfg.scope
    clonecfg.segmentId = parentcfg.segmentId
    clonecfg.transportZoneName = parentcfg.transportZoneName
    clonecfg.transportZoneUuid = parentcfg.transportZoneUuid
    clonecfg.type = parentcfg.type
    clonecfg.vendorSpecificConfig = parentcfg.vendorSpecificConfig
    clonecfg.vmVnicNetworkResourcePoolKey = parentcfg.vmVnicNetworkResourcePoolKey
    # send clone task to server
    tsk = pgobj.config.distributedVirtualSwitch.CreateDVPortgroup_Task(clonecfg)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# graceful shutdown
def graceful_shutdown(data: DataTree, log: Text, parent_win: Toplevel):
    # TODO write code to check for vCenter on one of the datacenter hosts
    root = parent_win
    textlog = log
    dataset = data
    frozenvms = list()
    onvms = list()
    # find frozen VMs
    for vm in dataset.vmobjlist.view:
        if is_frozen(vm=vm):
            frozenvms.append(vm)
    # find powered on VMs
    for vm in dataset.vmobjlist.view:
        if is_powered_on(vm=vm):
            onvms.append(vm)

    # power off frozen VMs
    for vm in frozenvms:
        poweroff_vm(vmobj=vm)
    # shutdown powered on VMs
    for vm in onvms:
        # check to see if vms are already powered off just in case some frozen ones got added
        if is_powered_off(vm):
            continue
        poweroff_vm(vmobj=vm)
    # get all hosts
    # put all hosts in maintenance mode
    # shutdown hosts
    # show logon window for ESXi that holds vCenter
    # shut down vCenter
    # put last ESXi in maintenance mode
    # shut down last ESXi

    return


# shutdown VM guest
def shutdown_vm(vmobj: vim.VirtualMachine) -> bool:
    if not vmobj.ShutdownGuest():
        return False
    return True


# power off VM
def poweroff_vm(vmobj: vim.VirtualMachine) -> bool:
    if not vmobj.PowerOffVM_Task():
        return False
    return True


# put host in Maintenance Mode
def host_maint_mode_on(hostobj: vim.HostSystem) -> bool:
    if not hostobj.EnterMaintenanceMode_Task(timeout=0):
        return False
    return True


# shut down Host
def host_shut_down(hostobj: vim.HostSystem) -> bool:
    if not hostobj.ShutdownHost_Task(force=True):
        return False
    return True


# is a clone
def is_clone(vm: vim.VirtualMachine) -> bool:
    disklist = vm.layout.disk[0].diskFile
    newlist = []
    for disk in disklist:
        newlist.append(disk[disk.find(" ") + 1:disk.rfind("/")])
    numdiskbacking = len(set(newlist))
    if numdiskbacking > 1:
        return True
    else:
        return False


def is_powered_on(vm: vim.VirtualMachine) -> bool:
    if str(vm.runtime.powerState) == "poweredOn":
        return True
    else:
        return False


def is_frozen(vm: vim.VirtualMachine) -> bool:
    if vm.runtime.instantCloneFrozen:
        return True
    else:
        return False


def is_powered_off(vm: vim.VirtualMachine) -> bool:
    if str(vm.runtime.powerState) == "poweredOff":
        return True
    else:
        return False


def append_log(log: Text, message: str, parent_win: Toplevel) -> None:
    log.insert(END, message + '\n')
    log.see(END)
    parent_win.update_idletasks()
    return
# TODO write 'is' functions for hosts (maintenance mode, power on, power off)
