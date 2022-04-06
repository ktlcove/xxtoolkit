import abc
import inspect
import json
import logging
import typing

from xxtoolkit.common.type_manager import ABCTypeManager

logger = logging.getLogger(__name__)


class ObjectManager(ABCTypeManager):

    def __init__(self):
        self.types = []  # type: typing.List[XXToolkitObject]
        self.named_types = {}

    def add_type(self, c: 'XXToolkitObject'):

        if 'xx_type' not in c.__dict__:
            c.xx_type = c.__name__

        if c.xx_type in self.named_types:
            raise RuntimeError(f'type {c.xx_type} already defined in {self.named_types[c.xx_type]}.')
        else:
            self.named_types[c.xx_type] = c

        self.types.append(c)
        self.types.sort(key=lambda k: k.xx_type)

        print(f'add type {c.__name__} {c.xx_type}')
        logger.info(f'type {c.__name__} found.')

    def edit_type(self, c: 'XXToolkitObject'):
        base = inspect.getmro(c)[1] # type: ABCXXToolkit
        print('error manager edit', c, base, c.__name__)
        if 'xx_type' not in c.__dict__:
            c.xx_type = c.__name__
        if base.xx_type:
            c.xx_type = f'''{base.xx_type}.{c.xx_type}'''


object_manager = ObjectManager()


class ABCXXToolkit(metaclass=abc.ABCMeta):
    xx_code = 0
    xx_type = ''
    xx_base_class = None
    xx_class_managers = []

    def __init_subclass__(cls, **kwargs):
        print(f'init sub {cls}')
        for manager in cls.xx_class_managers:
            manager.edit_type(cls)
            manager.add_type(cls)

    @abc.abstractmethod
    def xx_dict(self) -> dict:
        pass

    def xx_json(self) -> str:
        return json.dumps(
            self.xx_dict(),
            indent=4,
            ensure_ascii=False,
            allow_nan=False,
        )


class XXToolkitObject(ABCXXToolkit, metaclass=abc.ABCMeta):
    xx_code = 0
    xx_type = ''
    xx_base_class = None
    xx_class_managers = [object_manager, ]

    @property
    @abc.abstractmethod
    def data(self) -> dict:
        pass

    def xx_dict(self) -> dict:
        return {
            'code': self.xx_code,
            'type': self.xx_type,
            'data': self.data,
        }
