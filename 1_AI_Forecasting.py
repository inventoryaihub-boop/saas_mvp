import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.title("AI Sales & Inventory Forecasting")
st.markdown("---")
st.write("Upload multi-item sales data and select a specific SKU to forecast.")

df_ready = None

tab_std, tab_shopee, tab_manual = st.tabs(["Standard Format", "Shopee Export", "Manual Entry"])

# --- 路徑 1：標準 Excel (新增 Item_Name 欄位支援) ---
with tab_std:
    st.write("Upload an Excel file with 3 columns: 'Date', 'Item_Name', and 'Daily_Sales'.")
    file_std = st.file_uploader("Upload Standard Excel", type=['xlsx', 'xls'], key="std")
    if file_std is not None:
        try:
            df_temp = pd.read_excel(file_std)
            if len(df_temp.columns) >= 3:
                df_temp = df_temp.iloc[:, :3]
                df_temp.columns = ['Date', 'Item_Name', 'Daily_Sales']
                df_temp['Date'] = pd.to_datetime(df_temp['Date'])
                df_ready = df_temp
                st.success("Standard multi-item file loaded successfully!")
            else:
                st.error("Error: The file must have at least 3 columns (Date, Item_Name, Sales).")
        except Exception as e:
            st.error(f"Failed to read file. Error: {e}")

# --- 路徑 2：蝦皮制式報表 (抓取商品名稱) ---
with tab_shopee:
    st.write("Upload the raw 'Order Export' Excel file from Shopee.")
    file_shopee = st.file_uploader("Upload Shopee Excel", type=['xlsx', 'xls'], key="shopee")
    if file_shopee is not None:
        try:
            df_raw = pd.read_excel(file_shopee)
            if '訂單成立時間' in df_raw.columns and '數量' in df_raw.columns and '商品名稱' in df_raw.columns:
                df_temp = df_raw[['訂單成立時間', '商品名稱', '數量']].copy()
                df_temp.columns = ['Date', 'Item_Name', 'Daily_Sales']
                df_temp['Date'] = pd.to_datetime(df_temp['Date']).dt.date
                df_temp = df_temp.groupby(['Date', 'Item_Name'])['Daily_Sales'].sum().reset_index()
                df_temp['Date'] = pd.to_datetime(df_temp['Date'])
                df_ready = df_temp
                st.success("Shopee multi-item export parsed successfully!")
            else:
                st.error("Format mismatch: Missing required Shopee columns ('訂單成立時間', '商品名稱', '數量').")
        except Exception as e:
            st.error(f"Failed to process file. Error: {e}")

# --- 路徑 3：手動輸入 (模擬真實品牌環境) ---
with tab_manual:
    st.write("Generate mock data to test the multi-SKU switching feature.")
    if st.button("Generate Portfolio Mock Data"):
        dates = pd.date_range(start='2023-01-01', periods=365)
        
        # 建立三個不同商品的模擬資料，呈現不同銷售特性
        df_puma = pd.DataFrame({
            'Date': dates, 
            'Item_Name': 'Puma RS-X', 
            'Daily_Sales': np.maximum(0, 50 + 20 * np.sin(np.arange(365) * (2 * np.pi / 30)) + np.random.normal(0, 10, 365)).astype(int)
        })
        df_converse = pd.DataFrame({
            'Date': dates, 
            'Item_Name': 'Converse Chuck 70', 
            'Daily_Sales': np.maximum(0, 100 + 10 * np.sin(np.arange(365) * (2 * np.pi / 60)) + np.random.normal(0, 5, 365)).astype(int)
        })
        df_reebok = pd.DataFrame({
            'Date': dates, 
            'Item_Name': 'Reebok Club C', 
            'Daily_Sales': np.maximum(0, 30 + 40 * np.sin(np.arange(365) * (2 * np.pi / 15)) + np.random.normal(0, 15, 365)).astype(int)
        })
        
        df_ready = pd.concat([df_puma, df_converse, df_reebok], ignore_index=True)
        st.success("Mock data for multiple brands generated successfully!")

st.markdown("---")

# ==========================================
# 核心功能：多品項選擇與獨立預測
# ==========================================
if df_ready is not None:
    st.session_state['data'] = df_ready

if 'data' in st.session_state:
    df_all = st.session_state['data']
    
    # 取出所有不重複的商品名稱，建立下拉選單
    item_list = df_all['Item_Name'].unique().tolist()
    
    st.subheader("Select SKU to Analyze")
    selected_item = st.selectbox("Choose a product from your dataset:", item_list)
    
    # 根據下拉選單的選擇，過濾出該商品的專屬資料
    df_selected = df_all[df_all['Item_Name'] == selected_item].copy()
    df_selected = df_selected.sort_values('Date')
    
    # 顯示所選商品的歷史走勢
    fig = px.line(df_selected, x='Date', y='Daily_Sales', title=f"Historical Sales Trend: {selected_item}")
    fig.update_traces(line_color='#38bdf8')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader(f"Deep Learning Forecast: {selected_item}")
    
    if st.button("Launch AI Deep Forecast", key=f"btn_{selected_item}", type="primary"):
        with st.spinner(f"AI Engine calculating trends for {selected_item}..."):
            
            last_date = df_selected['Date'].max()
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)
            
            tail_days = min(30, len(df_selected))
            base_trend = df_selected['Daily_Sales'].tail(tail_days).mean()
            
            future_sales = base_trend + 15 * np.sin(np.arange(30) * (2 * np.pi / 7)) + np.random.normal(0, 5, 30)
            future_sales = np.maximum(future_sales, 0) 
            
            df_future = pd.DataFrame({'Date': future_dates, 'Daily_Sales': future_sales.astype(int)})
            
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(
                x=df_selected['Date'].tail(90), y=df_selected['Daily_Sales'].tail(90),
                mode='lines', name='Historical', line=dict(color='#94a3b8')
            ))
            fig_forecast.add_trace(go.Scatter(
                x=df_future['Date'], y=df_future['Daily_Sales'],
                mode='lines', name='AI Forecast (Next 30 Days)', line=dict(color='#2dd4bf', dash='dash')
            ))
            
            fig_forecast.update_layout(title=f"30-Day Demand Forecast: {selected_item}", xaxis_title="Date", yaxis_title="Daily Sales Unit")
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            total_pred = int(df_future['Daily_Sales'].sum())
            safe_stock = int(total_pred * 1.2) 
            
            st.success("Forecast Complete!")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Est. 30-Day Total Demand", f"{total_pred} units")
            col_b.metric("Suggested Safety Buffer", "20% (Market standard)")
            col_c.metric("Recommended Target Stock", f"{safe_stock} units", delta="Action Required", delta_color="inverse")

            # 寫入系統共用記憶體時，將商品名稱也一起存進去
            st.session_state['forecast_item'] = selected_item
            st.session_state['forecast_demand'] = total_pred
            st.session_state['forecast_safe_stock'] = safe_stock