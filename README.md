# vmtool-tk

This is a set of tools that can be used against VCenter 6.7/7.0 to perfom many actions. Including some only found in the API.
These include the following:

1. Creating linked clones.
2. Creating instant clones
3. Promoting disks on a clone
4. Cloning DVPortgroups.
5. Pasting text into a VM.
6. Various VM stats.
7. Freezing a clone.
8. Regular clone operation.
9. View latest tasks.
10. Host Stats.
11. VM migration.
12. Deleting a VM

More features are planned.

Written in Python 3.10. Only requirements are those needed to install pyvmomi and requests, the rest is Python native. This code is still considered BETA. Use at your own risk.

Note for Mac users. The version of Tk that ships with Monterey is broken (may also be broken on other versions of macOS). Use hombrew python and pyhon-tk for best results. Python from https://python.org works as well
