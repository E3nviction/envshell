import sys
from hyprpy import Hyprland
from fabric.notifications import Notifications
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

global notification_service
try:
    notification_service = Notifications()
except Exception as e:
    print("Failed to create NotificationService:", e)
    sys.exit(1)

def main():
    return instance, envshell_service

def create_instance():
    try:
        _instance = Hyprland()
    except Exception as e:
        print("Failed to connect to Hyprland:", e)
        sys.exit(1)

    return _instance
