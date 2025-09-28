"""Structured representation of the EvergreenOS OS image PRD.

The module intentionally mirrors the canonical product requirements document
so that other tooling (such as build systems or documentation generators) can
reason about the expectations in code.  The data is distilled from the
"EvergreenOS OS Image – PRD" and exposed via an immutable dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple


@dataclass(frozen=True)
class EvergreenOSPRD:
    """In-memory representation of the EvergreenOS product requirements."""

    goals: Tuple[str, ...]
    non_goals: Tuple[str, ...]
    update_channels: Tuple[str, ...]
    repository_layout: Mapping[str, Mapping[str, object]]
    security_requirements: Mapping[str, str]
    success_metric_thresholds: Mapping[str, object]

    @classmethod
    def default(cls) -> "EvergreenOSPRD":
        """Return the canonical EvergreenOS PRD description.

        This method centralises the literal requirements so that tests and
        future consumers cannot accidentally diverge from the agreed contract.
        The returned dataclass is immutable, making it safe to share across the
        codebase.
        """

        repository_layout: Dict[str, Mapping[str, object]] = {
            "configs": {
                "manifest": "manifest.yaml",
                "subdirectories": ("branding", "services", "defaults", "security"),
            },
            "docs": ("prd.md", "build-instructions.md"),
            "enrollment-ui": {"subdirectories": ("greeter",)},
            "build": {
                "subdirectories": ("scripts", "iso", "ci"),
            },
            "artifacts": {"subdirectories": ("iso", "ostree", "qemu")},
            "root_files": ("README.md", "Makefile", "Dockerfile"),
        }

        security_requirements: Dict[str, str] = {
            "selinux": "enforcing",
            "ssh": "disabled",
            "usbguard": "enabled",
            "firewall": "minimal_open_ports",
            "disk_encryption": "luks2_tpm_auto_unlock",
            "secure_boot": "planned",
            "artifact_signing": "gpg_ostree_and_iso_signatures",
            "device_agent_policies": "enforced",
        }

        success_metric_thresholds: Dict[str, object] = {
            "fresh_install_boot_seconds": 60,
            "enrollment_completion_seconds": 120,
            "policy_application_seconds": 300,
            "ci_pipeline_artifacts": True,
            "update_rollback_verified": True,
            "artifact_signatures_status": "verified",
        }

        return cls(
            goals=(
                "Provide a fast, minimal, secure OS tailored for schools.",
                "Support both fresh installs and upgrades via OSTree.",
                "Boot reliably with atomic rollback if updates fail.",
                "Preconfigure EvergreenOS for zero-touch enrollment with device-agent.",
                "Ensure compatibility with older Chromebooks (EOL hardware repurpose).",
                "Automate CI builds for repeatable artifacts.",
            ),
            non_goals=(
                "Provide a mutable user-facing package manager.",
                "Develop a custom kernel beyond Fedora defaults.",
                "Ship an app store frontend within the OS image.",
                "Distribute proprietary firmware.",
            ),
            update_channels=("stable", "beta", "dev"),
            repository_layout=repository_layout,
            security_requirements=security_requirements,
            success_metric_thresholds=success_metric_thresholds,
        )

    def validate_success_metrics(self, observed_metrics: Mapping[str, object]) -> Tuple[str, ...]:
        """Validate observed metrics against the PRD success thresholds.

        Parameters
        ----------
        observed_metrics:
            Mapping of metric identifiers to their measured values.

        Returns
        -------
        Tuple[str, ...]
            A tuple of metric identifiers that failed validation.  An empty
            tuple indicates that all metrics satisfied the PRD expectations.
        """

        failures = []

        for metric, threshold in self.success_metric_thresholds.items():
            value = observed_metrics.get(metric)

            if isinstance(threshold, bool):
                if value is not threshold:
                    failures.append(metric)
                continue

            if isinstance(threshold, (int, float)):
                if value is None or not isinstance(value, (int, float)) or value > threshold:
                    failures.append(metric)
                continue

            if value != threshold:
                failures.append(metric)

        return tuple(failures)
