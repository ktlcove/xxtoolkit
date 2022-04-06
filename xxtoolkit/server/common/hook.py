import typing
from collections import namedtuple

Hook = namedtuple('Hook', ('func', 'args', 'kwargs', 'priority'))


class HookManager:

    def __init__(self):
        self.hooks = []  # type: typing.List[Hook]

    def add(self, func, args=None, kwargs=None, priority=100):
        self.hooks.append(Hook(func, args, kwargs, priority))
        self.hooks.sort(key=lambda x: x.priority)

    async def run_hooks(self):
        for hook in self.hooks:
            await hook.func(*hook.args, **hook.kwargs)


hook_manager = HookManager()
