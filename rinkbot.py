#!/usr/bin/python3.9
# Copyright (c) 2022 Sylvie Liberman
import asyncio
import logging
import random
from aiohttp import web
from forest.core import Bot, Message, run_bot, app


class Rink:
    lock = asyncio.Lock()

    async def start_process(self) -> None:
        for i in range(5):
            self.proc = await asyncio.create_subprocess_exec(
                "./rink", stdin=-1, stdout=-1
            )
            logging.info(await self.proc.wait())

    async def line(self, line: str) -> str:
        assert self.proc.stdout and self.proc.stdin
        async with self.lock:
            self.proc.stdin.write(line.encode() + b"\n")
            await self.proc.stdin.drain()
            return (await self.proc.stdout.readline()).decode().strip()


class RinkBot(Bot):
    async def start_process(self) -> None:
        self.rink = Rink()
        asyncio.create_task(self.rink.start_process())
        await super().start_process()

    async def do_rink(self, message: Message) -> str:
        "performs unit conversion with rink.rs"
        return await self.rink.line(message.text)

    do_r = do_rink

    async def do_shuffle(self, message: Message) -> str:
        random.shuffle(message.tokens)
        return ", ".join(message.tokens)


async def handle_route(request: web.Request) -> web.Response:
    bot = request.app["bot"]
    assert isinstance(bot, RinkBot)
    out = await bot.rink.line(await request.text())
    return web.Response(text=out)


app.add_routes([web.post("/rink", handle_route)])

if __name__ == "__main__":
    run_bot(RinkBot, app)
