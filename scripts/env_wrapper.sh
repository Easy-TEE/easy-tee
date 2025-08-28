#!/bin/bash
set -euo pipefail

LIMA_VM="${LIMA_VM:-tee-builder}"

# Check if Lima should be used
should_use_lima() {
    # Use Lima on macOS or if FORCE_LIMA is set
    [[ "$OSTYPE" == "darwin"* ]] || [ -n "${FORCE_LIMA:-}" ]
}

# Setup Lima if needed
setup_lima() {
    # Check if Lima is installed
    if ! command -v limactl &>/dev/null; then
        echo -e "Lima is not installed. Please install Lima to use this script."
        echo -e "Visit: https://lima-vm.io/docs/installation/"
        exit 1
    fi

    # Create VM if it doesn't exist
    if ! limactl list 2>/dev/null | grep -q "$LIMA_VM"; then
        lima_args=()
        if [ -n "${LIMA_CPUS:-}" ]; then
            lima_args+=("--cpus" "$LIMA_CPUS")
        fi
        if [ -n "${LIMA_MEMORY:-}" ]; then
            lima_args+=("--memory" "$LIMA_MEMORY")
        fi
        if [ -n "${LIMA_DISK:-}" ]; then
            lima_args+=("--disk" "$LIMA_DISK")
        fi

        echo -e "Creating $LIMA_VM VM..."
        limactl create -y \
            --name "$LIMA_VM" \
            "${lima_args[@]}" \
            lima.yaml
    fi

    # Start VM if not running
    if ! limactl list 2>/dev/null | grep "$LIMA_VM" | grep -q "Running"; then
        echo -e "Starting $LIMA_VM VM..."
        limactl start -y "$LIMA_VM"
        rm NvVars 2>/dev/null || true # Remove stray file created by QEMU
    fi
}

# Check if in nix environment
in_nix_env() {
    [ -n "${IN_NIX_SHELL:-}" ] || [ -n "${NIX_STORE:-}" ]
}

if [ $# -eq 0 ]; then
    echo "Error: No command specified"
    exit 1
fi

cmd=("$@")
if should_use_lima; then
    setup_lima

    mkosi_cache=/home/debian/mkosi-cache
    mkosi_output=/home/debian/mkosi-output

    if [[ "${cmd[0]}" == "mkosi" ]]; then
        limactl shell "$LIMA_VM" mkdir -p "$mkosi_cache" "$mkosi_output"

        cmd=(
            # First off, we need to run mkosi in a new user namespace,
            # because it creates files owned by multiple uids/gids, and we
            # either need to run as root, or use this unshare, which is safer.
            # See also:
            # https://manpages.debian.org/unstable/mkosi/mkosi.1.en.html#:~:text=Why%20do%20I%20see%20failures%20to%20chown%20files%20when%20building%20images
            "unshare"
            "--map-auto" "--map-current-user"
            "--setuid=0" "--setgid=0"
            "--"
            # Next, we use which because actual file is somewhere in /nix/store
            # and it's easier to explicitly specify it here instead of passing
            # $PATH.
            '$(which mkosi)'
            # Pass all original arguments except the first one (mkosi)
            "${cmd[@]:1}"
            # We can't use default cache dir from mnt/, because it is mounted
            # from host, and mkosi will try to preserve root/other permissions
            # without success.
            "--cache-directory=$mkosi_cache"
            # For the same reason, we need to use separate output dir.
            # mkosi tries to preserve ownership of output files, which fails,
            # as it is running from root in a user namespace.
            "--output-dir=$mkosi_output"
        )
    fi

    limactl shell "$LIMA_VM" bash -c \
        "cd /home/debian/mnt && nix develop -c bash -c '${cmd[*]}'"

    limactl shell "$LIMA_VM" mkdir -p /home/debian/mnt/build
    # TODO: quoting & run only after mkosi commands
    limactl shell "$LIMA_VM" bash -c "cp -rv $mkosi_output/* /home/debian/mnt/build/ || true"
    echo "Check ./build/ directory for output files"
    echo

    echo "Note: Lima VM is still running. To stop it, run: limactl stop $LIMA_VM"
else
    if in_nix_env; then
        exec "${cmd[@]}"
    else
        exec nix develop -c "${cmd[@]}"
    fi
fi
