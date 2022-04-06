import abc
import typing

import logging

from xxtoolkit.common.object import XXToolkitObject
from xxtoolkit.common.type_manager import ABCTypeManager

logger = logging.getLogger(__name__)


class TaskState:
    # todo: move this to ops.const
    created = 'created'
    pending = 'pending'
    running = 'running'
    succeed = 'succeed'
    warning = 'warning'
    failure = 'failure'
    timeout = 'timeout'


class TaskManager(ABCTypeManager):

    def __init__(self):
        self.types = []  # type: typing.List[XXToolkitObject]
        self.named_types = {}

    def add_type(self, c: 'ABCTask'):
        if c.xx_task_type in self.named_types:
            raise RuntimeError(f'type {c.xx_task_type} already defined in {self.named_types[c.xx_task_type]}.')
        else:
            self.named_types[c.xx_task_type] = c

        self.types.append(c)
        self.types.sort(key=lambda k: k.xx_task_type)

        logger.info(f'task {c.__class__.__name__} found.')


class ABCTask(XXToolkitObject):
    xx_type = 'task'
    xx_task_type: str = 'abc'

    def __init__(self, id):
        self.id = id
        self._data = {}

    @property
    def state(self):
        return self.data['state']

    @property
    def data(self):
        return self._data

    @classmethod
    async def create(cls, detail: dict, settings: dict, priority=0):
        raise NotImplemented

    async def get_status(self):
        raise NotImplemented

    async def execute(self):
        raise NotImplemented

    async def terminate(self, timeout=None):
        raise NotImplemented
