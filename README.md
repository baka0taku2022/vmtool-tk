# vmtool-tk


<img width="776" alt="image" src="https://user-images.githubusercontent.com/70031102/165833932-5a82d4c4-1ebf-46f6-8623-8bd4cafb1009.png">
<img width="296" alt="image" src="https://user-images.githubusercontent.com/70031102/165834192-f20e1d34-4cc5-4820-ab41-f539d3f79f48.png">
<img width="1209" alt="image" src="https://user-images.githubusercontent.com/70031102/165834307-c67097ac-508a-445a-95f6-90782567d152.png">
<img width="459" alt="image" src="https://user-images.githubusercontent.com/70031102/165834489-2c2d7c08-03d2-4164-8877-dc2fb1006bff.png">
<img width="462" alt="image" src="https://user-images.githubusercontent.com/70031102/165834617-2d1bfb02-b15f-4ee6-99bf-8f3507f6791b.png">
<img width="674" alt="image" src="https://user-images.githubusercontent.com/70031102/165834831-a78bc888-34eb-4f92-be79-7dea46684495.png">
<img width="715" alt="image" src="https://user-images.githubusercontent.com/70031102/165834940-7a5aeac1-c985-4c6e-8465-cffe0f48a4cf.png">



This is a set of tools that can be used against VCenter 6.7 to perfom a few actions that are available in the API, but not the GUI.
These include the following:

1. Creating linked clones.
2. Creating instant clones
3. Promoting disks on a clone
4. Cloning DVPortgroups.
5. Pasting text into a VM.
6. Various VM stats.

More features are planned.

Written in Python 3.8. Only requirements are those needed to install pyvmomi, the rest is Python native. This code is still considered BETA. Use at your own risk.

Note for Mac users. The version of Tk that ships with Monterey is broken (may also be broken on other versions of macOS). Use hombrew python and pyhon-tk for best results. Python from https://python.org works as well
