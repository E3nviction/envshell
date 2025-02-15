from .conf import Config

c = Config()
c.window_rule(is_wmclass="Hyprland", rule="autohide-panel")
c.window_rule(is_wmclass="albert", rule="autohide-panel")
c.window_rule(is_title="Albert", rule="autohide-panel")
c.window_rule(is_wmclass="main.py", rule="autohide-panel")
c.window_rule(is_wmclass="ulauncher", rule="autohide-panel")

app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}

c.window_rename(from_wmclass="code", to_wmclass="vscode")
c.window_rename(from_wmclass="vesktop", to_wmclass="discord")

# Ignore
c.window_rule(is_wmclass="kitty-dropterm", rule="ignore")
c.window_rule(is_wmclass="albert", rule="ignore")
c.window_rule(is_wmclass="main.py", rule="ignore")
c.window_rule(is_wmclass="ulauncher", rule="ignore")

# Dock
c.pin_window(wmclass="org.gnome.Nautilus", command="nautilus")
c.pin_window(wmclass="org.gnome.Settings", command="XDG_CURRENT_DESKTOP=GNOME gnome-control-center")
c.pin_window(wmclass="org.gnome.Software", command="gnome-software")
c.pin_window(wmclass="gnome-disks", command="gnome-disks")
c.pin_window(wmclass="org.gnome.baobab", command="baobab")
c.pin_window(wmclass="kitty", command="kitty")
c.pin_window(wmclass="brave-browser", command="brave")
c.pin_window(wmclass="code", command="code")
c.pin_window(wmclass="org.gnome.Calculator", command="gnome-calculator")
c.pin_window(wmclass="org.gnome.TextEditor", command="gnome-text-editor")
c.pin_window(wmclass="org.gnome.Loupe", command="Image Viewer")
c.pin_window(wmclass="org.gnome.clocks", command="gnome-clocks")
c.pin_window(wmclass="krita", command="krita")
c.pin_window(wmclass="spotify", command="spotify")
c.pin_window(wmclass="vesktop", command="vesktop")
c.pin_window(wmclass="org.keepassxc.KeePassXC", command="keepassxc")
c.pin_window(wmclass="com.github.rafostar.Clapper", command="clapper")
c.pin_window(wmclass="blender", command="blender")
c.pin_window(wmclass="obsidian", command="obsidian")

# Apps
c.window_rule(from_wmclass="None", to_title="Hyprland")
c.window_rule(from_wmclass="code", to_title="Visual Studio Code")
c.window_rule(from_wmclass="brave-browser", to_title="Brave Browser")
c.window_rule(from_wmclass="discord", to_title="Discord")
c.window_rule(from_wmclass="vesktop", to_title="Vesktop")
c.window_rule(from_wmclass="kitty", to_title="Kitty")
c.window_rule(from_wmclass="org.keepassxc.KeePassXC", to_title="KeePassXC")
c.window_rule(from_wmclass="org.gnome.Terminal", to_title="Terminal")
c.window_rule(from_wmclass="org.gnome.Nautilus", to_title="Finder")
c.window_rule(from_wmclass="org.gnome.NautilusPreviewer", to_title="Finder")
c.window_rule(from_wmclass="org.gnome.Maps", to_title="Maps")
c.window_rule(from_wmclass="org.gnome.Calculator", to_title="Calculator")
c.window_rule(from_wmclass="org.gnome.Clocks", to_title="Clocks")
c.window_rule(from_wmclass="brave-chatgpt.com__-Default", to_title="ChatGPT")
c.window_rule(from_wmclass="obsidian", to_title="Obsidian")
c.window_rule(from_wmclass="blender", to_title="Blender")
c.window_rule(from_wmclass="spotify", to_title="Spotify")
c.window_rule(from_wmclass="org.gnome.Software", to_title="App Store")
c.window_rule(from_wmclass="org.gnome.Settings", to_title="Settings")
c.window_rule(from_wmclass="gnome-disks", to_title="Disks")
c.window_rule(from_wmclass="org.gnome.baobab", to_title="Disk Usage")
c.window_rule(from_wmclass="org.gnome.TextEditor", to_title="Text Editor")
c.window_rule(from_wmclass="org.gnome.Loupe", to_title="Image Viewer")
c.window_rule(from_wmclass="org.gnome.clocks", to_title="Clocks")
c.window_rule(from_wmclass="krita", to_title="Krita")
c.window_rule(from_wmclass="com.github.rafostar.Clapper", to_title="Media Player")


# Workspace
c.workspace_rule(9)


# Shell
c.shell_rule(rule="dock-position", value="bottom center")
c.shell_rule(rule="dock-margin", value="0 0 -47 0")
c.shell_rule(rule="dock-margin-active", value="0 0 5 0")
c.shell_rule(rule="dock-rounding", value="15px")
c.shell_rule(rule="dock-orientation", value="horizontal")

c.shell_rule(rule="panel-position", value="top left right")
c.shell_rule(rule="panel-margin", value="0 0 0 0")
c.shell_rule(rule="panel-rounding", value="0")
c.shell_rule(rule="panel-date-format", value="%a %b %d %H:%M")
c.shell_rule(rule="panel-icon", value="")

c.shell_rule(rule="about-window-width", value=250)
c.shell_rule(rule="about-window-height", value=355)
c.shell_rule(rule="about-window-resizable", value=False)
c.shell_rule(rule="about-computer-label", value="Env Shell")
c.shell_rule(rule="about-computer-caption", value="ESH, 2024")
c.shell_rule(rule="about-more-info", value="https://github.com/E3nviction/envshell")

env_menu_option_labels = {
    "About this PC": ["NOTEDITABLE"],
    "System Settings...": ["code ~/.config/"],
    "Nix Store...": ["xdg-open https://search.nixos.org/packages"],
    "Force Quit App": ["hyprctl activewindow -j | jq -r .pid | xargs kill -9", "󰘶 󰘳 C"],
    "Sleep": ["systemctl suspend", "󰘶 󰘳 M"],
    "Restart...": ["systemctl restart", "󰘶 󰘳 M"],
    "Shut Down...": ["shutdown now", "󰘶 󰘳 M"],
    "Lock Screen": ["hyprlock", "󰘳 L"],
}

i = 0
for k, v in env_menu_option_labels.items():
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-label", value=k)
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-on-click", value=v[0])
    if len(v) > 1:
        c.shell_rule(rule=f"panel-env-menu-option-{i+1}-keybind", value=v[1])
    i += 1


# Icons
icon_list = []
icon_dir = "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/"
