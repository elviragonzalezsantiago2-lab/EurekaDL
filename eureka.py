#!/usr/bin/env python3
"""
Lightweight entrypoint to maintain backward compatibility with the original orpheus CLI.
Run with: python eureka.py [args...]
This simply imports orpheus and delegates to its main() function.
"""

from __future__ import print_function

import sys

# Importing the orpheus module (repo root orpheus.py) and calling its main function.
# This avoids duplicating CLI logic and keeps behavior identical.
try:
    import orpheus
except Exception as e:
    print(f'Error: could not import orpheus module: {e}')
    sys.exit(1)


def main():
    try:
        orpheus.main()
    except KeyboardInterrupt:
        print('\n\t^C pressed - abort')
        sys.exit(1)


if __name__ == "__main__":
    main()
