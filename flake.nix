{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
    kernel = import ./kernel.nix { inherit pkgs; };
    mkosi = pkgs.mkosi.overrideAttrs (oldAttrs: {
      version = "24.3-unstable-2025-01-08";
      src = pkgs.fetchFromGitHub {
        owner = "systemd";
        repo = "mkosi";
        rev = "d66bba09e3dde01f35ed1a9beb6cafeca07c3488";
        hash = "sha256-gYmZTDBwALzRI9FBTKOunZBKU5eRflH0T3vZmVLH8AU=";
      };
      # Ignore the patches. They can go in nixpkgs itself rather than this repo.
      patches = [];
      postPatch = "";
      postInstall = "mkdir -p $out/share/man/man1";
    });
  in {
    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        apt dpkg gnupg debootstrap
        squashfsTools dosfstools e2fsprogs mtools
        cryptsetup util-linux zstd qemu
        libseccomp
      ] ++ [ mkosi ];

      LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.libseccomp ];
      KERNEL_IMAGE = "${kernel}/bzImage";
      KERNEL_VERSION = kernel.version;
    };
  };
}