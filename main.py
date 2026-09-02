import yfinance as yf
import pandas as pd
import requests
import os

# Exemples d'actions PEA (Le suffixe .PA indique la Bourse de Paris)
tickers = [
    # Actions
    "AI.PA",    # Air Liquide
    "BNP.PA",   # BNP Paribas
    "TTE.PA",   # TotalEnergies
    "CS.PA",    # AXA
    "MC.PA",    # LVMH 
    "SAN.PA",   # Sanofi 
    "WAVE.PA",  # Wavestone 
    
    # ETFs
    "C40.PA",   # Amundi CAC 40 UCITS ETF
    "CW8.PA",   # Amundi MSCI World UCITS ETF PEA
    "MSE.PA",   # Amundi Euro Stoxx 50 UCITS ETF
    "MEUD.PA"   # Amundi Stoxx Europe 600 UCITS ETF
]

def send_telegram_alert(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)

def check_buy_signals():
    alertes = []
    for ticker in tickers:
        try:
            # Télécharger l'historique sur 1 an
            data = yf.download(ticker, period="1y", interval="1d", progress=False)
            if data.empty or len(data) < 200:
                continue

            # Calcul des Moyennes Mobiles
            # 'Close' représente le prix de clôture
            data['MM50'] = data['Close'].rolling(window=50).mean()
            data['MM200'] = data['Close'].rolling(window=200).mean()

            # Analyser les deux derniers jours de cotation
            yesterday = data.iloc[-2]
            today = data.iloc[-1]

            # Détection du Golden Cross : la MM50 passe au-dessus de la MM200
            if yesterday['MM50'] <= yesterday['MM200'] and today['MM50'] > today['MM200']:
                alertes.append(f"Signal d'achat (Golden Cross) détecté sur {ticker}")

        except Exception as e:
            print(f"Erreur technique sur {ticker}: {e}")

    # Envoi des alertes
    if alertes:
        message = "\n".join(alertes)
        print(message)
        send_telegram_alert(message)
    else:
        print("Aucun signal détecté aujourd'hui.")
        

if __name__ == "__main__":
    check_buy_signals()
