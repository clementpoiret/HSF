{ pkgs, lib, config, inputs, ... }:
let
  buildInputs = with pkgs; [
    pythonManylinuxPackages.manylinux2014Package
    stdenv.cc.cc
    libuv
    zlib
  ];
in {
  # https://devenv.sh/packages/
  #packages = [ pkgs.git ];
  env = { LD_LIBRARY_PATH = "${with pkgs; lib.makeLibraryPath buildInputs}"; };

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync = { enable = true; };
    };
  };

  enterShell = ''
    uv sync
    . ./.devenv/state/venv/bin/activate
  '';

  enterTest = ''
    uv run pytest
  '';

  scripts.pytestcoverage.exec = ''
    uv sync
    uv pip install onnxruntime>=1.8.0 deepsparse>=1.4.0
    uv run coverage run --source=hsf -m pytest
    uv run coverage xml
  '';
}
