
import datetime
from .FuncLib import *
class VmTaskWindow:
    def __init__(self, data:DataTree, vmobj:vim.VirtualMachine):
        self.vm = vmobj
        self.dataset = data
        self.task_manager = self.dataset.content.taskManager
        self.filter_spec = vim.TaskFilterSpec()
        self.by_entity = vim.TaskFilterSpec.ByEntity()
        self.by_entity.entity = self.vm
        self.by_entity.recursion = 'self'
        self.filter_spec.entity = self.by_entity
        self.task_collector = self.task_manager.CreateCollectorForTasks(filter=self.filter_spec)

        # create top level
        self.top = Toplevel(master=self.dataset.rootwin)
        # create inner class for tasks
        class TaskObj:
            def __init__(self):
                self.start_date = None
                self.state = None
                self.description_id = None
                self.start_time = None
                self.complete_time = None
                self.time_to_complete = None
        # init list of task objects
        task_objs = list()
        # package tasks in objects and append to list
        for task in self.task_collector.latestPage:
            tmp_obj = TaskObj()
            tmp_obj.start_date = str(task.startTime.date())
            tmp_obj.state = task.state
            tmp_obj.description_id = task.descriptionId
            tmp_obj.start_time = str(task.startTime.time())[:str(task.startTime.time()).rfind('.')]
            tmp_obj.complete_time = str(task.completeTime.time())[:str(task.completeTime.time()).rfind('.')]
            tmp_obj.time_to_complete = task.completeTime - task.startTime
            tmp_obj.time_to_complete = str(tmp_obj.time_to_complete)[:str(tmp_obj.time_to_complete).rfind('.')]
            task_objs.append(tmp_obj)

        # dynamically create and place widgets
        for i in range(len(task_objs)):
            # create widgets
            self.start_date = Entry(master=self.top, width=10)
            self.state = Entry(master=self.top, width=15)
            self.description_id = Entry(master=self.top, width=30)
            self.start_time = Entry(master=self.top, width=10)
            self.complete_time = Entry(master=self.top, width=10)
            self.time_to_complete = Entry(master=self.top, width=10)
            # place widgets
            self.start_date.grid(column=0, row=i)
            self.state.grid(column=1, row=i)
            self.description_id.grid(column=2, row=i)
            self.start_time.grid(column=3, row=i)
            self.complete_time.grid(column=4, row=i)
            self.time_to_complete.grid(column=5, row=i)
            # assign values
            self.start_date.insert(END, task_objs[i].start_date)
            self.state.insert(END, task_objs[i].state)
            self.description_id.insert(END, task_objs[i].description_id)
            self.start_time.insert(END, task_objs[i].start_time)
            self.complete_time.insert(END, task_objs[i].complete_time)
            self.time_to_complete.insert(END, task_objs[i].time_to_complete)