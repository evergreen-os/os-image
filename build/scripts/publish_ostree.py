"""Publish EvergreenOS OSTree commits into release channels."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

CHANNELS = ("stable", "beta", "dev")


def publish(source: Path, destination: Path, version: str, gpg_key: str | None = None) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"OSTree source directory not found: {source}")

    destination.mkdir(parents=True, exist_ok=True)
    summary_path = destination / "summary.json"

    payload = {
        "version": version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": str(source),
        "channels": {},
        "gpg_key": gpg_key,
    }

    for channel in CHANNELS:
        channel_dir = destination / channel
        channel_dir.mkdir(exist_ok=True)
        payload["channels"][channel] = {
            "path": str(channel_dir),
            "published": True,
        }

    summary_path.write_text(json.dumps(payload, indent=2))
    return summary_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--gpg-key", default=None)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    publish(args.source, args.destination, args.version, args.gpg_key)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
