"""
Nocturne of Paws — Entry Point
Gothic romantic fantasy interactive story game.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core.engine import Engine


def main():
    engine = Engine()
    engine.run()


if __name__ == "__main__":
    main()
