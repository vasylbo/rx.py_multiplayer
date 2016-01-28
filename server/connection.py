from aiohttp.web import WebSocketResponse
from rx import Observable
from rx.observer import Observer
from rx.subjects import Subject


class WSSubject(Observer):
    def __init__(self, web_socket: WebSocketResponse):
        super(WSSubject, self).__init__()
        self._web_socket = web_socket
        self._push_subject = Subject()

    def to_observable(self):
        return self._push_subject

    async def process(self):
        async for msg in self._web_socket:
            self._push_subject.on_next(msg)

        self._push_subject.on_completed()

    def on_next(self, data):
        self._web_socket.send_str(data)

    def on_completed(self):
        # close web socket
        # has to be coroutine to close ws
        pass

    def on_error(self, error):
        # send error and close web socket
        pass


class WSHandlerSubject(Observable):
    def __init__(self):
        self._subject = Subject()
        super(WSHandlerSubject, self).__init__(self._subject.subscribe)

    async def __call__(self, *args, **kwargs):
        request = args[0]
        web_socket = WebSocketResponse()
        await web_socket.prepare(request)

        ws_subject = WSSubject(web_socket)

        self._subject.on_next(ws_subject)

        await ws_subject.process()

        return web_socket
