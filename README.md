# EvergreenOS Image Repository

EvergreenOS packages a secure, immutable workstation image on top of Fedora
Silverblue. This repository contains the rpm-ostree compose manifest, hardened
configuration defaults, installer assets, and CI automation necessary to build
and validate EvergreenOS deliverables.

## Repository layout

```
configs/                # rpm-ostree manifests, security policy, systemd units
  defaults/             # Flatpak remotes and agent defaults staged at build time
  manifest.yaml         # EvergreenOS compose definition
  security/policies.yaml# SELinux, SSH, USBGuard, firewall, and disk encryption
  services/             # Systemd unit templates installed into the image
build/                  # Composition helpers, ISO and QEMU scripts
  iso/evergreen.ks      # Kickstart driving installer media generation
  scripts/              # Utility scripts referenced by CI and Kickstart
artifacts/              # Populated by CI when building OSTree/ISO/QEMU outputs
.enrollment-ui/         # Metadata pointing to the GTK enrollment greeter source
```

Additional documentation and PRD context lives in the
`evergreen_os_image` python package which powers the compliance checks.

## Building EvergreenOS

Image builds run entirely with Python tooling and can be reproduced locally or
via GitHub Actions.

1. **Set up a containerised build environment**
   ```bash
   podman build -t evergreenos-build .
   podman run --rm -it -v "$PWD":/workspace evergreenos-build bash
   ```
2. **Compose the base OSTree commit**
   ```bash
   python build/scripts/compose.py \
     --manifest configs/manifest.yaml \
     --output artifacts/ostree
   ```
3. **Generate installer media**
   ```bash
   python build/scripts/create_iso.py \
     --kickstart build/iso/evergreen.ks \
     --output artifacts/iso
   ```
4. **Publish update channels**
   ```bash
   python build/scripts/publish_ostree.py \
     --source artifacts/ostree \
     --destination artifacts/ostree-repo \
     --version 1.0.0 \
     --gpg-key evergreen-ci-signing
   ```
5. **Produce a QEMU smoke-test image**
   ```bash
   python build/scripts/create_qemu_image.py \
     --ostree artifacts/ostree \
     --output artifacts/qemu
   ```
6. **Run the automated smoke test harness**
   ```bash
   python build/scripts/qemu_smoke.py \
     --image artifacts/qemu/evergreenos.qcow2 \
     --enroll-url https://enroll.evergreen-os.dev/demo
   ```

The GitHub Actions workflow in `.github/workflows/build.yml` mirrors these
steps on every commit and publishes the resulting artifacts.

## Hardware requirements

* x86_64 CPU with Intel VT-x or AMD-V
* 4 GB RAM minimum (8 GB recommended)
* 32 GB storage (NVMe or eMMC supported)
* TPM 2.0 for automatic LUKS unlocking
* UEFI firmware with Secure Boot capability

Legacy Chromebooks can be repurposed provided firmware updates unlock UEFI boot
and expose the TPM to the operating system.

## Installation options

### ISO installer

1. Write the ISO from `artifacts/iso/EvergreenOS.iso` to USB using Fedora Media
   Writer or `dd`.
2. Boot the target hardware and follow the automated installer. The Kickstart
   enables full-disk LUKS2 encryption, provisions a TPM-backed unlock slot, and
   activates the Evergreen enrollment greeter on first boot.
3. On first boot, complete the enrollment dialog to point the device agent at
   your Evergreen backend. The configuration is saved to
   `/etc/evergreen/agent/agent.yaml` and the device agent starts immediately
   afterwards.

### Live USB (developer preview)

1. Compose a live root filesystem by rebasing a Fedora Silverblue live ISO onto
   the Evergreen OSTree commit:
   ```bash
   sudo rpm-ostree rebase ostree-unverified-image:evergreenos/stable/x86_64
   ```
2. Copy `configs/services/*` and `configs/defaults/evergreen-agent.yaml` into the
   live image before sealing the USB stick.

## Customising EvergreenOS

* **Branding** – Replace wallpaper and login assets by dropping images into
  `configs/branding/` and updating the compose manifest overrides.
* **Languages** – Add additional language packs to the `packages.install`
  section of `configs/manifest.yaml` and regenerate the ISO.
* **Default applications** – Extend the Flatpak remotes or add `default_refs`
  entries to seed additional Evergreen-provided applications.
* **Security posture** – Tweak SELinux, firewall, or USBGuard defaults in
  `configs/security/policies.yaml`. The Python loader will surface the changes
  in compliance reports.

## Continuous integration

The CI pipeline builds rpm-ostree commits, installer ISOs, QEMU images, and
executes smoke tests on every push. Successful runs upload artifacts so that QA
and release engineering can download them for manual verification. The pipeline
is designed to plug into downstream signing infrastructure for both ISO and
OSTree outputs.

## Outstanding work

Chromebook-specific flashing utilities and recovery workflows remain under
development. The compliance report (`tests/test_compliance.py`) keeps that gap
visible until the tooling lands.
