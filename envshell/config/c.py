from .conf import Config
from fabric.utils import get_relative_path, monitor_file
import tomllib
import json
import os
from loguru import logger


app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}

c = Config()

def load_config(config):
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

def write_config(config, config_to_write):
    for k, v in config.items():
        if isinstance(v, dict):
            node = config_to_write.setdefault(k, {})
            write_config(v, node)
        else:
            config_to_write[k] = v
    return config_to_write

config_location = os.path.join(os.path.expanduser("~"), ".config")
global default_config
global config
default_config = {}
config = {}
def load_default_config():
    global default_config
    global config
    with open(get_relative_path("default_config.toml"), "rb") as f:
        default_config = tomllib.load(f)
        load_config(default_config)
        config = default_config
        c._private_config = config

def load_config_file():
    global default_config
    global config
    logger.info("[Main] Applying Config")
    try:
        with open(os.path.join(config_location, "envshell", "config.toml"), "rb") as f:
            config = tomllib.load(f)
        config = write_config(config, default_config)
        with open(os.path.join(config_location, "envshell", "envctl.toml"), "rb") as f:
            config_temp = tomllib.load(f)
        config = write_config(config_temp, config)
        load_config(config)
        c._private_config = config
    except:
        logger.warning("Could not find a config file, using default")
    json.dump(config, open(get_relative_path("latest_compiled_config.json"), "w"), indent=4)

load_default_config()
load_config_file()

# check if config exists
if not os.path.exists(os.path.join(config_location, "envshell")):
    os.makedirs(os.path.join(config_location, "envshell"))

# check if config file exists
if not os.path.exists(os.path.join(config_location, "envshell", "config.toml")):
    shutil.copyfile(get_relative_path("example_config.toml"), os.path.join(config_location, "envshell", "config.toml"))

# check if temp config file exists
if not os.path.exists(os.path.join(config_location, "envshell", "envctl.toml")):
    with open(os.path.join(config_location, "envshell", "envctl.toml"), "w") as f:
        f.write("")

config_file_monitor = monitor_file(os.path.join(config_location, "envshell", "config.toml"))
config_file_monitor.connect("changed", lambda *_: load_config_file())

config_file_monitor = monitor_file(os.path.join(config_location, "envshell", "envctl.toml"))
config_file_monitor.connect("changed", lambda *_: load_config_file())