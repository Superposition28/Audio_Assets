"""This module runs the initialization, setup, and main process for the audio assets."""
import time
import sys
import os
from pathlib import Path
import configparser

def main() -> None:
    """Runs the initialization, setup, and main process for the audio assets."""

    module_dir = Path(__file__).resolve().parent
    config_file_path = module_dir / "Audconf.ini"

    print("running module initialization")
    # Initialize the module (ensures Audconf.ini exists)
    init.main(module_dir)

    # Load configuration once
    config = configparser.ConfigParser(allow_no_value=True)
    if config_file_path.exists():
        config.read(config_file_path)
        print(f"Configuration loaded from {config_file_path}")
    else:
        print(f"Error: Configuration file {config_file_path} not found after init.", file=sys.stderr)
        sys.exit(1)

    print("running tool setup")
    # Pass the config object to setup.main
    setup.main(config)

    print("running main process")
    # Pass the config object to Main.main
    Main.main(config)


if __name__ == "__main__":
    import init
    from Tools.process import Main
    from Tools.process import setup

    main()
else:
    from . import init
    from .Tools.process import Main
    from .Tools.process import setup
