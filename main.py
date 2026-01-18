import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime

from utils import (
    generate_mock_data, get_recommendation_logic, 
    generate_attribution_data, generate_iso_data,
    generate_audit_logs, generate_system_logs
)
from components import apply_theme

# --- Config ---
st.set_page_config(
    page_title="GreenTensor Enterprise",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Visual Style (Dark Mode FinOps)
apply_theme()

# Custom CSS for "Neon" look and Card styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #00FF00;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 14px;
        color: #AAAAAA;
    }
    .stSelectbox label {
        color: #00FF00 !important;
        font-weight: bold;
    }
    div[data-testid="stExpander"] details summary p {
        font-weight: bold;
        color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# --- Global Sidebar (Navigation & Grid Status) ---
with st.sidebar:
    st.title("GreenTensor ⚡")
    st.caption("Enterprise Carbon Orchestrator")
    
    st.markdown("---")
    
    # 1. User Persona
    role = st.selectbox(
        "View As", 
        ["AI Engineer", "FinOps Lead", "Compliance Officer", "Admin"]
    )
    
    st.markdown("---")

    # 2. Live Grid Status Card
    st.subheader("📡 Live Grid Status")
    
    # Region Selector (Simulates "Current Connection")
    region = st.selectbox(
        "Region", 
        ["Asia-Pacific (Mumbai)", "US-East (N. Virginia)", "Europe (Stockholm)"],
        label_visibility="collapsed"
    )
    
    # Generate Data for current region
    if 'data' not in st.session_state or st.session_state.get('region') != region:
        st.session_state['data'] = generate_mock_data(region=region)
        st.session_state['region'] = region

    df = st.session_state['data']
    current = df.iloc[0] # Current Hour
    grid_mix = current['grid_mix']
    
    # Donut Chart for Grid Mix
    # Colors: Coal=Red, Gas=Orange, Solar/Wind/Hydro=Green
    colors = {
        "Coal": "#FF4B4B", "Gas": "#FFA500", "Hydro": "#00FF00", 
        "Solar": "#FFFF00", "Wind": "#00FFFF", "Nuclear": "#0000FF"
    }
    
    labels = list(grid_mix.keys())
    values = list(grid_mix.values())
    node_colors = [colors.get(l, "#888") for l in labels]
    
    fig_mix = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=.6,
        marker=dict(colors=node_colors),
        textinfo='none'
    )])
    fig_mix.update_layout(
        showlegend=False, 
        margin=dict(t=0, b=0, l=0, r=0), 
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=f"{values[0]}%", x=0.5, y=0.5, font_size=20, showarrow=False, font_color=node_colors[0])]
    )
    st.plotly_chart(fig_mix, use_container_width=True)
    
    # Shadow Price Calculation (Mock: Carbon * Tax)
    # Tax = $50/ton => $0.05/kg. Carbon Int is g/kWh.
    # 700g/kWh = 0.7kg/kWh * $0.05 = $0.035/kWh surcharge
    shadow_surcharge = (current['carbon_intensity'] / 1000) * 50 
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Shadow Price", f"${shadow_surcharge:.2f}/ton", help="Internal Carbon Tax Rate")
    
    # Grid Mix Text
    max_source = max(grid_mix, key=grid_mix.get)
    st.caption(f"Grid Dominance: **{max_source} ({grid_mix[max_source]}%)**")
    if max_source in ["Coal", "Gas"]:
        st.warning("dirty grid detected", icon="⚠️")
    else:
        st.success("green grid active", icon="✅")

    st.markdown("---")
    
    # 3. Settings
    st.checkbox("Multi-Cloud Routing", value=True)
    st.checkbox("Auto-Demand Response", value=False)
    
# --- Main Content ---

# ==========================================
# VIEW: AI ENGINEER
# ==========================================
if role == "AI Engineer":
    st.title("Scheduler")
    st.markdown("Orchestrate high-performance workloads with carbon-aware intelligence.")
    
    # 2-Column Layout: Form vs Status
    col_form, col_vis = st.columns([1.2, 1])
    
    with col_form:
        st.markdown("#### Configure Workload")
        with st.container(border=True):
            # Step 1: Workload Select
            workload_type = st.selectbox(
                "1. Select Workload Type", 
                ["GenAI Training", "Inference Fleet", "HPC Simulation", "Enterprise ETL"]
            )
            
            # Step 2: Dynamic Inputs
            params = {}
            st.markdown("**2. Job Parameters**")
            
            if workload_type == "GenAI Training":
                c1, c2 = st.columns(2)
                params["GPU Type"] = c1.selectbox("Hardware", ["H100 NVL", "A100 80GB", "TPU v5"])
                params["Hours"] = c2.number_input("Est. Duration (hrs)", value=24)
                
            elif workload_type == "Inference Fleet":
                c1, c2 = st.columns(2)
                params["RPS"] = c1.number_input("Req Per Second", value=5000)
                params["Latency SLA"] = c2.selectbox("Max Latency", ["20ms (Strict)", "100ms (Loose)"])
                
            elif workload_type == "Enterprise ETL":
                c1, c2 = st.columns(2)
                params["Volume"] = c1.text_input("Data Volume", "50 TB")
                params["Deadline"] = c2.time_input("Delivery Deadline", value=None)
                
            else: # HPC
                params["Urgency"] = st.slider("Urgency Level", 1, 10, 5)
            
            st.divider()
            
            # Step 3: Recommendation Engine
            rec_text = get_recommendation_logic(workload_type, params)
            st.info(rec_text)
            
            # Action Button
            if st.button("Schedule Optimization ⚡", type="primary", use_container_width=True):
                st.balloons()
                time.sleep(1)
                st.toast("Workload dispatched to scheduler!", icon="🚀")
                st.success("Optimization Complete: Job scheduled for execution.")

    with col_vis:
        st.markdown("#### Carbon Forecast (24h)")
        
        # Prepare Data
        # Extract Solar % from grid_mix dict
        solar_gen = df['grid_mix'].apply(lambda x: x.get('Solar', 0))
        
        # Line Chart of Carbon
        fig = go.Figure()
        
        # Trace 1: Carbon Intensity (Primary Y)
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['carbon_intensity'],
            mode='lines', name='Carbon',
            line=dict(color='#00FF00' if current['carbon_intensity'] < 400 else '#FF4B4B', width=3),
            fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.1)'
        ))
        
        # Trace 2: Solar Generation (Secondary Y)
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=solar_gen,
            mode='lines', name='Solar (Secondary)',
            fill='tozeroy', line=dict(color='#FFD700', width=0),
            yaxis='y2', opacity=0.2
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis_title="Time", 
            yaxis_title="Carbon (gCO2/kWh)",
            yaxis2=dict(
                overlaying='y', 
                side='right', 
                showgrid=False, 
                range=[0, 100],
                title="Solar %"
            ),
            showlegend=True,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Mini Stats
        m1, m2 = st.columns(2)
        m1.metric("Current Load", "82%", "+12%")
        m2.metric("Est. Cost/Hr", "$42.50", "-$3.20")

# ==========================================
# VIEW: FINOPS LEAD
# ==========================================
elif role == "FinOps Lead":
    st.title("Financial Intelligence")
    st.markdown("Shadow pricing and carbon-adjusted cost analysis.")
    
    # Shadow Pricing Engine
    st.subheader("Shadow Pricing Engine")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Real Cloud Bill", "$142,000", delta="+2% MoM", delta_color="inverse")
    col2.metric("Carbon-Adjusted Spend", "$158,400", delta="+$16,400 Tax", delta_color="off")
    col3.metric("Carbon Credits Saved", "$12,500", delta="350 Tons")
    
    st.divider()
    
    # Attribution Table
    st.subheader("Team Efficiency Scorecard")
    st.info("Teams with a **Net Efficiency Score < 50** are penalized by the internal carbon tax.")
    
    attr_df = generate_attribution_data()
    
    # Formatting for better visuals
    st.dataframe(
        attr_df.style.background_gradient(subset=["Net Efficiency Score"], cmap="RdYlGn"),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Cost Trend
    st.subheader("Cost vs Carbon Trend")
    # Mock trend data
    trend_data = pd.DataFrame({
        "Day": [f"Day {i}" for i in range(1, 15)],
        "Cost ($)": [1000 + i*50 + (i%3)*100 for i in range(14)],
        "Carbon (kg)": [800 - i*20 for i in range(14)]
    })
    
    fig_trend = px.line(trend_data, x="Day", y=["Cost ($)", "Carbon (kg)"], markers=True, 
                        color_discrete_sequence=["#00FF00", "#FF4B4B"])
    fig_trend.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# VIEW: COMPLIANCE OFFICER
# ==========================================
elif role == "Compliance Officer":
    st.title("Regulatory & Compliance")
    st.markdown("ISO 14064 Reporting & EU AI Act Audit Trails.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Scope 2 Emissions vs Net Zero Target")
        iso_data = generate_iso_data()
        
        fig_iso = go.Figure()
        fig_iso.add_trace(go.Bar(
            x=iso_data["Month"], y=iso_data["Scope 2 Real"], 
            name="Actual Emissions", marker_color="#FF4B4B"
        ))
        fig_iso.add_trace(go.Scatter(
            x=iso_data["Month"], y=iso_data["Net Zero Target"], 
            name="Net Zero Path", mode='lines+markers', line=dict(color='#00FF00', width=2, dash='dash')
        ))
        fig_iso.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
        st.plotly_chart(fig_iso, use_container_width=True)
        
    with col2:
        st.subheader("Audit Artifacts")
        st.markdown("Generate signed reports for external auditors.")
        
        with st.container(border=True):
            st.markdown("📄 **ISO 14064 Report (Q1)**")
            if st.button("Generate PDF", key="iso_btn"):
                with st.spinner("Compiling global registry data..."):
                    time.sleep(2)
                st.success("Download Ready: ISO_14064_Q1_Signed.pdf")
                
        with st.container(border=True):
            st.markdown("🇪🇺 **EU AI Act Declaration**")
            if st.button("Generate XML", key="eu_btn"):
                 with st.spinner("Validating energy ratings..."):
                    time.sleep(1.5)
                 st.success("Download Ready: EU_AI_Act_Decl.xml")

# ==========================================
# VIEW: ADMIN
# ==========================================
elif role == "Admin":
    st.title("🛡️ System Administration")
    
    # Logs
    logs = generate_audit_logs()
    st.subheader("Security Audit Logs")
    st.dataframe(logs, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("Live System Shell")
    st.code(generate_system_logs(), language="bash")
