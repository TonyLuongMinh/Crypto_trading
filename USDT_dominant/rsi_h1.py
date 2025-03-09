import streamlit as st
import pandas as pd
import requests
import time
import json
import plotly.express as px
from datetime import datetime
import threading

# Hàm lấy USDT Dominance từ CoinGecko
def get_usdt_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    data = response.json()
    if "data" in data and "market_cap_percentage" in data["data"]:
        return {"timestamp": datetime.utcnow(), "usdt_d": data["data"]["market_cap_percentage"].get("usdt", None)}
    return None

# Hàm lưu dữ liệu vào file JSON
def save_to_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, default=str)

# Hàm tải dữ liệu từ file JSON
def load_from_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Hàm cập nhật dữ liệu mỗi 60 giây
def update_data():
    while True:
        usdt_data = get_usdt_dominance()
        
        if usdt_data:
            existing_usdt_data = load_from_json("usdt.json")
            existing_usdt_data.append(usdt_data)
            save_to_json("usdt.json", existing_usdt_data)
        
        time.sleep(60)

def main():
    # Chạy luồng cập nhật dữ liệu
    data_thread = threading.Thread(target=update_data, daemon=True)
    data_thread.start()
    
    # Giao diện Streamlit
    st.title("USDT Dominance Tracker")
    
    if "data" not in st.session_state:
        st.session_state["data"] = load_from_json("usdt.json")
    
    chart_placeholder = st.empty()
    
    # Cập nhật dữ liệu và vẽ đồ thị
    while True:
        st.session_state["data"] = load_from_json("usdt.json")
        
        if st.session_state["data"]:
            df_usdt = pd.DataFrame(st.session_state["data"])
            df_usdt["timestamp"] = pd.to_datetime(df_usdt["timestamp"])
            fig_usdt = px.line(df_usdt, x="timestamp", y="usdt_d", title="USDT Dominance")
            chart_placeholder.plotly_chart(fig_usdt, use_container_width=True)
        
        time.sleep(10)
        st.rerun()


if __name__ == "__main__":
    main()
