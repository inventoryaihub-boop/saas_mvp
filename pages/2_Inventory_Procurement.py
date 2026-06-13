import streamlit as st
import pandas as pd

st.title("Inventory & Procurement Advisory")
st.markdown("---")
st.write("Automated safety stock and replenishment lists based on active forecasts.")

# 讀取動態商品資料
forecast_item = st.session_state.get('forecast_item', 'No Item Selected')
forecast_demand = st.session_state.get('forecast_demand', 0)
forecast_safe_stock = st.session_state.get('forecast_safe_stock', 0)
current_stock = 5 

if forecast_safe_stock > 0 and current_stock < forecast_safe_stock:
    restock_amount = forecast_safe_stock - current_stock
    action_text = f"Urgent Restock ({restock_amount} units)"
elif forecast_safe_stock == 0:
    action_text = "Awaiting Forecast"
else:
    action_text = "Healthy"

# 將表格資料存成一個變數 (df_inventory)，方便後續顯示與下載
df_inventory = pd.DataFrame({
    "Item Name": ["Dress Type A", "Thermos Type B", forecast_item],
    "Current Stock": [15, 120, current_stock if forecast_item != 'No Item Selected' else 0],
    "Est. 30-Day Sales": [45, 80, forecast_demand],
    "Action Required": ["Urgent Restock (40 units)", "Healthy", action_text]
})

# 在網頁上顯示表格
st.dataframe(df_inventory, use_container_width=True)

st.markdown("---")
st.subheader("📥 Export Reports")
st.write("Download the current replenishment list to share with the procurement team or warehouse.")

# --- 核心匯出邏輯 ---
# 將 DataFrame 轉換為 CSV 格式，並加入 utf-8-sig 編碼以完美支援中文/英文內容不亂碼
csv_data = df_inventory.to_csv(index=False).encode('utf-8-sig')

# 建立下載按鈕
st.download_button(
    label="Download Replenishment List (CSV)",
    data=csv_data,
    file_name="Restock_Action_Plan.csv",
    mime="text/csv",
    type="primary"
)