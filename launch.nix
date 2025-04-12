{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell rec {
  buildInputs = [
    pkgs.python312Packages.pip
    pkgs.python312Packages.pygobject3
    pkgs.python312Packages.psutil
    pkgs.gtk4
    pkgs.gtk3
    pkgs.librsvg
    pkgs.libdbusmenu-gtk2
    pkgs.libdbusmenu-gtk3
    pkgs.gdk-pixbuf
    pkgs.cinnamon-desktop
    pkgs.pulseaudio
    pkgs.gtk-layer-shell
    pkgs.gobject-introspection
    pkgs.gnome-bluetooth
  ];

  shellHook = ''
    echo "Setting Timezone..."
    echo "use export TZ={insert your timezone} to change it to your timezone"
    export TZ=CEST-2
    echo "Setting up linkers for python."
    export PYTHONPATH="${pkgs.python312Packages.pygobject3}/lib/python3.12/site-packages"

    echo "Activating python virtual env..."
    source ./venv/bin/activate
    python ./envshell/watcher.py
  '';
}
