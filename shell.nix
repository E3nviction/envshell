# shell.nix
# This is a simple Development Shell for envShell
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell rec {
  buildInputs = [
    pkgs.python312Packages.pip
    pkgs.python312Packages.pygobject3
    pkgs.python312Packages.psutil
    pkgs.gtk4
    pkgs.gtk3
    pkgs.librsvg
    pkgs.libdbusmenu-gtk3
    pkgs.gdk-pixbuf
    pkgs.cinnamon-desktop
    pkgs.pulseaudio
    pkgs.gtk-layer-shell
    pkgs.gobject-introspection
    pkgs.gnome-bluetooth
  ];

  # make shell use fish
  shell = pkgs.fish;

  shellHook = ''
    fish -C 'export PYTHONPATH="${pkgs.python312Packages.pygobject3}/lib/python3.12/site-packages"
    source venv/bin/activate.fish
    cd envshell
    c
    echo "envShell:dev is Ready..."'
  '';
}
