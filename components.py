import streamlit as st

def apply_theme():
    """
    Applies custom CSS for the GreenTensor Neon/Dark aesthetic.
    """
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #050505;
            color: #E0E0E0;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0A0A0A;
            border-right: 1px solid #333;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #00FF00 !important;
            font-family: 'Courier New', Courier, monospace; /* Techy font */
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #00FF00;
            font-size: 24px;
            text-shadow: 0 0 5px #00FF00;
        }
        
        [data-testid="stMetricLabel"] {
            color: #AAAAAA;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #111;
            color: #00FF00;
            border: 1px solid #00FF00;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #00FF00;
            color: #000;
            box-shadow: 0 0 10px #00FF00;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #111;
            border-radius: 5px;
            color: #FFF;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00FF00 !important;
            color: #000 !important;
            font-weight: bold;
        }
        
        /* Success Box */
        .element-container .stAlert {
            background-color: #002200;
            color: #00FF00;
            border: 1px solid #00FF00;
        }
        
        </style>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, color="green"):
    """
    Custom wrapper for metrics if needed, but standard st.metric is often enough.
    We just style standard metrics via CSS above.
    """
    st.metric(label=label, value=value, delta=delta)
