# envShell Mods

EnvShell now supports adding custom buttons inside the top panel, called **Mods**.

## Creating Mods

Mods are dropdowns inside the top panel. You can create as many as you want.

### Basic Structure

To create a mod, follow these steps:

1. Define a section with the mod's name.
2. Optionally, set an icon and its size (default: 24px).
3. Add options with labels, keybinds, and on-click commands.
4. Use `divider = true` to add dividers between options.

### Example Mod

```toml
[Mods.terminal]
icon = "/run/current-system/sw/share/icons/WhiteSur-dark/apps/symbolic/terminal-app-symbolic.svg"
icon-size = 18

[[Mods.terminal.options]]
label = "Terminal"
on-clicked = "kitty"

[[Mods.terminal.options]]
label = "Terminal but scary"
on-clicked = "ghostty"
divider = true
```

## Features

- **List-based dropdowns**: Static labels with on-click commands.
- **Future plans**: Dynamic labels, more option types, and conditional commands.

Stay tuned for updates!

## More Mods?

Here is a small list of example mods.

- [Terminals](https://github.com/E3nviction/envShell/blob/master/docs/mods/terminal.toml)
- [Notifier](https://github.com/E3nviction/envShell/blob/master/docs/mods/notifier.toml)
- [Weather](https://github.com/E3nviction/envShell/blob/master/docs/mods/weather.toml)