import abc

import argparse
import asyncio

from xxtoolkit.configuration import load_from_file


class CmdEntrypoint(metaclass=abc.ABCMeta):

    def __init__(self):
        self.parser = argparse.ArgumentParser()

    def parse_configuration(self):
        self.parser.add_argument('-c', '--config', dest='config', required=False, default='~/.xxtoolkit.yaml')

    def add_parsers(self):
        self.parse_configuration()

    @abc.abstractmethod
    async def main(self, args):
        pass

    def entrypoint(self, args=None):
        self.add_parsers()
        my_args = self.parser.parse_args(args)
        load_from_file(my_args.config)

        asyncio.run(self.main(my_args))
