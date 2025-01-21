{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
    kernel = import ./kernel.nix { inherit pkgs; };
    mkosi = pkgs.mkosi;
  in {
    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        apt dpkg gnupg debootstrap
        squashfsTools dosfstools e2fsprogs mtools
        cryptsetup util-linux zstd qemu
      ] ++ [ mkosi ];

      KERNEL_IMAGE = "${kernel}/bzImage";
      KERNEL_VERSION = kernel.version;
    };
  };
}