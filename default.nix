{ pkgs ? import <nixpkgs> {} }:

let
  pythonWithPackages = pkgs.python3.withPackages (ps: with ps; [
    pygame
    loguru
    pygobject3
    psutil
    setproctitle
    pulsectl
    pydantic
    pyopengl
    numpy
  ]);

  extraDeps = [
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
    pkgs.playerctl
  ];

  env = pkgs.symlinkJoin {
    name = "python-env";
    paths = [ pythonWithPackages ] ++ extraDeps;
    preferLocalBuild = true;
    allowSubstitutes = true;
  };
in
pkgs.writeShellScriptBin "python-env-shell" ''
  echo "Setting Timezone..."
  echo "use export TZ={insert your timezone} to change it to your timezone"
  export TZ=CEST-2

  echo "Setting up linkers for python."
  export PATH=${env}/bin:$PATH

  export PYTHONPATH="${pkgs.python312Packages.pygobject3}/lib/python3.12/site-packages:$PYTHONPATH"

  export GI_TYPELIB_PATH="${pkgs.gobject-introspection}/lib/girepository-1.0:$GI_TYPELIB_PATH"
  export LD_LIBRARY_PATH="${env}/lib:$LD_LIBRARY_PATH"

  if [ -f "${toString ./.}/venv/bin/activate" ]; then
    . "${toString ./.}/venv/bin/activate"
  fi

  exec python "$@"
''