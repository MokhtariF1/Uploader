from aioftp import Client

class FTPClient:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    async def upload(self, local_path: str, remote_path: str):
        async with Client.context(self.host, self.port, self.user, self.password) as client:
            await client.upload(local_path, remote_path)

    async def get_public_url(self, remote_path: str) -> str:
        return f"https://cdn.zivana.work.gd/{remote_path}"
