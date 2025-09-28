#!/usr/bin/env python3
"""Produce a placeholder EvergreenOS QEMU image artifact."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable


QCOW_NAME = "evergreenos.qcow2"


def create_qemu_image(ostree: Path, output: Path) -> Path:
    if not ostree.exists():
        raise FileNotFoundError(f"OSTree artifacts directory not found: {ostree}")

    output.mkdir(parents=True, exist_ok=True)
    image_path = output / QCOW_NAME

    timestamp = datetime.utcnow().isoformat() + "Z"
    contents = (
        "EvergreenOS QEMU image placeholder\n"
        f"OSTree source: {ostree}\n"
        f"Generated: {timestamp}\n"
    )
    image_path.write_text(contents)
    return image_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ostree", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    create_qemu_image(args.ostree, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
