import requests
import json
import time
from datetime import datetime
import telebot
import os

# Cấu hình bot Telegram
TELEGRAM_BOT_TOKEN = '7259275113:AAFU7GY_hrottGU9lwlf1nGUSwHszg9Te84'
CHAT_ID = '990393276'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Hàm lấy dữ liệu từ CoinGecko
def get_market_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    data = response.json()
    if "data" in data and "market_cap_percentage" in data["data"]:
        return {
            "timestamp": datetime.utcnow(),
            "btc_d": data["data"]["market_cap_percentage"].get("btc", None),
            "usdt_d": data["data"]["market_cap_percentage"].get("usdt", None)
        }
    return None

# Hàm lưu dữ liệu vào file JSON
def save_to_json(filename, data):
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_path, filename)
    
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, default=str)
    except IOError:
        print(f"Lỗi khi ghi file {filepath}")

# Hàm tải dữ liệu từ file JSON
def load_from_json(filename):
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_path, filename)
    
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def analyze_market(btc_d, prev_btc_d, usdt_d, prev_usdt_d):
    if btc_d is None or usdt_d is None or prev_btc_d is None or prev_usdt_d is None:
        return None
    
    btc_trend = "🔼 Tăng" if btc_d > prev_btc_d else "🔽 Giảm"
    usdt_trend = "🔼 Tăng" if usdt_d > prev_usdt_d else "🔽 Giảm"
    
    if btc_trend == "🔼 Tăng" and usdt_trend == "🔼 Tăng":
        return "🚨 Bán tháo mạnh! Nhà đầu tư rút vốn vào BTC và stablecoin. Thị trường đang trong giai đoạn hoảng loạn."
    elif btc_trend == "🔼 Tăng" and usdt_trend == "🔽 Giảm":
        return "⚠️ Tiền chảy vào BTC, altcoins có thể suy yếu. Có thể là dấu hiệu bắt đầu downtrend."
    elif btc_trend == "🔽 Giảm" and usdt_trend == "🔼 Tăng":
        return "❓ Nhà đầu tư rời bỏ altcoins nhưng chưa chuyển ngay vào BTC, có thể là giai đoạn chưa rõ xu hướng."
    elif btc_trend == "🔽 Giảm" and usdt_trend == "🔽 Giảm":
        return "🚀 Tiền chảy vào altcoins, dấu hiệu thị trường lạc quan. Có thể là altseason."
    return None

def send_telegram_message(message):
    bot.send_message(CHAT_ID, message)

def main():
    while True:
        market_data = get_market_dominance()
        if market_data:
            existing_data = load_from_json("market.json")
            existing_data.append(market_data)
            save_to_json("market.json", existing_data)
            
            if len(existing_data) > 1:
                latest_data = existing_data[-1]
                prev_data = existing_data[-2]
                
                analysis_result = analyze_market(
                    latest_data["btc_d"], prev_data["btc_d"], latest_data["usdt_d"], prev_data["usdt_d"])
                
                if analysis_result:
                    send_telegram_message(f"📊 Đánh giá thị trường: {analysis_result}")
        
        time.sleep(15*60)  # Chạy mỗi 15 phút

if __name__ == "__main__":
    main()
