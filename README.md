# EvergreenOS Image Repository (prototype)

This repository currently contains **only** a structured representation of the
EvergreenOS Product Requirements Document (PRD) along with automated checks that
highlight the gaps between the specification and the source code that would be
needed to build a functioning EvergreenOS image.

At the moment:

- A starter rpm-ostree compose manifest lives in `configs/manifest.yaml` and
  enables the Evergreen device agent alongside the enrollment greeter.
- Hardened defaults (SELinux enforcing, SSH disabled, USBGuard blocking, and a
  minimal firewall) live in `configs/security/policies.yaml`.
- Flatpak remotes for both Flathub and the Evergreen App Catalog are defined in
  `configs/defaults/flatpak-remotes.conf` and mirrored in the compose manifest.
- The GTK enrollment greeter is developed in a dedicated repository referenced
  via `enrollment-ui/greeter/source.json`, ensuring image builds can fetch the
  latest UI artifacts even though the code lives elsewhere.
- GitHub Actions automation (see `.github/workflows/build.yml`) demonstrates how
  rpm-ostree commits, installer ISOs, and QEMU smoke tests would be produced.
- Chromebook repurposing scripts and documentation are still missing; the
  compliance report calls this out as the remaining major PRD gap.

The accompanying unit test suite exercises the configuration artifacts and
ensures the compliance report continues to call out the work remaining to ship
EvergreenOS.
