
from . import init
from .Tools.process import Main
from .Tools.process import setup
import time

def main() -> None:
    init.main()

    setup.main()

    time.sleep(15)

    Main.main()


if __name__ == "__main__":
    main()
