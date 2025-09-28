#version=F39
install
text
lang en_US.UTF-8
keyboard us
timezone America/Chicago --isUtc
network  --bootproto=dhcp --hostname=evergreenos
services --enabled="usbguard,firewalld" --disabled="sshd"
selinux --enforcing
authselect --enablesudo --useshadow
rootpw --lock
user --name=evergreen --password="evergreen" --plaintext --groups=wheel

bootloader --timeout=1 --append="rd.luks.options=tpm2-device=auto"
zerombr
clearpart --all --initlabel
autopart --type=thinp --encrypted --passphrase="evergreen" --luks-version=luks2 --cipher=aes-xts-plain64
reqpart --add-boot

%packages
@core
@standard
@workstation-product-environment
rpm-ostree
usbguard
NetworkManager
chrony
%end

%post --log=/var/log/evergreen-install.log
mkdir -p /var/lib/evergreen
cat <<'SCRIPT' >/var/lib/evergreen/firstboot-enroll.sh
#!/usr/bin/env bash
set -euo pipefail

default_config="/etc/evergreen/agent/agent.yaml"
mkdir -p "$(dirname "${default_config}")"
if [[ ! -f "${default_config}" ]]; then
  cp /usr/share/evergreen/defaults/agent.yaml "${default_config}"
fi
systemctl enable evergreen-enrollment-greeter.service
SCRIPT
chmod 0755 /var/lib/evergreen/firstboot-enroll.sh

cat <<'UNIT' >/etc/systemd/system/evergreen-firstboot.service
[Unit]
Description=Run Evergreen first boot enrollment
Before=evergreen-device-agent.service
ConditionPathExists=!/var/lib/evergreen/enrollment.complete

[Service]
Type=oneshot
ExecStart=/var/lib/evergreen/firstboot-enroll.sh

[Install]
WantedBy=multi-user.target
UNIT

systemctl enable evergreen-firstboot.service
%end

%post --nochroot --log=/mnt/sysimage/var/log/evergreen-post.log
cp -a /run/install/repo/configs/defaults/evergreen-agent.yaml /mnt/sysimage/usr/share/evergreen/defaults/agent.yaml || true
install -Dm0755 /run/install/repo/build/scripts/write_agent_config.sh /mnt/sysimage/usr/lib/evergreen/write-agent-config.sh
%end

%post --erroronfail --nochroot
ostree config --repo=/mnt/sysimage/ostree/repo set sysroot.bootloader none || true
%end
