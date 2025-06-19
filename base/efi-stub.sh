#!/bin/bash
set -euo pipefail

# Use a version of systemd-boot that is compatible with measured-boot script
SYSTEMD_BOOT_URL="https://snapshot.debian.org/archive/debian/20240314T094714Z/pool/main/s/systemd/systemd-boot-efi_255.4-1_amd64.deb"
TEMP_DEB="$BUILDROOT/systemd-boot.deb"
curl -L -o "$TEMP_DEB" "$SYSTEMD_BOOT_URL"
mkosi-chroot dpkg -i /systemd-boot.deb
rm -f "$TEMP_DEB"