# EnvShell

---

A shell for Hyprland, designed with simplicity and aesthetics in mind, by mimicing the look of MacOS as closely as possible.
All powered by [Fabric](https://github.com/Fabric-Development/fabric)

![screenshot-1](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-1.png)

![screenshot-2](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-2.png)

## Experimental

Please note that EnvShell is still in an experimental stage and is known to only work on the author's machine. It is not guaranteed to work on other systems. Proceed with caution and be prepared to encounter issues.

If you want to make it work on your machine, I would recommend changing the config file first, as it has paths for Nix Machines.

## Structure

- A TopPanel       (EnvPanel)
- A Dock           (EnvDock)
- An About Window  (EnvAbout)
- A OSMenu         (EnvMenu)
- A Notch          (EnvNotch)
- A SpotLight      (EnvLight)
- A ControlCenter  (EnvControlCenter)
- A Noti-Daemon    (EnvNoti)

## Usage

1. `cd envshell`
2. `python main.py`

### Hyprland

add this to your hyprland.conf

```conf
layerrule = blur, nwg-dock
layerrule = blur, fabric
layerrule = ignorezero, nwg-dock
layerrule = ignorezero, fabric
windowrulev2 = size 250 355,    title:(About Menu)
windowrulev2 = float,           title:(About Menu)
windowrulev2 = noborder,        title:(About Menu)
windowrulev2 = pin,             title:(About Menu)
```

## Credits

- [Hyprland](https://github.com/hyprwm/Hyprland)
- [Fabric](https://github.com/Fabric-Development/fabric)
- [Axenide's Dotfiles for Inspiration](https://github.com/Axenide/Dotfiles)

## Screenshots

![screenshot-3](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-3.png)

![screenshot-4](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-4.png)

![screenshot-5](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-5.png)

![screenshot-6](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-6.png)

## License

MIT
