"""
Nocturne of Paws — Entry Point
Gothic romantic fantasy interactive story game.

Runs both natively (desktop Python) and in the browser (pygbag/WASM).
pygbag requires a top-level `asyncio.run(main())` with an async game loop.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core.engine import Engine


async def main():
    engine = Engine()
    await engine.run_async()


if __name__ == "__main__":
    asyncio.run(main())
