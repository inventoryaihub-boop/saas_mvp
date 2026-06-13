import streamlit as st

st.set_page_config(page_title="MicroSaaS BI", layout="wide")

st.title("Dashboard")
st.markdown("---")
st.write("This is your daily operational overview.")

# 1. 讀取最新版的多品項共用記憶體
forecast_item = st.session_state.get('forecast_item', None)
forecast_demand = st.session_state.get('forecast_demand', None)
forecast_safe_stock = st.session_state.get('forecast_safe_stock', None)
current_stock = 5 # 假設目前的庫存為 5
unit_cost = 40

# 2. 根據是否有選擇商品，動態計算首頁指標
if forecast_item is not None:
    restock_need = max(0, forecast_safe_stock - current_stock)
    required_capital = restock_need * unit_cost
    
    revenue_gap_value = f"${required_capital:,}"
    revenue_gap_delta = "Immediate Capital Required"
    stock_status_value = "Action Required" if restock_need > 0 else "Healthy"
    stock_status_delta = f"{restock_need} units short"
    item_label = f"{forecast_item} Status"
else:
    revenue_gap_value = "$0"
    revenue_gap_delta = "No active forecast"
    stock_status_value = "Awaiting Data"
    stock_status_delta = "Go to Forecasting module"
    item_label = "Selected SKU Status"

# 3. 畫面呈現
col1, col2, col3 = st.columns(3)

col1.metric(
    label="Required Restock Capital", 
    value=revenue_gap_value, 
    delta=revenue_gap_delta, 
    delta_color="inverse" if forecast_item else "normal"
)
col2.metric(
    label="High-Risk Dead Stock", 
    value="12 Items", 
    delta="Requires review", 
    delta_color="inverse"
)
col3.metric(
    label=item_label, 
    value=stock_status_value, 
    delta=stock_status_delta
)

st.markdown("---")
if forecast_item is not None:
    st.success(f"✅ Global Synchronization Active: Dashboard is tracking {forecast_item}.")
else:
    st.info("👈 Please select '1_AI_Forecasting' to upload data and select an SKU.")