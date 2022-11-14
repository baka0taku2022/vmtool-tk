"""
The purpose of this file is to house all the general functions for the program so that things only have to be
written once.

-=baka0taku=-
"""
import random
import ssl
import re
import requests
from socket import gaierror
from time import sleep
from tkinter import *
from tkinter.messagebox import *
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from .DataTree import DataTree
from .StatWindow import StatWindow


# establish connection to vCenter
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
        showerror(title='Error', message=str(e))
        dataset.connection = None
        return False


# cleanup and disconnect from vCenter
def cleanup(dataset: DataTree, rootwin: Tk) -> None:
    # disconnect from server
    if dataset.connection:
        Disconnect(dataset.connection)
    # quit program
    rootwin.quit()
    return


# move to another listbox
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
    # send clone task(s) to vCenter
    if typeclone == "linked":
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
        for vm in vmobjs:
            if not is_frozen(vm=vm):
                notfrozen.append(vm.name)
        if len(notfrozen) > 0:
            cont: bool = askyesno(title="Continue?",
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
        if not is_powered_off(vm):
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
    randnumext: str = str(random.randint(100000, 999999))
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


# reset VM
def reset_vm(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.ResetVM_Task()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# reboot VM
def reboot_vm_guest(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.RebootGuest()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# shutdown VM guest
def shutdown_vm(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.ShutdownGuest()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# power off VM
def poweroff_vm(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.PowerOffVM_Task()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# power on VM
def power_on_vm(vmobj: vim.VirtualMachine) -> bool:
    tsk = vmobj.PowerOnVM_Task()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# put host in Maintenance Mode
def host_maint_mode_on(hostobj: vim.HostSystem) -> bool:
    tsk = hostobj.EnterMaintenanceMode_Task(timeout=0)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# shut down Host
def host_shut_down(hostobj: vim.HostSystem) -> bool:
    tsk = hostobj.ShutdownHost_Task(force=True)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# Is VM powered ON?
def is_powered_on(vm: vim.VirtualMachine) -> bool:
    try:
        if str(vm.runtime.powerState) == "poweredOn":
            return True
    except AttributeError:
        return False


# Is VM frozen?
def is_frozen(vm: vim.VirtualMachine) -> bool:
    try:
        if vm.runtime.instantCloneFrozen:
            return True
    except AttributeError:
        return False


# Is VM powered OFF
def is_powered_off(vm: vim.VirtualMachine) -> bool:
    if str(vm.runtime.powerState) == "poweredOff":
        return True
    else:
        return False


# Is host powered ON
def is_host_powered_on(hostobj: vim.HostSystem) -> bool:
    if hostobj is None:
        return False
    if str(hostobj.runtime.powerState) == "poweredOn":
        return True
    else:
        return False


# Is host powered OFF
def is_host_powered_off(hostobj: vim.HostSystem) -> bool:
    if hostobj is None:
        return False
    if str(hostobj.runtime.powerState) == "poweredOff":
        return True
    else:
        return False


# Is host in maintenance mode?
def is_host_in_maint_mode(hostobj: vim.HostSystem) -> bool:
    if hostobj is None:
        return False
    if hostobj.runtime.inMaintenanceMode:
        return True
    else:
        return False


# Get USB Hid code
def code_lookup(to_encode: str) -> int:
    keycodes = {
        "a": 0x4,
        "b": 0x5,
        "c": 0x6,
        "d": 0x7,
        "e": 0x8,
        "f": 0x9,
        "g": 0xa,
        "h": 0xb,
        "i": 0xc,
        "j": 0xd,
        "k": 0xe,
        "l": 0xf,
        "m": 0x10,
        "n": 0x11,
        "o": 0x12,
        "p": 0x13,
        "q": 0x14,
        "r": 0x15,
        "s": 0x16,
        "t": 0x17,
        "u": 0x18,
        "v": 0x19,
        "w": 0x1a,
        "x": 0x1b,
        "y": 0x1c,
        "z": 0x1d,
        "1": 0x1e,
        "2": 0x1f,
        "3": 0x20,
        "4": 0x21,
        "5": 0x22,
        "6": 0x23,
        "7": 0x24,
        "8": 0x25,
        "9": 0x26,
        "0": 0x27,
        "\n": 0x28,
        "esc": 0x29,
        "backspace": 0x2a,
        "\t": 0x2b,
        " ": 0x2c,
        "-": 0x2d,
        "=": 0x2e,
        "[": 0x2f,
        "]": 0x30,
        "\\": 0x31,
        ";": 0x33,
        "'": 0x34,
        "`": 0x35,
        ",": 0x36,
        ".": 0x37,
        "/": 0x38,
        "caps": 0x39,
        "F1": 0x3a,
        "F2": 0x3b,
        "F3": 0x3c,
        "F4": 0x3d,
        "F5": 0x3e,
        "F6": 0x3f,
        "F7": 0x40,
        "F8": 0x41,
        "F9": 0x42,
        "F10": 0x43,
        "F11": 0x44,
        "F12": 0x45,
        "prtscr": 0x46,
        "scl": 0x47,
        "pause": 0x48,
        "insert": 0x49,
        "home": 0x4a,
        "pgup": 0x4b,
        "del": 0x4c,
        "end": 0x4d,
        "pgdn": 0x4e,
        "right": 0x4f,
        "left": 0x50,
        "down": 0x51,
        "up": 0x52,
        "A": 0x4,
        "B": 0x5,
        "C": 0x6,
        "D": 0x7,
        "E": 0x8,
        "F": 0x9,
        "G": 0xa,
        "H": 0xb,
        "I": 0xc,
        "J": 0xd,
        "K": 0xe,
        "L": 0xf,
        "M": 0x10,
        "N": 0x11,
        "O": 0x12,
        "P": 0x13,
        "Q": 0x14,
        "R": 0x15,
        "S": 0x16,
        "T": 0x17,
        "U": 0x18,
        "V": 0x19,
        "W": 0x1a,
        "X": 0x1b,
        "Y": 0x1c,
        "Z": 0x1d,
        "!": 0x1e,
        "@": 0x1e,
        "#": 0x20,
        "$": 0x21,
        "%": 0x22,
        "^": 0x23,
        "&": 0x24,
        "*": 0x25,
        "(": 0x26,
        ")": 0x27,
        "_": 0x28,
        "+": 0x2e,
        "{": 0x2f,
        "}": 0x30,
        "|": 0x31,
        ":": 0x33,
        '"': 0x34,
        "~": 0x35,
        "<": 0x36,
        ">": 0x37,
        "?": 0x38
    }
    hidcode = int(keycodes.get(to_encode))
    hidcode = hidcode << 16
    hidcode = hidcode | 7
    return hidcode


def key_combo(normal_key: str, left_alt: bool, left_shift: bool, left_ctrl: bool, left_gui: bool,
              special_key: str) -> vim.UsbScanCodeSpec:
    # build spec object
    spec = vim.UsbScanCodeSpec()
    key_event = vim.UsbScanCodeSpec.KeyEvent()
    key_events = list()
    modifier_type = vim.UsbScanCodeSpec.ModifierType()
    key_event.modifiers = modifier_type
    key_events.append(key_event)
    spec.keyEvents = key_events

    # check parameters
    if normal_key:
        spec.keyEvents[0].usbHidCode = int(code_lookup(to_encode=normal_key))
    elif special_key:
        spec.keyEvents[0].usbHidCode = int(code_lookup(to_encode=special_key))

    # check bools
    if left_alt:
        spec.keyEvents[0].modifiers.leftAlt = True
    else:
        spec.keyEvents[0].modifiers.leftAlt = False
    if left_shift:
        spec.keyEvents[0].modifiers.leftShift = True
    else:
        spec.keyEvents[0].modifiers.leftShift = False
    if left_ctrl:
        spec.keyEvents[0].modifiers.leftControl = True
    else:
        spec.keyEvents[0].modifiers.leftControl = False
    if left_gui:
        spec.keyEvents[0].modifiers.leftGui = True
    else:
        spec.keyEvents[0].modifiers.leftGui = False
    return spec


# convert string to usb scancode
def str_to_usb(input_string: str) -> vim.UsbScanCodeSpec:
    # clear out newlines
    # input_string = input_string.replace("\n", '')
    spec: vim.UsbScanCodeSpec = vim.UsbScanCodeSpec()
    key_events = list()
    for key in input_string:
        regex = r"[A-Z\~\!\@\#\$\%\^\&\*\(\)\_\+\{\}\|\:\"\<\>\?]"
        if re.match(regex, key):
            evt = vim.UsbScanCodeSpec.KeyEvent()
            modifier_type: vim.UsbScanCodeSpec.ModifierType = vim.UsbScanCodeSpec.ModifierType()
            evt.modifiers = modifier_type
            evt.modifiers.leftShift = True
            evt.usbHidCode = code_lookup(to_encode=key)
            key_events.append(evt)
        else:
            evt = vim.UsbScanCodeSpec.KeyEvent()
            evt.usbHidCode = code_lookup(to_encode=key)
            key_events.append(evt)
    spec.keyEvents = key_events
    return spec


# make multiple linked clones
def multi_linked_clones(vm_names: list, num_of_clones: int, data: DataTree) -> None:
    for x in range(num_of_clones):
        send_clone_task(names=vm_names, data=data, typeclone="linked")
    return


# make multiple instant clones
def multi_instant_clones(vm_names: list, num_of_clones: int, data: DataTree) -> None:
    for x in range(num_of_clones):
        send_clone_task(names=vm_names, data=data, typeclone="instant")
    return


# get VM CPU usage
def get_cpu_usage(vm: vim.VirtualMachine) -> str:
    try:
        return str(vm.summary.quickStats.overallCpuUsage) + " Mhz"
    except AttributeError:
        return '0 Mhz'


# get VM Memory Usage
def get_memory_usage(vm: vim.VirtualMachine) -> str:
    try:
        return str(vm.summary.quickStats.guestMemoryUsage) + " MB"
    except AttributeError:
        return '0 MB'


# get VM disk usage
def get_disk_usage(vm: vim.VirtualMachine) -> str:
    try:
        size_in_bytes: int = vm.summary.storage.committed
        size_in_gb: int = int(size_in_bytes / 1073741824)
        return str(size_in_gb) + " GB"
    except AttributeError:
        return '0 GB'


# get number of disks
def get_num_disks(vm: vim.VirtualMachine) -> str:
    try:
        return str(len(vm.layout.disk))
    except AttributeError:
        return "0"


# get num of snapshots
def get_num_snapshots(vm: vim.VirtualMachine) -> str:
    try:
        return str(len(vm.layout.snapshot))
    except AttributeError:
        return "0"


# get number of disk files
def get_num_disk_files(vm: vim.VirtualMachine) -> str:
    try:
        return str(len(vm.layout.disk[0].diskFile))
    except IndexError:
        return "0"
    except AttributeError:
        return "0"


# create a VM snapshot
def create_snapshot(snapshot_name: str, vm: vim.VirtualMachine, snapshot_desc: str, snapshot_memory: bool,
                    snapshot_quiesce: bool):
    task = vm.CreateSnapshot_Task(name=snapshot_name,
                                  description=snapshot_desc,
                                  memory=snapshot_memory,
                                  quiesce=snapshot_quiesce)
    if task.info.error is not None:
        showerror(title="Error", message=task.info.error.msg)
        return False
    else:
        return True


# boot VM into BIOS
def bios_boot(vm: vim.VirtualMachine) -> None:
    spec = vim.vm.ConfigSpec()
    boot_spec = vim.vm.BootOptions()
    boot_spec.enterBIOSSetup = True
    spec.bootOptions = boot_spec
    vm.ReconfigVM_Task(spec=spec)
    sleep(1)
    tsk = vm.ResetVM_Task()
    if tsk.info.error is not None:
        vm.PowerOnVM_Task()
    return


# get host cpu usage
def get_host_cpu_usage(hostobj: vim.HostSystem) -> int:
    if hostobj is None:
        return 0
    hardware = hostobj.summary.hardware
    total_mhz = hardware.cpuMhz * hardware.numCpuCores
    used_mhz = hostobj.summary.quickStats.overallCpuUsage
    percentage_used = int((used_mhz / total_mhz) * 100)
    return percentage_used


# get host memory usage
def get_host_memory_usage(hostobj: vim.HostSystem) -> int:
    if hostobj is None:
        return 0
    total_memory = hostobj.summary.hardware.memorySize / 1024 / 1024
    used_memory = hostobj.summary.quickStats.overallMemoryUsage
    percentage_used = int((used_memory / total_memory) * 100)
    return percentage_used


# get host storage usage
def get_host_storage_usage(hostobj: vim.HostSystem) -> int:
    if hostobj is None:
        return 0
    total_storage = 0
    free_storage = 0
    for ds in hostobj.datastore:
        total_storage += ds.summary.capacity
        free_storage += ds.summary.freeSpace
    percentage_used = int((free_storage / total_storage) * 100)
    return percentage_used


# get swapped RAM from VM
def get_swapped_ram(vmobj: vim.VirtualMachine) -> str:
    if vmobj is not None:
        return str(vmobj.summary.quickStats.swappedMemory) + 'MB'
    else:
        return "0MB"


# set VM screen resolution
def set_screen_resolution(vmobj: vim.VirtualMachine, width: int, height: int) -> None:
    vmobj.SetScreenResolution(width=width, height=height)
    return


# rename managed entity
def rename_obj(obj: vim.ManagedEntity, new_name: str, data: DataTree) -> None:
    tsk = obj.Rename_Task(newName=new_name)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return
    data.clear_data()
    StatWindow(data=data).parse_data()
    return


# Get VM total memory
def get_total_mem(vmobj: vim.VirtualMachine) -> str:
    if vmobj is not None:
        return str(vmobj.config.hardware.memoryMB) + " MB"
    else:
        return "0"


# get host name
def get_host_name(vmobj: vim.VirtualMachine) -> str:
    if vmobj is not None:
        return vmobj.runtime.host.name
    else:
        return ""


# get number of CPU from VM
def get_num_processors(vmobj: vim.VirtualMachine) -> str:
    if vmobj is not None:
        return str(vmobj.config.hardware.numCPU)
    else:
        return "0"


# vanilla clone of VM
def clone_vm(vmobj: vim.VirtualMachine, vm_name: str) -> None:
    clonefolder = vmobj.parent
    clonename = vm_name
    clonespec = vim.VirtualMachineCloneSpec()
    clonespec.location = vim.VirtualMachineRelocateSpec()
    tsk = vmobj.CloneVM_Task(clonefolder, clonename, clonespec)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return
    return


# migrate VM
def migrate_vm(vmobj: vim.VirtualMachine, hostobj: vim.HostSystem, dsobj: vim.Datastore) -> bool:
    spec = vim.VirtualMachineRelocateSpec()
    spec.host = hostobj
    spec.datastore = dsobj
    tsk = vmobj.RelocateVM_Task(spec)
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return False
    return True


# delete VM
def delete_vm(vmobj: vim.VirtualMachine) -> None:
    tsk = vmobj.Destroy_Task()
    sleep(.5)
    if tsk.info.error is not None:
        showerror(title="Error", message=tsk.info.error.msg)
        return
    return


# freeze VM
def freeze_vm(user: str,
              password: str,
              script_type: str,
              file_name: str,
              file_content: str,
              data: DataTree,
              vm: vim.VirtualMachine) -> int:
    # create credential object for authentication
    creds: vim.vm.guest.NamePasswordAuthentication = vim.vm.guest.NamePasswordAuthentication(
        username=user, password=password)
    # create File Attributes object
    file_attr_obj: vim.vm.guest.FileManager.FileAttributes = vim.vm.guest.FileManager.FileAttributes()
    # get file manager object
    file_manager: vim.vm.guest.FileManager = data.content.guestOperationsManager.fileManager
    # create temp directory on VM
    try:
        remote_dir = file_manager.CreateTemporaryDirectoryInGuest(vm=vm, auth=creds, prefix='', suffix='')
    except vim.fault.InvalidGuestLogin:
        showerror(title="Error", message="Invalid Login")
        return 0
    except vim.fault.GuestOperationsUnavailable:
        showerror(title="Error", message="Guest services not started.")
        return 0
    # make file path in guest
    vm_guest_id = vm.config.guestId
    vm_regex = r"win"
    if re.match(vm_regex, vm_guest_id):
        remote_path = remote_dir + '\\' + file_name
    else:
        remote_path = remote_dir + '/' + file_name
    # get file size
    file_size = len(file_content)
    # initiate file transfer
    put_url = file_manager.InitiateFileTransferToGuest(vm=vm, auth=creds, guestFilePath=remote_path,
                                                       fileAttributes=file_attr_obj, fileSize=file_size,
                                                       overwrite=True)
    # push file to vm
    response = requests.put(url=put_url, data=file_content, verify=False)
    if not response.status_code == 200:
        showerror(title="Error", message="File Transfer Failed.")

    # get process manager singleton
    process_manager = data.content.guestOperationsManager.processManager

    # set permissions for linux/bsd
    if not re.match(vm_regex, vm_guest_id):
        chmod_prog = "/bin/chmod"
        chmod_opts = "777 " + remote_path
        chmod_spec = vim.vm.guest.ProcessManager.ProgramSpec(programPath=chmod_prog, arguments=chmod_opts)
        process_manager.StartProgramInGuest(vm=vm, auth=creds, spec=chmod_spec)

    # define spec for program
    if script_type == "Windows Fast Script":
        program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
            programPath=r"c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe", arguments=remote_path)
    else:
        program_spec = vim.vm.guest.ProcessManager.ProgramSpec(programPath=remote_path)

    # execute freeze script
    try:
        ret = process_manager.StartProgramInGuest(vm=vm, auth=creds, spec=program_spec)
        return ret
    except vmodl.fault.SystemError:
        showerror(title="Error", message="Unknown system error in guest.")
        return 0
    except vim.fault.GuestPermissionDenied:
        showerror(title='Error',
                  message='The guest authentication used does not have permissions to perform the operation.')
        return 0
