import logging
import os

import attr
import pytz
from ruamel.yaml import YAML

from xxtoolkit.common.error import XXToolkitException

logger = logging.getLogger(__name__)


class ConfigurationException(XXToolkitException):
    xx_code = 1001
    pass


@attr.s(repr=False, kw_only=True)
class ABCCfg:

    def to_dict(self):
        return {i.name: self.get(i.name).to_dict() if isinstance(self.get(i.name), ABCCfg) else self.get(i.name)
                for i in self.__attrs_attrs__}

    def keys(self):
        return [i.name for i in self.__attrs_attrs__]

    def get(self, item, default=None):
        return getattr(self, item, default)

    def __getitem__(self, item):
        return getattr(self, item)


@attr.s(repr=False, kw_only=True)
class System(ABCCfg):
    # log = attr.ib(converter=lambda x: Log(**x), default={})
    timezone = attr.ib(default='UTC', type=pytz.timezone, converter=pytz.timezone)


@attr.s(repr=False, kw_only=True)
class TaskSetting(ABCCfg):
    timeout = attr.ib(type=int, default=10, converter=lambda x: int(x))


@attr.s(repr=False, kw_only=True)
class Log(ABCCfg):
    level = attr.ib(type=str, default='INFO', converter=lambda x: x.upper())

    @property
    def debug(self):
        return self.level == 'DEBUG'

    config = attr.ib(type=dict, default={
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(name)s %(levelname)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": 'INFO'},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    })


@attr.s(repr=False, kw_only=True)
class Database(ABCCfg):
    database = attr.ib(type=str, default='xxtoolkit')
    user = attr.ib(type=str, default='postgres')
    password = attr.ib(type=str, default='postgres')
    host = attr.ib(type=str, default='127.0.0.1')
    port = attr.ib(type=int, default=5432, converter=lambda x: int(x))
    min_size = attr.ib(type=int, default=3, converter=lambda x: int(x))
    max_size = attr.ib(type=int, default=100, converter=lambda x: int(x))


@attr.s(repr=False, kw_only=True)
class ServerTask(ABCCfg):
    setting = attr.ib(type=TaskSetting, converter=lambda x: TaskSetting(**(x or {})), default=None)
    fetch_interval = attr.ib(type=int, default=3)
    max_task_pre_runner = attr.ib(type=int, default=20)


@attr.s(repr=False, kw_only=True)
class ServerApi(ABCCfg):
    prefix = attr.ib(type=str, default='/api')
    host = attr.ib(type=str, default='0.0.0.0')
    port = attr.ib(type=int, default=8000)


@attr.s(repr=False, kw_only=True)
class Server(ABCCfg):
    database = attr.ib(type=Database, converter=lambda x: Database(**(x or {})), default=None)
    task = attr.ib(type=ServerTask, converter=lambda x: ServerTask(**(x or {})), default=None)
    api = attr.ib(type=ServerApi, converter=lambda x: ServerApi(**(x or {})), default=None)


@attr.s(repr=False, kw_only=True)
class Configuration(ABCCfg):
    log = attr.ib(type=Log, converter=lambda x: Log(**(x or {})), default=None)
    system = attr.ib(type=System, converter=lambda x: System(**(x or {})), default=None)
    server = attr.ib(type=Server, converter=lambda x: Server(**(x or {})), default=None)


def load_from_file(filepath, cls=Configuration) -> Configuration:
    _yaml = YAML()
    if not os.path.isfile(filepath):
        raise ConfigurationException(f'{filepath} not found.')
    with open(filepath) as f:
        cfg = cls(**(_yaml.load(f) or {}))
        return cfg


# cfg = load_from_file('./config.yaml')  # type: Configuration
cfg = None  # type: Configuration
