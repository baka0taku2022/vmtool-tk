# vmtool-tk
This is a set of tools that can be used against VCenter 6.7 to perfom a few actions that are available in the API, but not the GUI.
These include the following:

1. Creating linked clones.
2. Creating instant clones
3. Promoting disks on a clone
4. Cloning DVPortgroups.

More features are planned.

Written in Python 3.8. Only requirements are those needed to install pyvmomi, the rest is Python native. This code is still considered BETA. Use at your own risk.

Note for Mac users. The version of Tk that ships with Monterey is broken (may also be broken on other versions of macOS). Use hombrew python and pyhon-tk for best results. Python from https://python.org works as well
