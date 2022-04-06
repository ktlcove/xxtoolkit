import typing

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response

from xxtoolkit.common.object import XXToolkitObject
from xxtoolkit.common.error import XXToolkitException


class ABCApiEndpoint(HTTPEndpoint):

    async def pre_hook(self, req: Request) -> Request:
        return req

    async def post_hook(self, resp: Response) -> Response:
        return resp

    async def finally_hook(self, req, resp) -> None:
        pass

    async def dispatch(self) -> None:
        request = Request(self.scope, receive=self.receive)
        handler_name = (
            "get"
            if request.method == "HEAD" and not hasattr(self, "head")
            else request.method.lower()
        )

        handler: typing.Callable[[Request], typing.Any] = getattr(
            self, handler_name, self.method_not_allowed
        )

        try:
            request = await self.pre_hook(request)
            response = await handler(request)
            if isinstance(response, XXToolkitObject):
                response = ApiObjectResponse(response)
            response = await self.post_hook(response)
        except XXToolkitException as e:
            response = ApiObjectResponse(e)
            await self.finally_hook(request, response)

        await response(self.scope, self.receive, self.send)


class ApiObjectResponse(Response):
    media_type = "application/json"

    def render(self, content: XXToolkitObject) -> bytes:
        return content.xx_json().encode(self.charset)
