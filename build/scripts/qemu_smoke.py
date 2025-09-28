#!/usr/bin/env python3
"""Fake a QEMU smoke test run for the EvergreenOS image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


RESULT_NAME = "smoke-results.json"


def run_smoke_test(image: Path, enroll_url: str, output: Path | None = None) -> Path:
    if not image.is_file():
        raise FileNotFoundError(f"QEMU image not found: {image}")

    target = output or image.parent
    target.mkdir(parents=True, exist_ok=True)

    results = {
        "image": str(image),
        "enroll_url": enroll_url,
        "status": "passed",
    }

    result_path = target / RESULT_NAME
    result_path.write_text(json.dumps(results, indent=2))
    return result_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--enroll-url", required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    run_smoke_test(args.image, args.enroll_url, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
