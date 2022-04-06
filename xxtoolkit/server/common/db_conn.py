import logging

import asyncpg

from xxtoolkit.configuration import cfg

logger = logging.getLogger(__name__)


class DB:

    def __init__(self):
        self.pool = asyncpg.Pool(**cfg.server,
                                 connection_class=asyncpg.connection.Connection,
                                 record_class=asyncpg.Record)
        self.execute = self.pool.execute
        self.fetch = self.pool.fetch
        self.fetchrow = self.pool.fetchrow
        self.fetchval = self.pool.fetchval


db = DB()
