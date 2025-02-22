from .conf import Config
from fabric.utils import get_relative_path
import tomllib
import json


app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}
with open("./config/default_config.toml", "rb") as f:
    default_config = tomllib.load(f)
    config = default_config
try:
    with open("./config/config.toml", "rb") as f:
        config = tomllib.load(f)
except:
    print("Failed to load config.toml, using default config")
    config = default_config
json.dump(config, open("./config/latest_compiled_config.json", "w"), indent=4)

c = Config()

c._private_config = config

# Autohide
for k, v in config["Window"].get("autohide", {}).get("class", {}).items():
    c.window_rule(is_wmclass=k, rule="autohide-panel")
for k, v in config["Window"].get("autohide", {}).get("title", {}).items():
    c.window_rule(is_title=k, rule="autohide-panel")
# Rename
for k, v in config["Window"].get("rename", {}).get("class", {}).items():
    c.window_rename(from_wmclass=k, to_wmclass=v)
for k, v in config["Window"].get("rename", {}).get("title", {}).items():
    c.window_rename(from_title=k, to_wmclass=v)
# Ignore
for k, v in config["Window"].get("ignore", {}).get("class", {}).items():
    if v == True:
        c.window_rule(is_wmclass=k, rule="ignore")
for k, v in config["Window"].get("ignore", {}).get("title", {}).items():
    if v == True:
        c.window_rule(is_title=k, rule="ignore")
# Dock
for k, v in config["Dock"].get("pinned", {}).items():
    c.pin_window(wmclass=k, command=v)
# Apps
for k, v in config["Window"].get("translate", {}).get("class", {}).items():
    c.window_rule(from_wmclass=k, to_title=v)

# Workspace
for k, v in config["Workspace"]["ignore"]["id"].items():
    if v == True:
        c.workspace_rule(is_id=int(k), rule="ignore")

# Shell

c.shell_rule(rule="about-window-width", value=config["Shell"]["about"].get("width", 250))
c.shell_rule(rule="about-window-height", value=config["Shell"]["about"].get("height", 355))
c.shell_rule(rule="about-window-resizable", value=config["Shell"]["about"].get("resizable", False))
c.shell_rule(rule="about-computer-label", value=config["Shell"]["about"].get("computer-label", "Env Shell"))
c.shell_rule(rule="about-computer-caption", value=config["Shell"]["about"].get("computer-caption", "ESH, 2024"))
c.shell_rule(rule="about-more-info", value=config["Shell"]["about"].get("more-info", "https://github.com/E3nviction/envshell"))

env_menu_option_labels = {}
for num, se in config["Shell"].get("env-menu", {}).get("options", {}).items():
    env_menu_option_labels[se.get("label", "")] = [se.get("on-click", ""), se.get("keybind", "")]

c.shell_rule(rule="panel-env-menu-option-settings-on-click", value=config["Shell"]["env-menu"].get("settings", {}).get("on-click", "hyprctl dispatch settings"))
c.shell_rule(rule="panel-env-menu-option-store-label", value=config["Shell"]["env-menu"].get("store", {}).get("label", "Nix Store..."))
c.shell_rule(rule="panel-env-menu-option-store-on-click", value=config["Shell"]["env-menu"].get("store", {}).get("on-click", "xdg-open https://search.nixos.org/packages"))


i = 0
for k, v in env_menu_option_labels.items():
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-label", value=k)
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-on-click", value=v[0])
    if len(v) > 1:
        c.shell_rule(rule=f"panel-env-menu-option-{i+1}-keybind", value=v[1])
    i += 1
