import abc
import asyncio
import json
import logging
import traceback

import async_timeout

from xxtoolkit.common.task import ABCTask, TaskManager, TaskState
from xxtoolkit.configuration import cfg
from xxtoolkit.server.common import db_conn

logger = logging.getLogger(__name__)


server_task_manager = TaskManager()


class ABCServerTask(ABCTask):
    xx_type = 'serverTask'
    xx_class_managers = [*ABCTask.xx_class_managers, server_task_manager]
    db = db_conn.db

    xx_task_default_settings = {}

    async def get_setting(self, k):
        for v in [self.data['settings'].get(k),
                  self.xx_task_default_settings.get(k),
                  cfg.server.task.setting.get(k)]:
            if v is not None:
                return v

    async def set_task_state(self, state):
        await self.db.execute(f'''update "task" set state=$1, stime=now() where id=$2''',
                              state, self.id)
        logger.info(f'task: task start: {self.id}')

    async def execute(self):
        try:
            await self.load()
            await self.on_running()
            async with async_timeout.timeout(int(self.get_setting('timeout'))) as timeout_manager:
                try:
                    logger.info(f'task: task pre exec: {self.id}')
                    await self.func()
                except asyncio.CancelledError:
                    # timeout
                    await self.set_task_state(TaskState.timeout)
                except Exception as error:
                    # failure
                    await self.on_failure(error)
                if timeout_manager.expired:
                    # timeout 2
                    await self.set_task_state(TaskState.timeout)

            await self.done()

        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)

    @abc.abstractmethod
    async def func(self):
        pass

    async def load(self):
        info = dict(await self.db.fetchrow(
            f'''select * from "task" where id = $1''', self.id))
        self._data = info

    async def on_running(self):
        await self.set_task_state(TaskState.running)

    async def on_succeed(self, result):
        logger.info(f'task succeed result {result}')
        await self.db.execute(f'''update "task" set state=$1, result=$2, etime=now()
                                               where id=$3
                                                ''',
                              TaskState.succeed,
                              json.dumps(result) if result else None,
                              self.id)
        logger.info(f'task: task succeed: {self.id}')

    async def on_succeed_without_result(self):
        await self.db.execute(f'''update "task" set state = $1, etime=now()
                                               where id = $2
                                                ''',
                              TaskState.succeed,
                              self.id)
        logger.info(f'task: task succeed: {self.id}')

    async def on_failure(self, error):
        # raise error
        error_msg = json.dumps({'t': str(type(error)), 'm': str(error)})
        await self.db.execute(f'''update "task" set state=$1, error=$2, etime=now() 
                                                  where id = $3
                                               ''', TaskState.failure, error_msg, self.id)
        logger.info(f'task: task failure: {self.id}')

    async def done(self):
        logger.info(f'task: task done: {self.id}')
