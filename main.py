import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

from utils import generate_mock_data, find_optimal_window
from components import apply_theme

# --- Config ---
st.set_page_config(
    page_title="GreenTensor Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Visual Style
apply_theme()

# --- Sidebar ---
with st.sidebar:
    st.title("Settings")
    
    # Region Selector
    region = st.selectbox(
        "Region",
        ["India-West", "India-North", "US-East"]
    )
    
    # Map Region to Seed
    region_seeds = {
        "India-West": 42,
        "India-North": 101,
        "US-East": 999
    }
    selected_seed = region_seeds[region]
    
    st.divider()
    
    # Connection Status
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 10px; height: 10px; background-color: #00FF00; border-radius: 50%; box-shadow: 0 0 5px #00FF00;"></div>
            <span style="font-size: 0.9rem; color: #E0E0E0;">Connection Status: <b>Online</b></span>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- Title ---
st.title("⚡ GreenTensor")  
st.markdown("_Schedule your training jobs when the grid is clean and cheap._")

# --- Data Loading ---
# Check if data needs to be regenerated (if not present or if parameters changed)
if 'data' not in st.session_state or 'region' not in st.session_state or st.session_state['region'] != region:
    st.session_state['data'] = generate_mock_data(seed=selected_seed)
    st.session_state['region'] = region

df = st.session_state['data']
now_idx = 0
current_data = df.iloc[now_idx]

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Grid Forecast", "Smart Scheduler", "Compliance"])

# ==========================================
# TAB 1: GRID FORECAST
# ==========================================
with tab1:
    # Metrics Review
    # Logic: Status Green if Carbon < 400
    is_green = current_data['carbon_intensity'] < 400
    status = "GREEN" if is_green else "DIRTY"
    status_color = "normal" if is_green else "off" # standard metric delta colors are inverse sometimes
    
    # Calculate next green window
    # Search forward from now until carbon < 400
    future_green = df[(df.index > now_idx) & (df['carbon_intensity'] < 400)]
    if not future_green.empty:
        next_green_time = future_green.iloc[0]['timestamp']
        delta_hours = (next_green_time - current_data['timestamp']).total_seconds() / 3600
        time_label = f"In {int(delta_hours)}h ({next_green_time.strftime('%H:%M')})"
    else:
        time_label = "No window soon"

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Grid Status", status, delta="GO" if is_green else "STOP", delta_color=status_color)
    col2.metric("Current Price", f"₹{current_data['price']}/kWh", delta=f"{current_data['carbon_intensity']} gCO2", delta_color="inverse")
    col3.metric("Next Green Window", time_label)

    # Main Chart
    st.subheader("Carbon Intensity Forecast (48h)")
    
    # Plotly Chart
    fig = go.Figure()

    # Carbon Line (Primary Axis)
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['carbon_intensity'],
        mode='lines',
        name='Carbon Intensity',
        line=dict(color='#00FF00' if is_green else '#FF4B4B', width=3)
    ))

    # Solar Line (Secondary Axis)
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['solar_generation'],
        mode='lines',
        name='Solar Generation %',
        fill='tozeroy',
        line=dict(color='#FFD700', width=2), # Yellow
        yaxis='y2',
        opacity=0.4
    ))

    # Green Zone (Under 400) - Primary Axis
    fig.add_hrect(
        y0=0, y1=400,
        fillcolor="rgba(0, 255, 0, 0.1)",
        layer="below",
        line_width=0,
    )
    
    # Update layout for Dark Mode and Dual Axis
    # Update layout for Dark Mode and Dual Axis
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(title="Time"),
        yaxis=dict(
            title=dict(text="Carbon Intensity (gCO2/kWh)", font=dict(color="#E0E0E0")),
            tickfont=dict(color="#E0E0E0")
        ),
        yaxis2=dict(
            title=dict(text="Solar Generation %", font=dict(color="#FFD700")),
            tickfont=dict(color="#FFD700"),
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        legend=dict(x=0, y=1.1, orientation="h"),
        height=400
    )
    
    st.plotly_chart(fig)


# ==========================================
# TAB 2: SMART SCHEDULER
# ==========================================
with tab2:
    st.subheader("Schedule Training Job")
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        with st.form("job_form"):
            model_name = st.text_input("Model Name", value="LLaMA-7B-FineTune")
            gpu_count = st.slider("GPU Count (A100s)", 1, 100, 8)
            duration = st.slider("Est. Duration (Hours)", 1, 24, 4)
            
            submitted = st.form_submit_button("Optimize Schedule 🚀")
    
    with c2:
        if submitted:
            # Calculation
            # 1. Start Now
            now_window = df.iloc[0:duration]
            avg_carbon_now = now_window['carbon_intensity'].mean()
            avg_price_now = now_window['price'].mean()
            total_cost_now = avg_price_now * duration * gpu_count * 0.5 # Assume 0.5 kWh per GPU per hour for rough math? Or just base price cost.
            # Let's say Price is per GPU-hour for simplicity or Energy Price * Power.
            # Assume 1 GPU uses 0.4 kW.
            power_kw = gpu_count * 0.4
            energy_kwh = power_kw * duration
            cost_now = avg_price_now * energy_kwh
            
            # 2. Smart Start
            opt = find_optimal_window(df, duration)
            if opt:
                cost_smart = opt['avg_price'] * energy_kwh
                savings = cost_now - cost_smart
                carbon_saved = (avg_carbon_now - opt['avg_carbon']) * energy_kwh
                
                # Display results
                st.success(f"Optimization Complete! Recommendation: Wait until {opt['start_time'].strftime('%H:%M')}")
                
                 # Tree Equivalent Calculation (25kg CO2 approx 1 Tree)
                carbon_kg = carbon_saved / 1000
                trees_planted = carbon_kg / 25

                m1, m2, m3 = st.columns(3)
                m1.metric("Financial Savings", f"₹{int(savings)}", delta=f"-{int((savings/cost_now)*100)}%")
                m2.metric("Carbon Avoided", f"{int(carbon_saved)} gCO2", delta="Green")
                m3.metric("Start Time", opt['start_time'].strftime('%A %H:%M'))
                
                if savings > 0:
                    st.balloons()
                    st.markdown(f"### 🎉 Congratulations! You saved {carbon_kg:.2f} kg CO2 = **{trees_planted:.1f} Trees** 🌳")
            else:
                st.warning("Could not find a better window within 48h.")
        else:
            st.info("Configure your job parameters and click Optimize.")

# ==========================================
# TAB 3: COMPLIANCE
# ==========================================
with tab3:
    st.subheader("EU AI Act Compliance Tracker")
    
    # Mock Past Jobs
    past_jobs = pd.DataFrame({
        "Job ID": ["JOB-1023", "JOB-1024", "JOB-1025"],
        "Model": ["GPT-NeoX", "ResNet-50", "BERT-Large"],
        "Status": ["Completed", "Completed", "Failed"],
        "Carbon Intensity": ["320 g/kWh (Green)", "450 g/kWh", "310 g/kWh"],
        "Cost Savings": ["₹2,400", "₹0", "₹1,200"]
    })
    
    st.table(past_jobs)
    
    st.write("---")
    st.write("Generate your emissions report for regulatory compliance.")
    
    if st.button("Download EU AI Act Certificate"):
        with st.spinner("Verifying blockchain carbon credits..."):
            time.sleep(2)
        st.success("Certificate Generated Successfully! (Mock Download)")
        st.toast("Certificate downloaded to local drive.")
