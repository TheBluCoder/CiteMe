from aiohttp import ClientSession

class AsyncHTTPClient:
    """Manages a shared aiohttp session."""
    session = None

    @classmethod
    async def init_session(cls):
        if cls.session is None:
            cls.session = ClientSession()

    @classmethod
    async def close_session(cls):
        if cls.session:
            await cls.session.close()
            cls.session = None

    @classmethod
    async def getSession(cls)->ClientSession:
        if cls.session is None:
            await cls.init_session()
        return cls.session
