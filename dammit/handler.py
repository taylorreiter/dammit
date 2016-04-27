#!/usr/bin/env python

from doit.cmd_base import TaskLoader
from doit.doit_cmd import DoitMain
from doit.dependency import Dependency, SqliteDB

from .util import Move
from .tasks import print_tasks

class TaskHandler(TaskLoader):

    def __init__(self, doit_db, logger, config=None, files=None, **doit_config_kwds):

        super(TaskHandler, self).__init__()

        if files is None:
            self.files = {}
        if type(files) is not dict:
            raise TypeError('files must be of type dict')
        else:
            self.files = files

        self.tasks = {}
        self.doit_config = dict(dep_file=doit_db, **doit_config_kwds)
        self.doit_dir = os.path.dirname(doit_db)
        self.doit_dep_mgr = Dependency(SqliteDB, doit_db)
        self.logger = logger

    def register_task(name, task, files=None):
        if files is None:
            self.files = {}
        if type(files) is not dict:
            raise TypeError('files must be of type dict')
        
        self.tasks[name] = task
        self.files.update(files)

    def get_status(self, task):
        if type(task) is str:
            try:
                task = self.tasks[task]
            except KeyError:
                self.logger.error('Task not found:{0}'.format(task))
                raise
        return self.doit_dep_mgr.get_status(task, self.tasks.values())

    def check_uptodate(self):
        outofdate_tasks = {}
        outofdate = False
        for task_name, task in self.tasks.items():
            if self.get_status(task) != 'up-to-date'):
                outofdate_tasks[task_name] = task
                outofdate = True
        return not outofdate, outofdate_tasks
    
    def load_tasks(self, cmd, opt_values, pos_args):
        print_tasks(self.tasks.values(), logger=self.logger)
        return self.tasks.values()

    def run(self, doit_args=None, move=False):
        if doit_args is None:
            doit_args = ['run']
        runner = DoitMain(self())
        if move:
            with Move(self.doit_dir):
                return runner.run(doit_args)
        else:
            return runner.run(doit_args)
