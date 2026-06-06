import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),  # Локальный хост, так как используем туннель
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
}

SSH_CONFIG = {
    "ssh_host": os.getenv("SSH_HOST"),
    "ssh_port": int(os.getenv("SSH_PORT", "22")),
    "ssh_user": os.getenv("SSH_USER"),
    "ssh_password": os.getenv("SSH_PASSWORD"),
    "remote_bind_address": (
        os.getenv("REMOTE_DB_HOST"),
        int(os.getenv("REMOTE_DB_PORT", "3306")),
    ),
}

admins = ["chinanumb2", "burzhuykaa", "fullmetalldickk"]
