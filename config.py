import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
PAYMENT_PROVIDER_TOKEN = os.environ.get("PAYMENT_PROVIDER_TOKEN")
OVPN_FILE_PATH = os.environ.get("OVPN_FILE_PATH")
WG_FILE_PATH = os.environ.get("WG_FILE_PATH")
QR_CODE_PATH = os.environ.get("QR_CODE_PATH")
