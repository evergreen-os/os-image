from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

compose_module = importlib.import_module("build.scripts.compose")
create_iso_module = importlib.import_module("build.scripts.create_iso")
create_qemu_module = importlib.import_module("build.scripts.create_qemu_image")
qemu_smoke_module = importlib.import_module("build.scripts.qemu_smoke")


@pytest.fixture
def manifest_file(tmp_path: Path) -> Path:
    path = tmp_path / "manifest.yaml"
    path.write_text("packages:\n  - evergreen-device-agent\n  - enrollment-greeter\n")
    return path


def test_compose_generates_artifact(tmp_path: Path, manifest_file: Path) -> None:
    output = tmp_path / "ostree"
    artifact = compose_module.compose(manifest_file, output)

    assert artifact.exists()
    data = json.loads(artifact.read_text())
    assert data["checksum"]
    assert "evergreen-device-agent" in data["packages"]


@pytest.fixture
def kickstart_file(tmp_path: Path) -> Path:
    path = tmp_path / "evergreen.ks"
    path.write_text("# kickstart")
    return path


def test_create_iso(tmp_path: Path, kickstart_file: Path) -> None:
    output = tmp_path / "iso"
    iso_path = create_iso_module.create_iso(kickstart_file, output)

    assert iso_path.exists()
    contents = iso_path.read_text()
    assert "EvergreenOS ISO placeholder" in contents
    assert str(kickstart_file) in contents


@pytest.fixture
def ostree_dir(tmp_path: Path) -> Path:
    path = tmp_path / "ostree"
    (path / "repo").mkdir(parents=True)
    return path


def test_create_qemu_image(tmp_path: Path, ostree_dir: Path) -> None:
    output = tmp_path / "qemu"
    image_path = create_qemu_module.create_qemu_image(ostree_dir, output)

    assert image_path.exists()
    contents = image_path.read_text()
    assert "EvergreenOS QEMU image placeholder" in contents
    assert str(ostree_dir) in contents


def test_qemu_smoke(tmp_path: Path) -> None:
    image = tmp_path / "evergreenos.qcow2"
    image.write_text("placeholder")

    results = qemu_smoke_module.run_smoke_test(image, "https://ci.test/tenant")

    assert results.exists()
    payload = json.loads(results.read_text())
    assert payload["status"] == "passed"
    assert payload["image"] == str(image)
