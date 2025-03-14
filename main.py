import MetaTrader5 as mt5
import telebot
import os
import time
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

# 📌 Connexion à MetaTrader 5
ACCOUNT = int(os.getenv("MT5_ACCOUNT"))
PASSWORD = os.getenv("MT5_PASSWORD")
SERVER = os.getenv("MT5_SERVER")

if not mt5.initialize():
    print("⚠️ Erreur de connexion à MT5")
    mt5.shutdown()

authorized = mt5.login(ACCOUNT, password=PASSWORD, server=SERVER)

if not authorized:
    print("⚠️ Impossible de se connecter au compte MT5")
    exit()

print("✅ Connexion à MT5 réussie")

# 📌 Configuration de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def envoyer_telegram(message):
    bot.send_message(CHAT_ID, message)

# 📌 Fonction pour prendre un trade
def prendre_trade(symbol, volume, type_trade):
    """Exécute un trade sur MT5"""
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
        print(f"✅ Trade {type_trade} sur {symbol} exécuté !")
        envoyer_telegram(f"✅ Trade {type_trade} sur {symbol} exécuté !")
    else:
        print(f"⚠️ Échec du trade {type_trade} sur {symbol} - Code: {result.retcode}")
        envoyer_telegram(f"⚠️ Échec du trade {type_trade} sur {symbol} - Code: {result.retcode}")

# 📌 Boucle de scalping automatique toutes les minutes
while True:
    prendre_trade("XAUUSD", 0.01, "buy")  # Exemple : Achat d’or (XAUUSD)
    time.sleep(60)  # Attente de 1 minute avant le prochain trade
