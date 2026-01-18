import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Regional profiles: (Base Carbon, Amplitude, Solar Potential)
REGION_PROFILES = {
    "Asia-Pacific (Mumbai)": {"base": 700, "amp": 150, "solar": 1.0, "currency": "₹", "mix_bias": "Coal"},
    "US-East (N. Virginia)": {"base": 400, "amp": 100, "solar": 0.5, "currency": "$", "mix_bias": "Gas"},
    "Europe (Stockholm)": {"base": 40, "amp": 20, "solar": 0.2, "currency": "€", "mix_bias": "Hydro"},
}

def get_regional_profile(region_name):
    return REGION_PROFILES.get(region_name, REGION_PROFILES["Asia-Pacific (Mumbai)"])

def generate_mock_data(region="Asia-Pacific (Mumbai)", seed=None):
    """
    Generates mock data for Carbon Intensity, Price, and Grid Mix for 24h.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
        
    profile = get_regional_profile(region)
    base_carbon = profile["base"]
    
    # 24 Hour Snapshot
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hours = 24
    
    timestamps = [now + timedelta(hours=i) for i in range(hours)]
    
    carbon_values = []
    prices = []
    grid_mixes = []
    
    for i in range(hours):
        dt = timestamps[i]
        h = dt.hour
        
        # Carbon Sine Wave
        wave = np.sin(2 * np.pi * (h - 13) / 24)
        noise = np.random.normal(0, 20)
        
        val = base_carbon + (profile["amp"] * wave) + noise
        val = max(10, val)
        carbon_values.append(int(val))
        
        # Price
        price = (val / 100) + 2 + np.random.normal(0, 0.5)
        prices.append(round(max(0.5, price), 2))
        
        # Grid Mix Generation (Simplistic)
        # If High Carbon -> High Coal/Gas
        # If Low Carbon -> High Solar/Hydro/Wind
        
        if profile["mix_bias"] == "Coal":
            # Coal dominant
            coal = min(90, max(40, (val / 900) * 100))
            solar = 0
            if 6 <= h <= 18:
                solar = max(0, 30 * np.sin((h-6)*np.pi/12))
            
            # Normalize remainder
            rem = 100 - coal - solar
            wind = rem * 0.3
            gas = rem * 0.7
            
            grid_mix = {"Coal": int(coal), "Solar": int(solar), "Gas": int(gas), "Wind": int(wind)}
            
        elif profile["mix_bias"] == "Hydro":
            hydro = 70 + np.random.randint(-5, 5)
            wind = 20 + np.random.randint(-5, 5)
            solar = 0
            if 6 <= h <= 18:
                 solar = 5
            
            rem = 100 - hydro - wind - solar
            if rem < 0:
                hydro += rem # adjust
                rem = 0
            
            grid_mix = {"Hydro": int(hydro), "Wind": int(wind), "Solar": int(solar), "Nuclear": int(rem)}
            
        else: # Gas/Mix
            gas = 40 + (val/500)*20
            nuclear = 20
            solar = 0
            if 6 <= h <= 18:
                solar = 20 * np.sin((h-6)*np.pi/12)
            
            rem = 100 - gas - nuclear - solar
            wind = max(0, rem)
            grid_mix = {"Gas": int(gas), "Nuclear": int(nuclear), "Solar": int(solar), "Wind": int(wind)}

        grid_mixes.append(grid_mix)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "carbon_intensity": carbon_values,
        "price": prices,
        "grid_mix": grid_mixes
    })
    
    return df

def get_recommendation_logic(workload_type, inputs):
    """
    Returns specific text based on workload type logic.
    """
    if workload_type == "GenAI Training":
        gpu = inputs.get("GPU Type", "H100")
        return f"💡 **Recommendation:** Shifting this **{gpu} cluster** to 'Europe (Stockholm)' reduces carbon by **92%**. Latency is irrelevant for training jobs. Shadow savings: **$4,500**."
    
    elif workload_type == "Inference Fleet":
        return f"💡 **Recommendation:** Route via **Geo-DNS** to 'US-East' for off-peak hours? Saves **12% Cost**. Latency impact: +40ms (Within SLA)."
        
    elif workload_type == "HPC Simulation":
        return f"💡 **Recommendation:** Your deadline is 48h away. **Pause & Resume** at 02:00 AM (Wind Peak) to improve **Net Efficiency Score** by +15."
        
    elif workload_type == "Enterprise ETL":
        return f"💡 **Recommendation:** Shifting this ETL job to 'US-East-N.Virginia' saves **12% Cost** and **40% Carbon**. Latency impact: Negligible."
        
    return "💡 Optimizing parameters..."

def generate_attribution_data():
    """Generates the scorecard for FinOps view."""
    data = {
        "Team": ["Data Science (GenAI)", "Core Platform", "Data Engineering (ETL)", "R&D"],
        "GPU Hours": [12500, 450, 3200, 800],
        "Carbon Intensity Avg": [450, 210, 680, 120], # gCO2/kWh
        "Net Efficiency Score": [72, 95, 45, 88] # 0-100
    }
    return pd.DataFrame(data)

def generate_iso_data():
    """Generates chart data for Compliance view."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    emissions = [500, 480, 460, 420, 400, 380, 350] # Trending down
    target = [450, 440, 430, 420, 410, 400, 390] # Linear target
    
    return pd.DataFrame({
        "Month": months,
        "Scope 2 Real": emissions,
        "Net Zero Target": target
    })

def generate_audit_logs():
    """Generates mock security logs for the Admin role."""
    logs = pd.DataFrame({
        "Timestamp": [datetime.now() - timedelta(minutes=i*15) for i in range(10)],
        "User": ["alice@company.com", "bob@company.com", "system_cron", "charlie@company.com", "alice@company.com"] * 2,
        "Action": ["Login", "Deploy Job", "Data Ingest", "API Key Access", "Logout"] * 2,
        "IP Address": ["192.168.1.10", "192.168.1.12", "Localhost", "10.0.0.5", "192.168.1.10"] * 2,
        "Status": ["Success", "Success", "Success", "Warn", "Success"] * 2
    })
    return logs

def generate_system_logs():
    """Generates a raw string of system logs."""
    logs = [
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Core Engine: Initialized Grid Connection",
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Data Ingest: Successfully fetched MP-Zone data",
        f"[WARN] {datetime.now().strftime('%H:%M:%S')} - Latency: 150ms detected in US-East region bridge",
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Optimizer: Found 2hr green window @ 03:00 AM",
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Scheduler: Queued 'LLaMA-7B-FineTune' for 03:00 AM",
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Security: Validating API Key for User-ID 8821",
        f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Compliance: Scope-2 Report Generated",
    ]
    return "\n".join(logs)
