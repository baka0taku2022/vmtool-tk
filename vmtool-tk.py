"""
-=vmtool-tk=-
The purpose of this program is to use a GUI to accomplish common tasks in vCenter using the pyvmomi API. Some of these
tasks are:
1. create one or more linked clones.
2. create one or more instant clones.
3. upgrade a linked clones to a full clones.
4. clone a DVPortgroup
5. Perform a graceful shutdown of all servers and vms

More will likely get added when i have the time/inclination.

This builds upon the foundations of the vmtool program i wrote for personal use. That software, however, had its
limitations. These included but were not limited to:

1. Only one machine at a time could be cloned.
2. The connection had to be re-established if you wanted to do more than one task.

-=baka0taku=-



"""
# local includes
from vmtoolTkLib import DataTree
from vmtoolTkLib import RootWindow
if __name__ == '__main__':
    RootWindow(data=DataTree().get_instance()).start()
