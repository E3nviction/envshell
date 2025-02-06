import sys
from hyprpy import Hyprland
from utils.services import EnvShellService

global instance
try:
    instance = Hyprland()
except Exception as e:
    print("Failed to connect to Hyprland:", e)
    sys.exit(1)

global envshell_service
try:
    envshell_service = EnvShellService()
except Exception as e:
    print("Failed to create EnvShellService:", e)
    sys.exit(1)

def main():
    return instance, envshell_service