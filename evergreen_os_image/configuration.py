"""Load EvergreenOS build-time configuration artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class FlatpakRemote:
    """Description of a single Flatpak remote configuration."""

    name: str
    url: str
    collection_id: str
    gpg_key: str | None = None
    enabled: bool = True
    default_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ComposeManifest:
    """Structured representation of the rpm-ostree compose manifest."""

    ref: str
    base_image: Mapping[str, str]
    base_image_metadata: Mapping[str, str]
    packages_install: Tuple[str, ...]
    packages_remove: Tuple[str, ...]
    overrides: Mapping[str, Tuple[str, ...]]
    systemd_enable: Tuple[str, ...]
    systemd_mask: Tuple[str, ...]
    update_channels: Tuple[str, ...]
    flatpak_remotes: Tuple[FlatpakRemote, ...]
    default_kargs: Tuple[str, ...]

    @classmethod
    def load(cls, path: Path | None = None) -> "ComposeManifest":
        """Load the compose manifest from disk."""

        manifest_path = path or REPO_ROOT / "configs" / "manifest.yaml"
        data = json.loads(manifest_path.read_text())

        remotes = tuple(
            FlatpakRemote(
                name=remote["name"],
                url=remote["url"],
                collection_id=remote["collection_id"],
                gpg_key=remote.get("gpg_key"),
                enabled=remote.get("enabled", True),
                default_refs=tuple(remote.get("default_refs", ())),
            )
            for remote in data.get("flatpak_remotes", [])
        )

        packages = data.get("packages", {})
        systemd = data.get("systemd", {})
        overrides = {
            key: tuple(value)
            for key, value in data.get("overrides", {}).items()
        }

        base_image = data["base_image"]
        minimal_base_image = {
            "name": base_image.get("name", ""),
            "version": base_image.get("version", ""),
        }
        extra_base_image = {
            key: value
            for key, value in base_image.items()
            if key not in minimal_base_image
        }

        return cls(
            ref=data["ref"],
            base_image=minimal_base_image,
            base_image_metadata=extra_base_image,
            packages_install=tuple(packages.get("install", ())),
            packages_remove=tuple(packages.get("remove", ())),
            overrides=overrides,
            systemd_enable=tuple(systemd.get("enable", ())),
            systemd_mask=tuple(systemd.get("mask", ())),
            update_channels=tuple(data.get("update_channels", ())),
            flatpak_remotes=remotes,
            default_kargs=tuple(data.get("default_kargs", ())),
        )


@dataclass(frozen=True)
class SecurityPolicies:
    """Aggregated EvergreenOS hardening policies."""

    selinux_mode: str
    ssh_enabled: bool
    usbguard_default_policy: str
    firewall_allowed_services: Tuple[str, ...]
    firewall_custom_rules: Tuple[str, ...]
    disk_encryption: Mapping[str, object]
    secure_boot_status: str
    auditing_enabled: bool
    auditing_profile: str | None

    @classmethod
    def load(cls, path: Path | None = None) -> "SecurityPolicies":
        """Load security policy configuration from disk."""

        policies_path = path or REPO_ROOT / "configs" / "security" / "policies.yaml"
        data = json.loads(policies_path.read_text())

        return cls(
            selinux_mode=data["selinux"]["mode"],
            ssh_enabled=data["ssh"]["enabled"],
            usbguard_default_policy=data["usbguard"]["default_policy"],
            firewall_allowed_services=tuple(data["firewall"].get("allowed_services", ())),
            firewall_custom_rules=tuple(data["firewall"].get("custom_rules", ())),
            disk_encryption=data["disk_encryption"],
            secure_boot_status=data["secure_boot"]["status"],
            auditing_enabled=data.get("auditing", {}).get("enabled", False),
            auditing_profile=data.get("auditing", {}).get("profile"),
        )


@dataclass(frozen=True)
class FlatpakRemoteConfig:
    """Parsed representation of the Flatpak remotes defaults file."""

    remotes: Mapping[str, FlatpakRemote]

    @classmethod
    def load(cls, path: Path | None = None) -> "FlatpakRemoteConfig":
        """Load the Flatpak remotes defaults file."""

        config_path = path or REPO_ROOT / "configs" / "defaults" / "flatpak-remotes.conf"
        remotes: Dict[str, FlatpakRemote] = {}
        current_remote: FlatpakRemote | None = None
        current_section: str | None = None

        def commit_remote(remote: FlatpakRemote | None) -> None:
            if remote is None:
                return
            remotes[remote.name] = remote

        with config_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("[") and line.endswith("]"):
                    commit_remote(current_remote)
                    current_section = line[1:-1]
                    if current_section.startswith("Flatpak Remote "):
                        name = current_section.split("\"", maxsplit=2)[1]
                        current_remote = FlatpakRemote(name=name, url="", collection_id="", gpg_key=None)
                    else:
                        current_remote = None
                    continue
                if current_remote is None or current_section is None:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key.lower() == "url":
                    current_remote = FlatpakRemote(
                        name=current_remote.name,
                        url=value,
                        collection_id=current_remote.collection_id,
                        gpg_key=current_remote.gpg_key,
                        enabled=current_remote.enabled,
                    )
                elif key.lower() == "collectionid":
                    current_remote = FlatpakRemote(
                        name=current_remote.name,
                        url=current_remote.url,
                        collection_id=value,
                        gpg_key=current_remote.gpg_key,
                        enabled=current_remote.enabled,
                    )
                elif key.lower() == "gpgkey":
                    current_remote = FlatpakRemote(
                        name=current_remote.name,
                        url=current_remote.url,
                        collection_id=current_remote.collection_id,
                        gpg_key=value,
                        enabled=current_remote.enabled,
                    )
                elif key.lower() == "enabled":
                    enabled = value.lower() in {"1", "true", "yes"}
                    current_remote = FlatpakRemote(
                        name=current_remote.name,
                        url=current_remote.url,
                        collection_id=current_remote.collection_id,
                        gpg_key=current_remote.gpg_key,
                        enabled=enabled,
                    )
        commit_remote(current_remote)
        return cls(remotes=remotes)


@dataclass(frozen=True)
class EnrollmentGreeterSource:
    """Pointer to the out-of-tree GTK enrollment greeter implementation."""

    repository_url: str
    description: str

    @classmethod
    def load(cls, path: Path | None = None) -> "EnrollmentGreeterSource":
        """Load metadata that references the external enrollment greeter."""

        source_path = path or REPO_ROOT / "enrollment-ui" / "greeter" / "source.json"
        data = json.loads(source_path.read_text())

        return cls(
            repository_url=data["repository"],
            description=data.get("description", ""),
        )


__all__ = [
    "FlatpakRemote",
    "ComposeManifest",
    "SecurityPolicies",
    "FlatpakRemoteConfig",
    "EnrollmentGreeterSource",
    "REPO_ROOT",
]
