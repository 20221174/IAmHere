from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4")
}

FINGERPRINT_SENSOR_PORT = os.getenv("FINGERPRINT_SENSOR_PORT")
FINGERPRINT_BAUDRATE = int(os.getenv("FINGERPRINT_BAUDRATE", "57600"))

NOTIFY_API_URL = os.getenv("NOTIFY_API_URL")

AES_KEY = os.getenv("AES_KEY", "12345678901234567890123456789012")  # 32 bytes for AES-256


