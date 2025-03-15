import MetaTrader5 as mt5
import telebot
import os
import time
import random
from dotenv import load_dotenv

# 🔄 Charger les variables d’environnement
load_dotenv()

# 🎯 Connexion à MetaTrader 5
LOGIN = int(os.getenv("BYBIT_LOGIN"))
PASSWORD = os.getenv("BYBIT_PASSWORD")
SERVER = os.getenv("BYBIT_SERVER")

if not mt5.initialize():
    print("⚠️ Erreur de connexion à MT5")
    mt5.shutdown()

authorized = mt5.login(LOGIN, password=PASSWORD, server=SERVER)

if not authorized:
    print("⚠️ Impossible de se connecter au compte MT5")
    exit()

print("✅ Connexion à MT5 réussie")

# 🤖 Configuration du bot Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def envoyer_telegram(message):
    """Envoie un message sur Telegram"""
    bot.send_message(CHAT_ID, message)

# 🔥 Liste des paires disponibles sur Bybit (MT5)
PAIRS_BYBIT = ["BTCUSD", "ETHUSD", "XAUUSD", "SOLUSD", "XRPUSD", "ADAUSD"]

# 📈 Fonction pour prendre un trade intelligent
def prendre_trade():
    """Exécute un trade automatique toutes les minutes"""
    symbol = random.choice(PAIRS_BYBIT)  # Sélection aléatoire d'une paire
    volume = float(os.getenv("TRADE_LOT", 0.1))  # Volume de trade par défaut 0.1
    type_trade = random.choice(["buy", "sell"])  # Achat ou vente aléatoire

    type_dict = {"buy": mt5.ORDER_TYPE_BUY, "sell": mt5.ORDER_TYPE_SELL}

    order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type_dict[type_trade],
        "price": mt5.symbol_info_tick(symbol).ask if type_trade == "buy" else mt5.symbol_info_tick(symbol).bid,
        "deviation": 10,
        "magic": 123456,
        "comment": "Trade auto",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(order)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        message = f"✅ Trade {type_trade} exécuté sur {symbol} | Volume: {volume} | Prix: {order['price']}"
        print(message)
        envoyer_telegram(message)
    else:
        message = f"⚠️ Trade {type_trade} échoué sur {symbol} | Code: {result.retcode}"
        print(message)
        envoyer_telegram(message)

# 🔄 Boucle de scalping automatique
while True:
    prendre_trade()
    time.sleep(int(os.getenv("TRADE_INTERVAL", 60)))  # Attente définie dans .env
