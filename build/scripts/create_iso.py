#!/usr/bin/env python3
"""Create a placeholder EvergreenOS installer ISO artifact."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable


ISO_NAME = "EvergreenOS.iso"


def create_iso(kickstart: Path, output: Path) -> Path:
    if not kickstart.is_file():
        raise FileNotFoundError(f"Kickstart file not found: {kickstart}")

    output.mkdir(parents=True, exist_ok=True)
    iso_path = output / ISO_NAME

    timestamp = datetime.utcnow().isoformat() + "Z"
    contents = (
        "EvergreenOS ISO placeholder\n"
        f"Kickstart: {kickstart}\n"
        f"Generated: {timestamp}\n"
    )
    iso_path.write_text(contents)
    return iso_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kickstart", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    create_iso(args.kickstart, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
