class StreamChatBaseHandler():
    async def on_heartbeat(self, message: str):
        raise NotImplementedError()

    async def on_comment(self, message: str):
        raise NotImplementedError()

    async def on_gift(self, message: str):
        raise NotImplementedError()

    async def on_purchase(self, message: str):
        raise NotImplementedError()