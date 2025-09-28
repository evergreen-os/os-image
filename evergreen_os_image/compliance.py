"""Compliance reporting for the EvergreenOS image PRD."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .ci import GitHubWorkflow
from .configuration import (
    ComposeManifest,
    EnrollmentGreeterSource,
    FlatpakRemoteConfig,
    REPO_ROOT,
    SecurityPolicies,
)
from .prd import EvergreenOSPRD


@dataclass(frozen=True)
class RequirementStatus:
    """Represents implementation state for a single PRD requirement."""

    identifier: str
    implemented: bool
    details: str


@dataclass(frozen=True)
class PRDComplianceReport:
    """Summarises how the repository fares against the EvergreenOS PRD."""

    prd: EvergreenOSPRD
    statuses: Tuple[RequirementStatus, ...]

    @classmethod
    def current_state(cls) -> "PRDComplianceReport":
        """Return the compliance report for the current repository contents."""

        prd = EvergreenOSPRD.default()

        manifest = ComposeManifest.load()
        security = SecurityPolicies.load()
        flatpak_defaults = FlatpakRemoteConfig.load()
        services_dir = REPO_ROOT / "configs" / "services"
        device_agent_service = services_dir / "evergreen-device-agent.service"
        greeter_source = EnrollmentGreeterSource.load()
        workflow = GitHubWorkflow.load_default()

        base_image_composition = RequirementStatus(
            "base_image_composition",
            implemented=(
                manifest.base_image.get("name") == "fedora-silverblue"
                and "evergreen-device-agent" in manifest.packages_install
                and "evergreen-enrollment-greeter" in manifest.packages_install
            ),
            details=(
                "rpm-ostree compose manifest targeting Fedora Silverblue with Evergreen"
                " packages and services." if manifest.base_image.get("name") == "fedora-silverblue" else
                "Compose manifest missing or not targeting Fedora Silverblue."
            ),
        )

        device_agent_integration = RequirementStatus(
            "device_agent_integration",
            implemented=(
                "evergreen-device-agent" in manifest.packages_install
                and "evergreen-device-agent.service" in manifest.systemd_enable
                and device_agent_service.exists()
            ),
            details=(
                "Device agent packaged, enabled at boot, and systemd unit provided."
                if device_agent_service.exists()
                else "Device agent configuration incomplete."
            ),
        )

        flatpak_remotes = RequirementStatus(
            "flatpak_remotes",
            implemented=(
                len(manifest.flatpak_remotes) >= 2
                and "flathub" in flatpak_defaults.remotes
                and "evergreen" in flatpak_defaults.remotes
            ),
            details=(
                "Flatpak remotes for Flathub and Evergreen App Catalog are preconfigured."
                if len(manifest.flatpak_remotes) >= 2
                else "Flatpak remote definitions are incomplete."
            ),
        )

        security_hardening = RequirementStatus(
            "security_hardening",
            implemented=(
                security.selinux_mode == "enforcing"
                and not security.ssh_enabled
                and security.usbguard_default_policy == "block"
                and "evergreen-device-agent" in security.firewall_allowed_services
                and security.disk_encryption.get("tpm_auto_unlock") is True
            ),
            details=(
                "SELinux enforcing, SSH disabled, USBGuard blocking, firewall restricted,"
                " and disk encryption policies codified."
                if security.selinux_mode == "enforcing"
                else "Security policies incomplete."
            ),
        )

        update_channels = RequirementStatus(
            "update_channels",
            implemented=(
                set(prd.update_channels).issubset(set(manifest.update_channels))
            ),
            details=(
                "rpm-ostree manifest declares stable, beta, and dev channels."
                if set(prd.update_channels).issubset(set(manifest.update_channels))
                else "Update channel configuration missing from compose manifest."
            ),
        )

        statuses: Tuple[RequirementStatus, ...] = (
            base_image_composition,
            device_agent_integration,
            RequirementStatus(
                "enrollment_ui",
                implemented=bool(greeter_source.repository_url),
                details=(
                    "Enrollment greeter sourced from external repository at "
                    f"{greeter_source.repository_url}."
                    if greeter_source.repository_url
                    else "No GTK greeter application or configuration is present."
                ),
            ),
            flatpak_remotes,
            security_hardening,
            update_channels,
            RequirementStatus(
                "ci_pipeline",
                implemented=workflow.meets_prd_expectations,
                details=(
                    "GitHub Actions workflow builds rpm-ostree commits, ISOs, and QEMU smoke tests."
                    if workflow.meets_prd_expectations
                    else (
                        "GitHub Actions workflow missing or incomplete; automated builds "
                        "for OSTree, ISOs, and QEMU verification are not satisfied."
                    )
                ),
            ),
            RequirementStatus(
                "chromebook_support",
                implemented=False,
                details=(
                    "Firmware flashing scripts or low-resource installation guidance are absent."
                ),
            ),
        )

        return cls(prd=prd, statuses=statuses)

    @property
    def fully_compliant(self) -> bool:
        """Whether every PRD requirement is currently implemented."""

        return all(status.implemented for status in self.statuses)

    def missing_requirements(self) -> Tuple[RequirementStatus, ...]:
        """Return the requirements that are not yet implemented."""

        return tuple(status for status in self.statuses if not status.implemented)

    def implemented_requirements(self) -> Tuple[RequirementStatus, ...]:
        """Return the requirements that have been implemented."""

        return tuple(status for status in self.statuses if status.implemented)

    def requirement_map(self) -> Tuple[tuple[str, RequirementStatus], ...]:
        """Return a deterministic mapping of identifier to status."""

        return tuple((status.identifier, status) for status in self.statuses)


__all__ = ["RequirementStatus", "PRDComplianceReport"]
