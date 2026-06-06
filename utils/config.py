import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    SERVER_ID = int(os.getenv("SERVER_ID", 0))
    PANEL_CHANNEL_ID = int(os.getenv("PANEL_CHANNEL_ID", 0))
    ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", 0))
    
    # Database
    DB_PATH = os.getenv("DB_PATH", "./data/panel.db")
    
    # Project
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Irish Lagger")
    PROJECT_PREFIX = os.getenv("PROJECT_PREFIX", "/")
    
    # Colors
    COLOR_SUCCESS = 0x00FF00
    COLOR_ERROR = 0xFF0000
    COLOR_INFO = 0x0000FF
    COLOR_WARNING = 0xFFFF00
