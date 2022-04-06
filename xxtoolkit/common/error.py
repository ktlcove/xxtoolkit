import inspect
import logging

from xxtoolkit.common.object import ABCXXToolkit
from xxtoolkit.common.type_manager import ABCTypeManager

logger = logging.getLogger(__name__)


class ExceptionManager(ABCTypeManager):

    def __init__(self):
        self.types = []  # type: [XXToolkitException]
        self.named_types = {}
        self.coded_types = {}

    def add_type(self, c: 'XXToolkitException'):

        if 'xx_code' not in c.__dict__:
            raise RuntimeError(f'xx_code not defined in cls {c}')

        if c.xx_type in self.named_types:
            raise RuntimeError(f'type {c.xx_type} already defined in {self.named_types[c.xx_type]}.')
        elif c.xx_code in self.coded_types:
            raise RuntimeError(f'code {c.xx_code} already defined in {self.coded_types[c.xx_code]}.')
        else:
            self.named_types[c.xx_type] = c
            self.coded_types[c.xx_code] = c

        self.types.append(c)
        self.types.sort(key=lambda k: k.xx_code)

        print(f'exception manager add type {c.__name__} {c.xx_type}')
        logger.info(f'type {c.__name__} found.')

    def edit_type(self, c: 'XXToolkitException'):
        base = inspect.getmro(c)[1]
        print('error manager edit', c, base, c.__name__)
        if 'xx_type' not in c.__dict__:
            c.xx_type = c.__name__
        if base.xx_type:
            c.xx_type = f'''{base.xx_type}.{c.xx_type}'''


exception_manager = ExceptionManager()


class XXToolkitException(ABCXXToolkit, Exception):
    xx_code = 1
    xx_type = 'Exception'
    xx_class_managers = [exception_manager, ]
    xx_err_format = ''

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.msg = self.xx_err_format.format_map({'self': self})
        Exception(self, self.msg)

    @property
    def data(self):
        return {}

    def xx_dict(self) -> dict:
        return {
            'code': self.xx_code,
            'type': self.xx_type,
            'err': {
                'args': self.args,
                'kwargs': self.kwargs,
                'msg': self.msg,
            }
        }
