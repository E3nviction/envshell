from .conf import Config

c = Config()
c.window_rule(is_wmclass="Hyprland", rule="autohide-panel")
c.window_rule(is_wmclass="albert", rule="autohide-panel")
c.window_rule(is_title="Albert", rule="autohide-panel")
c.window_rule(is_wmclass="main.py", rule="autohide-panel")

app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}

c.window_rename(from_wmclass="code", to_wmclass="vscode")
c.window_rename(from_wmclass="vesktop", to_wmclass="discord")

# Ignore
c.window_rule(is_wmclass="kitty-dropterm", rule="ignore")
c.window_rule(is_wmclass="albert", rule="ignore")
c.window_rule(is_wmclass="main.py", rule="ignore")

# Dock
c.pin_window(wmclass="org.gnome.Nautilus", command="nautilus")
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

# Workspace
c.workspace_rule(9)

# Icons
icon_list = []
icon_dir = "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/"