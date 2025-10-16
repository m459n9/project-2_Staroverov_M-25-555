#!/usr/bin/env python3
from .engine import welcome

def main() -> int:
    return welcome()

if __name__ == "__main__":
    raise SystemExit(main())