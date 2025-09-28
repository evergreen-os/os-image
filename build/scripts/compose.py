#!/usr/bin/env python3
"""Simulate composing an rpm-ostree tree for EvergreenOS."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


def _checksum_manifest(manifest: Path) -> str:
    content = manifest.read_bytes()
    return hashlib.sha256(content).hexdigest()


def compose(manifest: Path, output: Path) -> Path:
    """Create a placeholder rpm-ostree commit description."""

    if not manifest.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest}")

    output.mkdir(parents=True, exist_ok=True)

    data = {
        "manifest": str(manifest),
        "checksum": _checksum_manifest(manifest),
        "packages": _extract_packages(manifest.read_text()),
    }

    artifact_path = output / "compose.json"
    artifact_path.write_text(json.dumps(data, indent=2))
    return artifact_path


def _extract_packages(manifest_text: str) -> list[str]:
    try:
        data = json.loads(manifest_text)
    except json.JSONDecodeError:
        packages: list[str] = []
        for line in manifest_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                candidate = stripped[2:].strip()
                if candidate and " " not in candidate:
                    packages.append(candidate)
        return packages

    install = data.get("packages", {}).get("install", [])
    return [str(pkg) for pkg in install]


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    compose(args.manifest, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests
    raise SystemExit(main())
