import sys
import os
from hyprpy import Hyprland
from fabric.audio import Audio
from fabric.notifications import Notifications
from utils.services import EnvShellService
from loguru import logger


global envshell_service
try:
    envshell_service = EnvShellService()
except Exception as e:
    logger.error("[Main] Failed to create EnvShellService:", e)
    sys.exit(1)

#global notification_service
#try:
#    notification_service = Notifications()
#except Exception as e:
#    logger.error("[Main] Failed to create NotificationService:", e)
#    sys.exit(1)

global audio_service
try:
    audio_service = Audio()
except Exception as e:
    logger.error("[Main] Failed to create AudioService:", e)
    sys.exit(1)