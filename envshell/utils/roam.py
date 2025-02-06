import sys

from hyprpy import Hyprland

global instance
try:
    instance = Hyprland()
except Exception as e:
    print("Failed to connect to Hyprland:", e)
    sys.exit(1)