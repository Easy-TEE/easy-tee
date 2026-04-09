# Easy-TEE

Easy-TEE is a toolkit that turns your software into a secure, minimal VM image and lets anyone verify that it hasn’t been tampered with or modified.
It uses trusted execution environments (TEEs), like Intel TDX, and cryptographic attestations to prove exactly what code is running.

This repository is built from the same production-grade foundations that power Flashbots’ TEE products.
It is maintained as a mirror, so it stays in sync with upstream improvements from other Flashbots products.

## What Makes Easy-TEE different?

Images built with Easy-TEE run across Azure, GCP, and self-hosted environments, and support any software that runs on Debian Linux.
This means you can bring your existing software stack without changing your code, and also allow others to verify exactly what’s running.
Builds can be produced from either Linux or macOS without changing the resulting image.

Easy-TEE also gives you full control over what runs inside the VM image, with no extra layers between your software and the system it runs on.
The contents of images are fully transparent and easily auditable.

## How it Works

Easy-TEE builds minimal, reproducible VM images using [mkosi](https://github.com/systemd/mkosi).
Each image runs a stripped-down, security-hardened version of Debian with only the necessary dependencies required to run your software.
Image builds are completely reproducible and deterministic, meaning anyone can reproduce them bit-for-bit and verify that their image matches a live instance.

## Getting Started

### Prerequisites

By default, builds run inside a [Lima](https://lima-vm.io/) VM, which requires installing Lima prior to using this repository. This works on both Mac and Linux and requires no other dependencies.

Alternatively, it is possible to build natively with [Nix](https://nixos.org/download/) by creating a `.bypass-lima` file in the repo root.

### 1. Fork the repository

```bash
git clone https://github.com/<your-username>/easy-tee.git
cd easy-tee
```

### 2. Configure your image

Follow the guides in the repository wiki to define your image, add your software, and configure any required dependencies:

https://github.com/flashbots/easy-tee/wiki

### 3. Build your image

Once your image is configured, build it with:

```bash
make build IMAGE=<your-image-name>
```

This will produce a reproducible, hardened VM image that can be deployed and verified by your users through attestation.

### 4. Deploy your image

Follow the deployment guide to deploy your image to a cloud environment or a TDX-compatible server:

https://github.com/flashbots/easy-tee/wiki/Deployment-Guide
