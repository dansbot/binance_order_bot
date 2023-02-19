from binance.client import Client
import os


def get_client():
    if os.environ.get("TRAINING"):
        import spoof_binance

        return spoof_binance.Client()
    return Client(
        api_key=os.environ.get("BINANCE_API_KEY"),
        api_secret=os.environ.get("BINANCE_API_SECRET"),
    )
