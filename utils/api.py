import aiohttp
from aiohttp import ContentTypeError

from settings import DOMAIN, AUTH_TOKEN, PORT

headers = {'Authorization': f'bearer {AUTH_TOKEN}'}


async def account_status():
    async with aiohttp.ClientSession() as session:
        url = f"http://{DOMAIN}:{PORT}/account/status"
        async with session.get(url, headers=headers) as resp:
            try:
                response = await resp.json()
            except ContentTypeError:
                return {"error": {'status': "400", "message": "Ошибка авторизации"}}
            return response


async def rename(port: int):
    async with aiohttp.ClientSession() as session:
        url = f"http://{DOMAIN}:{port}/rename"
        async with session.get(url, headers=headers, timeout=600) as resp:
            try:
                response = await resp.json()
            except ContentTypeError:
                return {"error": {'status': "400", "message": "Ошибка авторизации"}}
            except Exception as ex:
                return {"error": {'status': "400", "message": {ex}}}
            return response
