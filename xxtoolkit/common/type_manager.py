import abc
import logging

logger = logging.getLogger(__name__)


class ABCTypeManager(abc.ABC):

    def add_type(self, c):
        pass

    def edit_type(self, c):
        pass