import aiohttp
from telethon import TelegramClient, types
from telethon.tl.custom import Button
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import config
import os
import socks
import logging
import traceback
import aiofiles


logging.basicConfig()

BASE_URL = 'https://s2.coinmarketcap.com/static/img/coins/64x64'

if not os.path.exists('sessionFiles'):
    os.mkdir('sessionFiles')
proxy = {
    'proxy_type': socks.PROXY_TYPE_SOCKS5,
    'addr': '45.94.47.18',
    'port': 8062,
    'username': 'unergtzc-dest',
    'password': 'vc3h2h86oht1'
}

bot = TelegramClient('sessionFiles/bot', config.API_ID,
                     config.API_HASH)

PEER = types.PeerChannel(config.CHANNEL_ID)
DOWNLOADS = f'./Downloads'
if not os.path.exists(DOWNLOADS):
    os.makedirs(DOWNLOADS)


def links():
    number = config.STARTING_NUMBER
    while True:
        number += 1
        URL = f'{BASE_URL}/{number}.png'
        yield URL


link_gen = links()


def generate_gis_link(image_url):
    return f'https://www.google.com/searchbyimage?&image_url={image_url}'


async def download_file(url, output_file):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(output_file, mode='wb')
                await f.write(await resp.read())
                await f.close()


async def watch_link():
    print('Watching link')
    async with aiohttp.ClientSession() as session:
        url = next(link_gen)
        while True:
            try:
                async with session.get(url=url) as response:
                    if response.status == 200:
                        btns = [
                            [Button.url(text="Google Image Search",
                                        url=generate_gis_link(url))]
                        ]
                        name = url.split('/')[-1]
                        file_loc = f'{DOWNLOADS}/{name}'
                        await download_file(url, file_loc)
                        await bot.send_file(PEER, file=file_loc, buttons=btns)
                        os.remove(file_loc)
                        url = next(link_gen)
                        continue
                    else:
                        await asyncio.sleep(0.2)
            except aiohttp.client_exceptions.ClientConnectionError:
                await asyncio.sleep(0.5)
            except Exception as e:
                traceback.print_exc()
                print('Unhandled exception')


async def main():
    for i in range(10):
        asyncio.create_task(watch_link())
    print('Bot is ready!')


if __name__ == '__main__':
    bot.start(bot_token=config.BOT_TOKEN)
    bot.loop.create_task(main())
    bot.run_until_disconnected()
