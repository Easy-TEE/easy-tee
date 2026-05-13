# Easy-TEE

Easy-TEE is a toolkit for building reproducible, minimal VM images that run inside trusted execution environments (TEEs) and produce cryptographic attestations of exactly what's running. It is built on the same foundations as [Flashbots](https://flashbots.net/)' production TEE products and stays in sync with upstream improvements.

## What you can do with it

- Package any Debian-compatible software stack into a TEE image without changing your code
- Deploy the same image to GCP, Azure, or self-hosted TDX hardware
- Produce bit-identical builds from either a Linux or macOS host
- Generate attestation values that let users verify a running instance matches the published source
- Audit every component of your image

## How it works

Easy-TEE uses [mkosi](https://github.com/systemd/mkosi) to build minimal, security-hardened Debian images containing only what your software needs to run. Your software runs directly on Linux with no extra abstraction layers. Builds are deterministic, so anyone with the same source tree can reproduce the image bit-for-bit and check that it matches what's running on a deployed instance.

## Getting Started

### Prerequisites

By default, builds run inside a [Lima](https://lima-vm.io/) VM, which works on both macOS and Linux and requires no other dependencies. Alternatively, you can build natively with [Nix](https://nixos.org/download/) on Linux by creating a `.bypass-lima` file in the repo root.

### 1. Fork the repository

```bash
git clone https://github.com/<your-username>/easy-tee.git
cd easy-tee
```

### 2. Configure your image

Follow the guides in the [wiki](https://github.com/flashbots/easy-tee/wiki) to define your image, add your software, and configure any required dependencies.

### 3. Build your image

```bash
make build IMAGE=<your-image-name>
```

This produces a reproducible, hardened VM image that can be deployed and verified through attestation.

### 4. Deploy your image

See the [Deployment Guide](https://github.com/flashbots/easy-tee/wiki/Deployment-Guide) for cloud and self-hosted deployment instructions.
