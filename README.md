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

## New

| | |
| --- | --- |
| The newly Designed Control Center. Now being more similar to the macOS Control Center. Although there still isn't any music player, Now theres actually a new Window if clicking on the Bluetooth widget. You can see it below! | ![The New Design of the Control Center](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-new-cc.png) |
| ![The Bluetooth Window](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-bluetooth.png) | This is the new Bluetooth window, accessed through the Control Center, give it a try! Here you can scan for new Devices or connect to already paired ones. On the right top you have a toggle for toggling the Bluetooth connection. Keep in mind that this is still in development |
| Now we come to one of the most experimental features, the launcher. It's Design definitly needs refactoring, but for the moment it does everything you need, Launching Apps. | ![Volume OSD](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-launcher.png) |
| ![](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-osd.png) | Are you tired of using an OSD server that's not integrated into your shell? Worry no more, because now you have your very own OSD server for volume control. |
| Do you like Ubuntu? Do you want to have a side-ways Dock? If so then this is the perfect Dock for you, because it supports the left, right, and bottom position and even a floating and full setting! | ![Dock at the Left Side, Filling the Side](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-left-dock-full.png) |
| ![Dock at the Left Side, Floating](https://raw.githubusercontent.com/E3nviction/envshell/refs/heads/master/assets/screenshot-left-dock-center.png) | This is the floating (or as it's called in the settings "center") mode for the Dock, as the name implies, it makes your dock float in the center, instead of taking up the whole space. |

## License

This Project is Licensed under the MIT License. See more at [LICENSE](license).
