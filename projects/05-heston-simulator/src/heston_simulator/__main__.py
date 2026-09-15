"""Allow ``python -m heston_simulator``."""

from heston_simulator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
