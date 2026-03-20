{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.uv
    pkgs.nodejs_20
    pkgs.sqlite
  ];
}