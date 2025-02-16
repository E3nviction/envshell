from .conf import Config
from fabric.utils import get_relative_path
import tomllib
import json


icon_list = []
app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}
with open("./config/default_config.json", "r") as f:
    default_config = json.load(f)
try:
    with open("./config/config.toml", "rb") as f:
        config = tomllib.load(f)
except:
    print("Failed to load config.toml, using default config")
    config = default_config
json.dump(config, open("./config/latest_compiled_config.json", "w"), indent=4)

c = Config()

class SectionMissing():
    def __init__(self, section):
        return f"{section} section is missing from config.toml, using the default config"

# Error Checking

if config.get("Window", None) is None:
    print(SectionMissing("Window"))
    config["Window"] = default_config["Window"]

if config.get("Dock", None) is None:
    print(SectionMissing("Dock"))
    config["Dock"] = default_config["Dock"]

if config.get("Shell", None) is None:
    print(SectionMissing("Shell"))
    config["Shell"] = default_config["Shell"]

if config.get("Shell").get("dock", None) is None:
    print(SectionMissing("Shell.dock"))
    config["Shell"]["dock"] = default_config["Shell"]["dock"]

if config.get("Shell").get("panel", None) is None:
    print(SectionMissing("Shell.panel"))
    config["Shell"]["panel"] = default_config["Shell"]["panel"]

if config.get("Shell").get("about", None) is None:
    print(SectionMissing("Shell.about"))
    config["Shell"]["about"] = default_config["Shell"]["about"]

if config.get("Shell").get("env-menu", None) is None:
    print(SectionMissing("Shell.env-menu"))
    config["Shell"]["env-menu"] = default_config["Shell"]["env-menu"]

if config.get("Icons", None) is None:
    print(SectionMissing("Icons"))
    config["Icons"] = default_config["Icons"]

if config.get("Bluetooth", None) is None:
    print(SectionMissing("Bluetooth"))
    config["Bluetooth"] = default_config["Bluetooth"]

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
c.shell_rule(rule="dock-width", value=config["Shell"]["dock"].get("width", 782))
c.shell_rule(rule="dock-height", value=config["Shell"]["dock"].get("height", 64))
c.shell_rule(rule="dock-position", value=config["Shell"]["dock"].get("position", "bottom center"))
c.shell_rule(rule="dock-margin", value=(
    config["Shell"]["dock"].get("margin", (0, 0, 5, 0))[0],
    config["Shell"]["dock"].get("margin", (0, 0, 5, 0))[1],
    config["Shell"]["dock"].get("margin", (0, 0, 5, 0))[2],
    config["Shell"]["dock"].get("margin", (0, 0, 5, 0))[3],
))
c.shell_rule(rule="dock-rounding", value=config["Shell"]["dock"].get("rounding", "19.2px"))
c.shell_rule(rule="dock-orientation", value=config["Shell"]["dock"].get("orientation", "horizontal"))

c.shell_rule(rule="panel-width", value=config["Shell"]["panel"].get("width", 1920))
c.shell_rule(rule="panel-height", value=config["Shell"]["panel"].get("height", 24))
c.shell_rule(rule="panel-position", value=config["Shell"]["panel"].get("position", "top left right"))
c.shell_rule(rule="panel-margin", value=(
    config["Shell"]["panel"].get("margin", (0, 0, 0, 0))[0],
    config["Shell"]["panel"].get("margin", (0, 0, 0, 0))[1],
    config["Shell"]["panel"].get("margin", (0, 0, 0, 0))[2],
    config["Shell"]["panel"].get("margin", (0, 0, 0, 0))[3],
))
c.shell_rule(rule="panel-rounding", value=config["Shell"]["panel"].get("rounding", "0"))
c.shell_rule(rule="panel-date-format", value=config["Shell"]["panel"].get("date-format", "%a %b %d %H:%M"))
c.shell_rule(rule="panel-icon", value=config["Shell"]["panel"].get("icon", ""))

c.shell_rule(rule="about-window-width", value=config["Shell"]["about"].get("width", 250))
c.shell_rule(rule="about-window-height", value=config["Shell"]["about"].get("height", 355))
c.shell_rule(rule="about-window-resizable", value=config["Shell"]["about"].get("resizable", False))
c.shell_rule(rule="about-computer-label", value=config["Shell"]["about"].get("computer-label", "Env Shell"))
c.shell_rule(rule="about-computer-caption", value=config["Shell"]["about"].get("computer-caption", "ESH, 2024"))
c.shell_rule(rule="about-more-info", value=config["Shell"]["about"].get("more-info", "https://github.com/E3nviction/envshell"))

env_menu_option_labels = {}
for num, se in config["Shell"].get("env-menu", {}).get("options", {}).items():
    env_menu_option_labels[se.get("label", "")] = [se.get("on-click", ""), se.get("keybind", "")]

i = 0
for k, v in env_menu_option_labels.items():
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-label", value=k)
    c.shell_rule(rule=f"panel-env-menu-option-{i+1}-on-click", value=v[0])
    if len(v) > 1:
        c.shell_rule(rule=f"panel-env-menu-option-{i+1}-keybind", value=v[1])
    i += 1

c.shell_rule(rule="bluetooth-show-hidden-devices", value=config["Bluetooth"].get("show-hidden-devices", False))


# Icons
icon_dir = config["Icons"].get("directory", "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/")