import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
PAYMENT_INFO = {
    "faucetpay": os.getenv("FAUCET_PAY"),
    "binance": os.getenv("BINANCE_ADDRESS")
}
