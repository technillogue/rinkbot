#!/usr/bin/python3.9
# Copyright (c) 2022 Sylvie Liberman
import asyncio
from forest.core import Bot, Message, run_bot


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

    async def do_rink(self, message: Message) -> str:
        "performs unit conversion with rink.rs"
        return await self.rink.line(message.text)

    do_r = do_rink


if __name__ == "__main__":
    run_bot(RinkBot)
