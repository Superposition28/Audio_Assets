"""This module runs the initialization, setup, and main process for the audio assets."""
import time
import sys
import os
from pathlib import Path

def main() -> None:
    """Runs the initialization, setup, and main process for the audio assets."""

    module_dir = Path(__file__).resolve().parent

    print("running module initialization")
    # Initialize the module
    init.main(module_dir)

    print("running tool setup")
    setup.main(module_dir)

    exit(0)
    
    print("running main process")
    Main.main(module_dir)


if __name__ == "__main__":
    import init
    from Tools.process import Main
    from Tools.process import setup

    main()
else:
    from . import init
    from .Tools.process import Main
    from .Tools.process import setup
