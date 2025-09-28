from pathlib import Path

from evergreen_os_image.configuration import (
    ComposeManifest,
    EnrollmentGreeterSource,
    FlatpakRemoteConfig,
    SecurityPolicies,
)


def test_compose_manifest_loads_expected_content():
    manifest = ComposeManifest.load()

    assert manifest.ref == "evergreenos/stable/x86_64"
    assert manifest.base_image == {"name": "fedora-silverblue", "version": "39"}
    assert "evergreen-device-agent" in manifest.packages_install
    assert "evergreen-enrollment-greeter" in manifest.packages_install
    assert "evergreen-device-agent.service" in manifest.systemd_enable
    assert set(manifest.update_channels) == {"stable", "beta", "dev"}


def test_security_policies_capture_hardening_defaults():
    policies = SecurityPolicies.load()

    assert policies.selinux_mode == "enforcing"
    assert policies.ssh_enabled is False
    assert policies.usbguard_default_policy == "block"
    assert "evergreen-device-agent" in policies.firewall_allowed_services
    assert policies.disk_encryption["tpm_auto_unlock"] is True
    assert policies.secure_boot_status == "planned"


def test_flatpak_remote_config_parses_ini_file(tmp_path: Path):
    config_path = tmp_path / "flatpak-remotes.conf"
    config_path.write_text(
        """
[Flatpak Remote "example"]
Url=https://example.test/repo
CollectionID=com.example.Stable
GPGKey=example-key
Enabled=false
""".strip()
    )

    parsed = FlatpakRemoteConfig.load(path=config_path)

    assert "example" in parsed.remotes
    remote = parsed.remotes["example"]
    assert remote.url == "https://example.test/repo"
    assert remote.collection_id == "com.example.Stable"
    assert remote.gpg_key == "example-key"
    assert remote.enabled is False


def test_flatpak_remote_config_repository_defaults():
    parsed = FlatpakRemoteConfig.load()

    assert set(parsed.remotes) == {"flathub", "evergreen"}
    assert parsed.remotes["flathub"].enabled is True
    assert parsed.remotes["evergreen"].url.startswith("https://apps.evergreen-os.dev")


def test_enrollment_greeter_source_points_to_external_repo():
    source = EnrollmentGreeterSource.load()

    assert source.repository_url == "https://github.com/evergreen-os/enrollment-greeter"
    assert "GTK enrollment greeter" in source.description
