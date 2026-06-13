import streamlit as st
import pandas as pd

st.title("Financial & Cash Flow Planning")
st.markdown("---")
st.write("Translating inventory movements into financial metrics.")

forecast_item = st.session_state.get('forecast_item', 'No Item Selected')
forecast_demand = st.session_state.get('forecast_demand', 0)
forecast_safe_stock = st.session_state.get('forecast_safe_stock', 0)
current_stock = 5 

unit_cost = 40
unit_price = 120

projected_revenue = forecast_demand * unit_price
restock_need = max(0, forecast_safe_stock - current_stock)
required_capital = restock_need * unit_cost

col1, col2, col3 = st.columns(3)
col1.metric(f"Est. 30-Day Revenue ({forecast_item})", f"${projected_revenue:,}")
col2.metric("Required Restock Capital", f"${required_capital:,}", delta="Immediate Cash Need", delta_color="inverse")
col3.metric("Projected Gross Margin", f"{((unit_price - unit_cost) / unit_price) * 100:.1f}%")

st.markdown("---")
st.subheader("Cash Flow Risk Analysis")

st.dataframe(pd.DataFrame({
    "Item Name": ["Dress Type A", "Thermos Type B", forecast_item],
    "Unit Cost": ["$25", "$15", f"${unit_cost}"],
    "Restock Quantity": [40, 0, restock_need if forecast_item != 'No Item Selected' else 0],
    "Capital Required": ["$1,000", "$0", f"${required_capital:,}"]
}), use_container_width=True)

if required_capital > 0:
    st.warning(f"Action Required: Ensure you have at least ${required_capital:,} to cover {forecast_item} restocking costs.")
elif forecast_item != 'No Item Selected':
    st.success("Cash flow is healthy. No immediate restocking capital required.")