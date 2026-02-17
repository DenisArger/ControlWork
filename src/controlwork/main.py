from __future__ import annotations

import sys

from .app import ControlWorkApplication


def main() -> int:
    app = ControlWorkApplication()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
