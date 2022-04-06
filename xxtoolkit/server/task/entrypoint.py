import asyncio
import signal
import socket

from xxtoolkit.common.entrypoint import CmdEntrypoint
from xxtoolkit.common.task import TaskState
from xxtoolkit.configuration import cfg
from xxtoolkit.server.common import db_conn

import logging

from xxtoolkit.server.task import ABCServerTask, server_task_manager

logger = logging.getLogger(__name__)


class ServerTaskEntrypoint(CmdEntrypoint):
    db = db_conn.db

    def __init__(self):
        self.keep_running = False
        self.running_tasks = {}

        self.name = socket.gethostbyname(socket.gethostname())

    async def task_generator(self):
        while self.keep_running:
            try:
                result = await self.db.fetchrow(
                    '''
                    update "task" set state = $1, runner = $2
                    from (select id from "task"
                                     where "task".state = $3 and "task".runner is null
                                     order by priority desc nulls last, ctime
                                     limit 1
                                     for update skip locked) as upd_task
                    returning *
                    ''', TaskState.pending, self.name, TaskState.created)
            except Exception as e:
                logger.error(f'try fetch task from postgres but sql return an error {type(e)} {str(e)}')
                continue
            if result:
                try:
                    task_data = dict(result)
                except Exception as e:
                    logger.error(f'try fetch task raise {type(e)} {str(e)} for result {result}')
                    continue
                logger.debug(f'got new task: {task_data}')
                task_type = task_data['type']
                task_id = task_data['id']
                try:
                    task_class = server_task_manager.named_types[task_type]
                    yield task_class(task_id)
                except KeyError:
                    logger.fatal(f'run task failure for {task_type}({task_id}).')
            else:
                await asyncio.sleep(cfg.server.task.fetch_interval)

    async def run_task(self, task: ABCServerTask):
        logger.info(f'run task -> {task}')
        await task.execute()
        self.running_tasks.pop(task.id)
        logger.info(f'task done -> {task}')

    async def main(self, args):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        while self.keep_running:
            if len(self.running_tasks) < cfg.server.task.max_task_pre_runner:
                async for task in self.task_generator():
                    self.running_tasks[task.id] = asyncio.ensure_future(self.run_task(task))
            else:
                await asyncio.sleep(cfg.server.task.fetch_interval)

    async def run_once(self):
        async for task in self.task_generator():
            python_task = asyncio.ensure_future(self.run_task(task))
            self.running_tasks[task.id] = python_task
            await python_task
            break

    def stop(self, *_):
        self.keep_running = False


server_task_entrypoint = ServerTaskEntrypoint()
