import logging.config

from starlette.applications import Starlette
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Mount
from starlette.routing import Route

from xxtoolkit.configuration import cfg

logger = logging.getLogger(__name__)


async def health(_):
    return PlainTextResponse(status_code=200)


def create_app(api_routes, init_func=None):
    logging.config.dictConfig(cfg.log.config)

    _app = Starlette(debug=cfg.log.debug,
                     routes=[
                         Route("/_health", endpoint=health, methods=['GET']),
                         Mount(cfg.server.api.prefix, routes=api_routes, name='api'),
                     ])
    if init_func:
        _app.add_event_handler('startup', init_func)
    _app.add_middleware(GZipMiddleware)
    return _app
