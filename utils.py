import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data(seed=None):
    """
    Generates mock data for Carbon Intensity and Price for the next 48 hours.
    Carbon Intensity: Sine wave peaking at 7 PM (19:00), low around 2 AM (conceptually).
    Price: Correlated with Carbon.
    """
    if seed is not None:
        np.random.seed(seed)
        
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hours = 48
    
    # Generate timestamps
    timestamps = [now + timedelta(hours=i) for i in range(hours)]
    
    # Generate mock carbon intensity (gCO2/kWh)
    # Target: Peak at 19:00, Lows roughly at 2 AM.
    # We use a combined sine wave or just a shifted sine wave.
    # Simple sine wave period 24h.
    # Peak at 19. 
    # phase shift calculation: 
    # sin(2*pi*(t - shift)/24). Peak when argument is pi/2.
    # 2*pi*(19 - shift)/24 = pi/2 => (19-shift)/12 = 1/2 => 19-shift = 6 => shift = 13.
    
    x = np.array([t.hour + (24 if i >= 24 else 0) for i, t in enumerate(timestamps)]) # continuous hours not perfect but okay for wave
    # actually better to just use strict hour of day for pattern + some noise
    
    # We want a 48h series. 
    # Let's create a continuous time variable t from 0 to 47
    t = np.arange(hours)
    
    # Aligning phase so peak is at 7 PM (19:00) of the first day?
    # The start time 'now' varies. We need to align with actual hour of day.
    
    current_hour = now.hour
    # hour_offsets = (current_hour + t) % 24
    
    # To get peak at 19:00:
    # sin(2pi/24 * (hour - 13))
    
    base_carbon = 400
    amplitude = 150
    
    carbon_values = []
    prices = []
    solar_values = []
    
    for i in range(hours):
        dt = timestamps[i]
        h = dt.hour
        
        # Sine wave calculation for Carbon
        # Normalized -1 to 1
        wave = np.sin(2 * np.pi * (h - 13) / 24)
        
        # Add some randomness
        noise = np.random.normal(0, 20)
        
        # Skew slightly to push low towards 2 AM if possible, but standard sine is fine.
        val = base_carbon + (amplitude * wave) + noise
        val = max(100, val) # clamp
        
        carbon_values.append(int(val))
        
        # Price correlates with carbon (high demand = dirty peaker plants = expensive)
        # Base price 5 INR, max 15 INR
        price_noise = np.random.normal(0, 0.5)
        price = 4 + (val / 50) + price_noise
        prices.append(round(price, 2))
        
        # Solar Generation % (0 at night, peak at 12:00)
        # Simple Model: Sine wave from 06:00 to 18:00
        if 6 <= h <= 18:
            # Peak at 12. 
            # (h - 6) maps 6->0, 12->6, 18->12
            # We want sin(0) to sin(pi).
            # Argument = (h-6) * pi / 12
            solar_arg = (h - 6) * np.pi / 12
            solar_val = np.sin(solar_arg) * 100 # Peak at 100%
            
            # Add noise/weather
            solar_noise = np.random.normal(0, 5)
            solar_val = max(0, min(100, solar_val + solar_noise))
        else:
            solar_val = 0
            
        solar_values.append(int(solar_val))
        
    df = pd.DataFrame({
        "timestamp": timestamps,
        "carbon_intensity": carbon_values,
        "price": prices,
        "solar_generation": solar_values
    })
    
    return df

def find_optimal_window(df, duration_hours):
    """
    Finds the window of 'duration_hours' with the lowest average carbon intensity.
    Returns: start_time, avg_carbon, total_cost_estimate (heuristic)
    """
    if duration_hours > len(df):
        return None
    
    rolling_carbon = df['carbon_intensity'].rolling(window=duration_hours).mean()
    # rolling gives value at the end of the window. 
    # We want to identify the start index.
    # Shift backward to align with start time? 
    # ACTUALLY, we can just iterate or use idxmin properly.
    
    # Valid indices for start of window are 0 to len-duration
    best_start_idx = -1
    min_avg = float('inf')
    
    for i in range(len(df) - duration_hours + 1):
        window = df.iloc[i : i+duration_hours]
        avg = window['carbon_intensity'].mean()
        if avg < min_avg:
            min_avg = avg
            best_start_idx = i
            
    if best_start_idx != -1:
        best_window = df.iloc[best_start_idx : best_start_idx+duration_hours]
        return {
            "start_time": best_window.iloc[0]['timestamp'],
            "end_time": best_window.iloc[-1]['timestamp'],
            "avg_carbon": min_avg,
            "avg_price": best_window['price'].mean(),
            "window_df": best_window
        }
    return None
