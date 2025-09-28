import pytest

from evergreen_os_image.prd import EvergreenOSPRD


def test_prd_goals_match_prd_spec():
    prd = EvergreenOSPRD.default()
    assert prd.goals == (
        "Provide a fast, minimal, secure OS tailored for schools.",
        "Support both fresh installs and upgrades via OSTree.",
        "Boot reliably with atomic rollback if updates fail.",
        "Preconfigure EvergreenOS for zero-touch enrollment with device-agent.",
        "Ensure compatibility with older Chromebooks (EOL hardware repurpose).",
        "Automate CI builds for repeatable artifacts.",
    )


def test_repository_layout_contains_key_directories():
    prd = EvergreenOSPRD.default()
    layout = prd.repository_layout

    assert layout["configs"]["manifest"] == "manifest.yaml"
    assert "branding" in layout["configs"]["subdirectories"]
    assert "services" in layout["configs"]["subdirectories"]
    assert "artifacts" in layout
    assert set(layout["artifacts"]["subdirectories"]) == {"iso", "ostree", "qemu"}


def test_success_metrics_validation_passes_when_thresholds_met():
    prd = EvergreenOSPRD.default()
    result = prd.validate_success_metrics(
        {
            "fresh_install_boot_seconds": 45,
            "enrollment_completion_seconds": 90,
            "policy_application_seconds": 240,
            "ci_pipeline_artifacts": True,
            "update_rollback_verified": True,
            "artifact_signatures_status": "verified",
        }
    )
    assert result == ()


def test_success_metrics_validation_returns_failures_when_thresholds_exceeded():
    prd = EvergreenOSPRD.default()
    result = prd.validate_success_metrics(
        {
            "fresh_install_boot_seconds": 75,
            "enrollment_completion_seconds": 180,
            "policy_application_seconds": 400,
            "ci_pipeline_artifacts": False,
            "update_rollback_verified": False,
            "artifact_signatures_status": "missing",
        }
    )

    assert "fresh_install_boot_seconds" in result
    assert "enrollment_completion_seconds" in result
    assert "policy_application_seconds" in result
    assert "ci_pipeline_artifacts" in result
    assert "update_rollback_verified" in result
    assert "artifact_signatures_status" in result


def test_update_channels_match_prd_spec():
    prd = EvergreenOSPRD.default()
    assert prd.update_channels == ("stable", "beta", "dev")


def test_security_requirements_detail():
    prd = EvergreenOSPRD.default()
    requirements = prd.security_requirements
    assert requirements["selinux"] == "enforcing"
    assert requirements["ssh"] == "disabled"
    assert requirements["usbguard"] == "enabled"
    assert requirements["disk_encryption"] == "luks2_tpm_auto_unlock"
    assert "secure_boot" in requirements
