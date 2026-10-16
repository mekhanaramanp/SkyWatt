import streamlit as st
import pandas as pd
import numpy as np
import pickle
import datetime
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components

# Page configuration - Set sidebar to collapsed by default
st.set_page_config(
    page_title="Weather-Based Energy Predictor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Base directory of the app script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Custom CSS for Cyberpunk Glassmorphism, Floating Weather Icons, and Custom Cursors
st.markdown("""
<style>
    /* Default CSS Variables */
    :root {
        --glow-color: #fbbf24;
        --pulse-speed: 1.8s;
    }

    /* Parallax Background Elements */
    .parallax-bg {
        position: fixed;
        pointer-events: none;
        z-index: -2;
        transition: transform 0.35s cubic-bezier(.2,.7,.3,1);
    }

    /* Radial gradient orbs with dynamic color mapping */
    .orb-amber {
        top: 10%;
        left: 15%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, var(--glow-color) 0%, rgba(0,0,0,0) 70%);
        filter: blur(55px);
        opacity: 0.85;
        transition: background 0.8s ease-in-out;
    }
    
    .orb-violet {
        bottom: 10%;
        right: 15%;
        width: 450px;
        height: 450px;
        background: radial-gradient(circle, rgba(167, 139, 250, 0.18) 0%, rgba(0,0,0,0) 70%);
        filter: blur(55px);
    }
    
    .orb-blue {
        top: 45%;
        left: 40%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, rgba(0,0,0,0) 70%);
        filter: blur(55px);
    }

    /* Floating Weather Items */
    .emoji-item {
        font-size: 3.5rem;
        opacity: 0.08;
        z-index: -2;
    }

    /* Main App Background and Styling */
    .stApp {
        background: #0a0e1a !important;
        color: #f1f5f9;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Header Container styling */
    .header-container {
        text-align: center;
        padding: 3rem 1.5rem 2.5rem 1.5rem;
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(18px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fbbf24 0%, #f1f5f9 50%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-title {
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 0px;
    }

    /* Custom Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.55);
        backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.07);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        margin-bottom: 2rem;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .glass-card:hover {
        border-color: rgba(251, 191, 36, 0.35);
        box-shadow: 0 20px 45px rgba(251, 191, 36, 0.15);
        transform: translateY(-4px);
    }

    /* Glowing Output Card */
    .glass-card-predicted {
        border: 1px solid var(--glow-color);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 15px var(--glow-color);
        animation: pulse-card var(--pulse-speed) infinite alternate ease-in-out;
    }

    @keyframes pulse-card {
        0% {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 10px var(--glow-color);
            transform: translateY(0px);
        }
        100% {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 22px var(--glow-color);
            transform: translateY(-2px);
        }
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.6rem;
    }
    
    .metric-value {
        font-size: 3.4rem;
        font-weight: 900;
        color: #f8fafc;
        line-height: 1.05;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    .metric-unit {
        font-size: 1.5rem;
        color: var(--glow-color);
        font-weight: 700;
        transition: color 0.5s ease;
    }

    /* Demand Badges */
    .demand-badge {
        display: inline-block;
        padding: 0.4rem 1.4rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    .demand-low {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
    }
    
    .demand-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.1);
    }
    
    .demand-high {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        box-shadow: 0 0 18px rgba(239, 68, 68, 0.15);
    }

    /* Insight Block */
    .insight-block {
        background: rgba(251, 191, 36, 0.04);
        border-left: 4px solid var(--glow-color);
        border-radius: 12px;
        padding: 1.6rem;
        margin-top: 1.5rem;
        border-right: 1px solid rgba(251, 191, 36, 0.05);
        border-top: 1px solid rgba(251, 191, 36, 0.05);
        border-bottom: 1px solid rgba(251, 191, 36, 0.05);
        transition: border-left-color 0.5s ease;
    }
    
    .insight-title {
        font-weight: 700;
        color: var(--glow-color);
        margin-bottom: 0.5rem;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: color 0.5s ease;
    }

    /* Modern Styled Input & Button overrides */
    .stButton>button {
        background: rgba(15, 23, 42, 0.55) !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.75rem 2.2rem !important;
        font-size: 1rem !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    .stButton>button:hover {
        border-color: rgba(251, 191, 36, 0.5) !important;
        color: #fbbf24 !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(251, 191, 36, 0.15) !important;
    }

    /* Active navigation button highlight */
    div.nav-active button {
        background: linear-gradient(90deg, #fbbf24 0%, #a78bfa 100%) !important;
        color: #0a0e1a !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3) !important;
    }

    /* Landing Page Hero CTA Button Overrides */
    .hero-btn-filled button {
        background: #fbbf24 !important;
        color: #0a0e1a !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.9rem 2.2rem !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .hero-btn-filled button:hover {
        background: #f59e0b !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(251, 191, 36, 0.5) !important;
    }

    .hero-btn-outline button {
        background: rgba(15, 23, 42, 0.45) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.9rem 2.2rem !important;
        font-size: 1.05rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .hero-btn-outline button:hover {
        border-color: #a78bfa !important;
        color: #a78bfa !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(167, 139, 250, 0.15) !important;
    }

    /* Slider handle custom glows & gradients */
    .stSlider div[role="slider"] {
        background-color: var(--glow-color) !important;
        box-shadow: 0 0 10px var(--glow-color), 0 0 20px var(--glow-color) !important;
        border: 2px solid #0a0e1a !important;
        transition: box-shadow 0.15s ease !important;
    }
    
    .stSlider div[role="slider"]:hover, .stSlider div[role="slider"]:active {
        box-shadow: 0 0 18px var(--glow-color), 0 0 36px var(--glow-color), 0 0 54px var(--glow-color) !important;
    }
    
    /* Slider progress track colored gradients */
    .stSlider div[data-baseweb="slider"] > div > div > div {
        background: linear-gradient(90deg, #a78bfa 0%, var(--glow-color) 100%) !important;
        transition: background 0.5s ease;
    }

    /* Input textboxes styling on the right side of manual sliders */
    .stNumberInput input {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        height: 40px !important;
    }
    
    .stNumberInput input:focus {
        border-color: var(--glow-color) !important;
        box-shadow: 0 0 12px var(--glow-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load Javascript component for cursor and parallax handling in the parent document context
components.html("""
<script>
const parentDoc = window.parent.document;

// 1. Guard against duplicate injection on Streamlit reruns
if (!parentDoc.getElementById('bg-field') || !parentDoc.querySelector('.custom-cursor-dot')) {
    
    // Create styles for parent document
    const style = parentDoc.createElement('style');
    style.innerHTML = `
        /* Disable cursor for the entire screen */
        html, body, [data-testid="stAppViewContainer"], .stApp, a, button, [role="button"], input, select, .stSlider > div, div[data-baseweb="select"] {
            cursor: none !important;
        }
        
        .custom-cursor-dot {
            width: 10px;
            height: 10px;
            background-color: #fbbf24;
            border-radius: 50%;
            position: fixed;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 999999;
            box-shadow: 0 0 10px #fbbf24, 0 0 20px #fbbf24;
            left: -100px;
            top: -100px;
            transition: width 0.15s, height 0.15s, background-color 0.15s;
        }
        
        .custom-cursor-ring {
            width: 34px;
            height: 34px;
            border: 1.5px solid #a78bfa;
            border-radius: 50%;
            position: fixed;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 999998;
            left: -100px;
            top: -100px;
            transition: width 0.2s, height 0.2s, border-color 0.2s;
        }
        
        .custom-cursor-hover .custom-cursor-dot {
            width: 14px;
            height: 14px;
            background-color: #fbbf24;
            box-shadow: 0 0 12px #fbbf24, 0 0 24px #fbbf24;
        }
        
        .custom-cursor-hover .custom-cursor-ring {
            width: 44px;
            height: 44px;
            border-color: #fbbf24;
        }
        
        /* Parallax Background Element styling */
        .parallax-bg {
            position: absolute;
            pointer-events: none;
            transition: transform 0.35s cubic-bezier(.2,.7,.3,1);
        }
        
        .orb-amber {
            top: 10%;
            left: 15%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, var(--glow-color) 0%, rgba(0,0,0,0) 70%);
            filter: blur(55px);
        }
        
        .orb-violet {
            bottom: 10%;
            right: 15%;
            width: 450px;
            height: 450px;
            background: radial-gradient(circle, rgba(167, 139, 250, 0.18) 0%, rgba(0,0,0,0) 70%);
            filter: blur(55px);
        }
        
        .orb-blue {
            top: 45%;
            left: 40%;
            width: 350px;
            height: 350px;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, rgba(0,0,0,0) 70%);
            filter: blur(55px);
        }
        
        .emoji-item {
            font-size: 3.5rem;
            opacity: 0.08;
            user-select: none;
        }
        
        /* Mobile fallback - fallback to standard cursors and static positions on touch screens */
        @media (hover: none) and (pointer: coarse) {
            .custom-cursor-dot, .custom-cursor-ring {
                display: none !important;
            }
            html, body, [data-testid="stAppViewContainer"], .stApp, a, button, [role="button"], input, select, .stSlider > div {
                cursor: auto !important;
            }
            .parallax-bg {
                transform: none !important;
                transition: none !important;
            }
        }
    `;
    parentDoc.head.appendChild(style);
    
    // Create cursor elements if missing
    let dot = parentDoc.querySelector('.custom-cursor-dot');
    if (!dot) {
        dot = parentDoc.createElement('div');
        dot.className = 'custom-cursor-dot';
        parentDoc.body.appendChild(dot);
    }
    
    let ring = parentDoc.querySelector('.custom-cursor-ring');
    if (!ring) {
        ring = parentDoc.createElement('div');
        ring.className = 'custom-cursor-ring';
        parentDoc.body.appendChild(ring);
    }
    
    // Create bg-field container for parallax elements if missing
    let bgField = parentDoc.getElementById('bg-field');
    if (!bgField) {
        bgField = parentDoc.createElement('div');
        bgField.id = 'bg-field';
        bgField.style.cssText = 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: -2; overflow: hidden;';
        
        // Helper to add background elements
        const addEl = (className, depth, styles, content = '') => {
            const el = parentDoc.createElement('div');
            el.className = 'parallax-bg ' + className;
            el.setAttribute('data-depth', depth);
            el.style.cssText = styles;
            if (content) el.innerHTML = content;
            bgField.appendChild(el);
        };
        
        // Add Orbs to container
        addEl('orb-amber', '0.08', '');
        addEl('orb-violet', '0.06', '');
        addEl('orb-blue', '0.04', '');
        
        // Add Emojis to container
        addEl('emoji-item', '0.12', 'position: absolute; top: 15%; left: 8%;', '⚡');
        addEl('emoji-item', '0.10', 'position: absolute; top: 45%; right: 7%;', '☁️');
        addEl('emoji-item', '0.08', 'position: absolute; bottom: 25%; left: 10%;', '🌡️');
        addEl('emoji-item', '0.14', 'position: absolute; top: 75%; right: 14%;', '🌩️');
        addEl('emoji-item', '0.06', 'position: absolute; top: 8%; right: 26%;', '☀️');
        
        // Append bgField to parent body
        parentDoc.body.appendChild(bgField);
    }
    
    let mouseX = -100;
    let mouseY = -100;
    let ringX = -100;
    let ringY = -100;
    
    // Listen to mouse movements for cursors and parallax updates on parent document
    parentDoc.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';
        
        // Calculate offsets from screen center
        const w = window.parent.innerWidth;
        const h = window.parent.innerHeight;
        const xOffset = mouseX - w / 2;
        const yOffset = mouseY - h / 2;
        
        // Apply parallax shift opposite to mouse direction
        bgField.querySelectorAll('.parallax-bg').forEach(el => {
            const depth = parseFloat(el.getAttribute('data-depth')) || 0.05;
            const moveX = -xOffset * depth;
            const moveY = -yOffset * depth;
            el.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
    });
    
    // Smooth frame animation loop for trailing ring cursor
    function animate() {
        ringX += (mouseX - ringX) * 0.15;
        ringY += (mouseY - ringY) * 0.15;
        ring.style.left = ringX + 'px';
        ring.style.top = ringY + 'px';
        
        // Dynamic color matching to CSS --glow-color variable
        const bodyStyle = window.getComputedStyle(parentDoc.body);
        const dynamicGlow = bodyStyle.getPropertyValue('--glow-color').trim();
        if (dynamicGlow) {
            ring.style.borderColor = dynamicGlow;
        } else {
            ring.style.borderColor = '#a78bfa';
        }
        
        requestAnimationFrame(animate);
    }
    animate();
    
    // Monitor elements dynamically to apply hover scaling class
    const updateHoverListeners = () => {
        parentDoc.querySelectorAll('a, button, [role="button"], input, select, .stSlider > div, .glass-card, div[data-baseweb="select"]').forEach(el => {
            if (!el.dataset.hasCursorEvents) {
                el.dataset.hasCursorEvents = "true";
                el.addEventListener('mouseenter', () => {
                    parentDoc.body.classList.add('custom-cursor-hover');
                });
                el.addEventListener('mouseleave', () => {
                    parentDoc.body.classList.remove('custom-cursor-hover');
                });
            }
        });
    };
    setInterval(updateHoverListeners, 800);
    updateHoverListeners();
}
</script>
""", height=0, width=0)

# Load Model
@st.cache_resource
def load_model_and_meta():
    model_path = os.path.join(BASE_DIR, "model", "energy_model.pkl")
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    return data

try:
    meta_data = load_model_and_meta()
    model = meta_data['model']
    features = meta_data['features']
    weather_map = meta_data['weather_map']
except Exception as e:
    st.error(f"Error loading prediction model: {e}. Please run model_training.ipynb first.")
    st.stop()

# Load Dataset for averages and history
@st.cache_data
def load_historical_data():
    dataset_path = os.path.join(BASE_DIR, "dataset", "energy_weather.csv")
    df = pd.read_csv(dataset_path)
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d-%m-%Y %H:%M')
    df['Hour'] = df['Datetime'].dt.hour
    df['Month'] = df['Datetime'].dt.month
    df['Weekday'] = df['Datetime'].dt.weekday
    df['Year'] = df['Datetime'].dt.year
    return df

try:
    df_hist = load_historical_data()
except Exception as e:
    st.warning(f"Could not load historical dataset: {e}")
    df_hist = None

# Initialize session state variables
if 'show_dashboard' not in st.session_state:
    st.session_state['show_dashboard'] = False
if 'show_docs' not in st.session_state:
    st.session_state['show_docs'] = False
if 'predict_mode' not in st.session_state:
    st.session_state['predict_mode'] = 'manual'
if 'temp' not in st.session_state:
    st.session_state['temp'] = 25.0
if 'humidity' not in st.session_state:
    st.session_state['humidity'] = 60.0
if 'wind_speed' not in st.session_state:
    st.session_state['wind_speed'] = 12.0
if 'pressure' not in st.session_state:
    st.session_state['pressure'] = 1013.0
if 'cloud_cover' not in st.session_state:
    st.session_state['cloud_cover'] = 40.0
if 'weather_cond' not in st.session_state:
    st.session_state['weather_cond'] = "Sunny"
if 'day_idx' not in st.session_state:
    st.session_state['day_idx'] = 0
if 'hour_idx' not in st.session_state:
    st.session_state['hour_idx'] = 14
if 'month_idx' not in st.session_state:
    st.session_state['month_idx'] = datetime.datetime.now().month

# Initialize manual sync state variables
if 'temp_slider' not in st.session_state:
    st.session_state['temp_slider'] = st.session_state['temp']
if 'temp_num' not in st.session_state:
    st.session_state['temp_num'] = st.session_state['temp']

if 'humidity_slider' not in st.session_state:
    st.session_state['humidity_slider'] = st.session_state['humidity']
if 'humidity_num' not in st.session_state:
    st.session_state['humidity_num'] = st.session_state['humidity']

if 'wind_slider' not in st.session_state:
    st.session_state['wind_slider'] = st.session_state['wind_speed']
if 'wind_num' not in st.session_state:
    st.session_state['wind_num'] = st.session_state['wind_speed']

if 'pressure_slider' not in st.session_state:
    st.session_state['pressure_slider'] = st.session_state['pressure']
if 'pressure_num' not in st.session_state:
    st.session_state['pressure_num'] = st.session_state['pressure']

if 'cloud_slider' not in st.session_state:
    st.session_state['cloud_slider'] = st.session_state['cloud_cover']
if 'cloud_num' not in st.session_state:
    st.session_state['cloud_num'] = st.session_state['cloud_cover']

# ----------------- SLIDER & NUMBER SYNC CALLBACKS -----------------
def sync_temp_slider():
    st.session_state['temp'] = st.session_state['temp_slider']
    st.session_state['temp_num'] = st.session_state['temp_slider']

def sync_temp_num():
    st.session_state['temp'] = st.session_state['temp_num']
    st.session_state['temp_slider'] = st.session_state['temp_num']

def sync_humidity_slider():
    st.session_state['humidity'] = st.session_state['humidity_slider']
    st.session_state['humidity_num'] = st.session_state['humidity_slider']

def sync_humidity_num():
    st.session_state['humidity'] = st.session_state['humidity_num']
    st.session_state['humidity_slider'] = st.session_state['humidity_num']

def sync_wind_slider():
    st.session_state['wind_speed'] = st.session_state['wind_slider']
    st.session_state['wind_num'] = st.session_state['wind_slider']

def sync_wind_num():
    st.session_state['wind_speed'] = st.session_state['wind_num']
    st.session_state['wind_slider'] = st.session_state['wind_num']

def sync_pressure_slider():
    st.session_state['pressure'] = st.session_state['pressure_slider']
    st.session_state['pressure_num'] = st.session_state['pressure_slider']

def sync_pressure_num():
    st.session_state['pressure'] = st.session_state['pressure_num']
    st.session_state['pressure_slider'] = st.session_state['pressure_num']

def sync_cloud_slider():
    st.session_state['cloud_cover'] = st.session_state['cloud_slider']
    st.session_state['cloud_num'] = st.session_state['cloud_slider']

def sync_cloud_num():
    st.session_state['cloud_cover'] = st.session_state['cloud_num']
    st.session_state['cloud_slider'] = st.session_state['cloud_num']

# -------------------------------------------------------------
# -------------------- VIEW 1: LANDING HERO PAGE --------------
# -------------------------------------------------------------
if not st.session_state['show_dashboard']:
    
    # 1. Badge Pill
    st.markdown("""
        <div style="text-align: center; margin-top: 5.5rem; margin-bottom: 1.5rem; animation: fadeInDown 0.8s ease;">
            <span style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                border: 1px solid rgba(251, 191, 36, 0.25);
                background: rgba(251, 191, 36, 0.05);
                color: #fbbf24;
                font-weight: 700;
                font-size: 0.8rem;
                padding: 0.45rem 1.25rem;
                border-radius: 9999px;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            ">
                ⚡ Live Grid Forecasting
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Glowing Hero Title
    st.markdown("""
        <h1 style="
            text-align: center;
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 1.5rem;
            letter-spacing: -0.03em;
            animation: fadeIn 1s ease;
        ">
            <span style="
                background: linear-gradient(135deg, #ffe082 0%, #fbbf24 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">Predict energy demand</span><br/>
            <span style="
                background: linear-gradient(135deg, #e2e8f0 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">before the weather turns</span>
        </h1>
    """, unsafe_allow_html=True)
    
    # 3. Sub-title
    st.markdown("""
        <p style="
            text-align: center;
            max-width: 680px;
            margin: 0 auto;
            font-size: 1.15rem;
            color: #94a3b8;
            line-height: 1.65;
            font-weight: 400;
            margin-bottom: 3.5rem;
            animation: fadeIn 1.2s ease;
        ">
            A clean, glass-panel dashboard that reads temperature, humidity and sky conditions to forecast grid load — built for operators who need the next hour, not just the next report.
        </p>
    """, unsafe_allow_html=True)
    
    # 4. Action CTA Buttons
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([1.5, 1.2, 1.2, 1.5, 0.1])
    
    with col_c2:
        st.markdown('<div class="hero-btn-filled">', unsafe_allow_html=True)
        if st.button("Open dashboard", use_container_width=True, key="hero_open_dash"):
            st.session_state['show_dashboard'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_c3:
        st.markdown('<div class="hero-btn-outline">', unsafe_allow_html=True)
        if st.button("View documentation", use_container_width=True, key="hero_view_docs"):
            st.session_state['show_docs'] = not st.session_state['show_docs']
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Expandable Documentation Panel
    if st.session_state['show_docs']:
        st.markdown("""
            <div class="glass-card" style="max-width: 820px; margin: 3.5rem auto 0 auto; animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);">
                <h3 style="color:#fbbf24; margin-top:0px; font-weight:700; font-size:1.4rem; margin-bottom:1rem;">
                    📖 Model Architecture & Pipeline Specifications
                </h3>
                <p style="color:#cbd5e1; font-size:0.95rem; line-height:1.6; margin-bottom:1.5rem;">
                    This energy analytics grid uses a highly optimized <b>Random Forest Regressor</b> machine learning model, trained over a 14-year climatic dataset. It learns patterns between local meteorological variables and electricity grid loads.
                </p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; font-size:0.9rem; border-top:1px solid rgba(255,255,255,0.07); padding-top:1.5rem;">
                    <div>
                        <h4 style="color:#a78bfa; font-weight:700; margin-top:0px; margin-bottom:0.5rem;">🧠 Feature Coefficients</h4>
                        <ul style="color:#94a3b8; padding-left:1.2rem; line-height:1.6; margin:0px;">
                            <li><b>Dry-Bulb Temperature:</b> Direct thermal HVAC loading curves.</li>
                            <li><b>Relative Humidity:</b> Latent heat and moisture saturation levels.</li>
                            <li><b>Temporal Dimensions:</b> Hour profiles, weekday offsets, and seasonal month variations.</li>
                        </ul>
                    </div>
                    <div>
                        <h4 style="color:#a78bfa; font-weight:700; margin-top:0px; margin-bottom:0.5rem;">🛠️ Data Pipeline Details</h4>
                        <p style="color:#94a3b8; line-height:1.5; margin:0px;">
                            Input fields are scaled and formatted to match target column vectors. The predictions display estimated load deviations (MW) from standard grid base levels.
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# -------------------- VIEW 2: INTERACTIVE DASHBOARD ----------
# -------------------------------------------------------------
else:
    # Navigation link at the top to go back to landing page
    back_col1, back_col2 = st.columns([1.5, 8.5])
    with back_col1:
        if st.button("⬅️ Back to Welcome", key="btn_back_home", use_container_width=True):
            st.session_state['show_dashboard'] = False
            st.rerun()

    # ----------------- VALUE CALCULATIONS -----------------
    # Demand categorization thresholds (statically defined)
    low_cutoff = 13630
    high_cutoff = 17200

    # Determine variables depending on active mode
    if st.session_state['predict_mode'] == 'live':
        # Live mode uses fetched values stored in session state
        temp_val = st.session_state['temp']
        humidity_val = st.session_state['humidity']
        wind_speed_val = st.session_state['wind_speed']
        pressure_val = st.session_state['pressure']
        cloud_cover_val = st.session_state['cloud_cover']
        weather_cond_val = st.session_state['weather_cond']
        day_idx_val = st.session_state['day_idx']
        hour_idx_val = st.session_state['hour_idx']
        month_idx_val = st.session_state['month_idx']
    else:
        # Manual mode variables will be bound directly to manual sliders
        temp_val = st.session_state['temp']
        humidity_val = st.session_state['humidity']
        wind_speed_val = st.session_state['wind_speed']
        pressure_val = st.session_state['pressure']
        cloud_cover_val = st.session_state['cloud_cover']
        weather_cond_val = st.session_state['weather_cond']
        day_idx_val = st.session_state['day_idx']
        hour_idx_val = st.session_state['hour_idx']
        month_idx_val = st.session_state['month_idx']

    # Fixed evaluation year
    eval_year = 2018

    # App Title & Header inside the dashboard view
    st.markdown("""
        <div class="header-container" style="padding: 2rem 1.5rem 1.5rem 1.5rem; margin-bottom: 1.5rem;">
            <h1 class="main-title" style="font-size: 2.4rem; margin-bottom:0.2rem;">Weather-Based Energy Predictor</h1>
            <p class="sub-title" style="font-size: 1rem;">Predicting Grid electricity consumption using real-time meteorological variables and temporal insights</p>
        </div>
    """, unsafe_allow_html=True)

    # ----------------- NAVIGATION SYSTEM -----------------
    col_n1, col_n2 = st.columns(2)

    with col_n1:
        is_manual_active = st.session_state['predict_mode'] == 'manual'
        if is_manual_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            
        if st.button("🎛️ Manual Simulator Prediction", use_container_width=True, key="nav_manual"):
            st.session_state['predict_mode'] = 'manual'
            st.rerun()
            
        if is_manual_active:
            st.markdown('</div>', unsafe_allow_html=True)

    with col_n2:
        is_live_active = st.session_state['predict_mode'] == 'live'
        if is_live_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        
        if st.button("🌐 Live Climate Sync Prediction", use_container_width=True, key="nav_live"):
            st.session_state['predict_mode'] = 'live'
            st.rerun()
            
        if is_live_active:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # ----------------- MODE 1: LIVE CLIMATE SYNC SYSTEM -----------------
    if st.session_state['predict_mode'] == 'live':
        
        # 1. Search Box
        st.markdown("""
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="text-align: center; margin-bottom: 1rem; font-weight: 700; color: #fbbf24; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.85rem;">
                    🌐 Satellite Synced Forecast Input
                </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns([1.2, 2.5, 1.2])
        with col_s2:
            col_city, col_btn = st.columns([2.5, 1])
            with col_city:
                city_options = ["Columbus", "Canton", "Fort Wayne", "Roanoke", "Charleston", "Kingsport", "Benton Harbor", "Other (Type Below)"]
                selected_city_opt = st.selectbox(
                    "Choose City Location", 
                    options=city_options, 
                    index=city_options.index(st.session_state.get('selected_city_opt', 'Columbus'))
                )
                st.session_state['selected_city_opt'] = selected_city_opt
                
                if selected_city_opt == "Other (Type Below)":
                    city_name_input = st.text_input("Enter city name:", value=st.session_state.get('custom_city_name', 'New Delhi'))
                    st.session_state['custom_city_name'] = city_name_input
                    city_search = city_name_input
                else:
                    city_search = selected_city_opt
                    
            with col_btn:
                st.markdown("<div style='padding-top: 1.7rem;'></div>", unsafe_allow_html=True)
                fetch_btn = st.button("🔌 Fetch Current Weather", use_container_width=True)

            if fetch_btn:
                with st.spinner(f"Acquiring meteorological details for {city_search}..."):
                    try:
                        # Geocoding
                        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_search}&count=1&language=en&format=json"
                        geo_resp = requests.get(geocode_url).json()
                        
                        if 'results' in geo_resp and len(geo_resp['results']) > 0:
                            result = geo_resp['results'][0]
                            lat = result['latitude']
                            lon = result['longitude']
                            res_name = result['name']
                            country = result.get('country', '')
                            
                            # Fetch Weather
                            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,cloud_cover,weather_code&timezone=auto"
                            weather_data = requests.get(weather_url).json()['current']
                            
                            # Store in session state
                            st.session_state['temp'] = float(weather_data['temperature_2m'])
                            st.session_state['humidity'] = float(weather_data['relative_humidity_2m'])
                            st.session_state['wind_speed'] = float(weather_data['wind_speed_10m'])
                            st.session_state['pressure'] = float(weather_data['surface_pressure'])
                            st.session_state['cloud_cover'] = float(weather_data['cloud_cover'])
                            
                            # Sync helper states for manual controls
                            st.session_state['temp_slider'] = st.session_state['temp']
                            st.session_state['temp_num'] = st.session_state['temp']
                            st.session_state['humidity_slider'] = st.session_state['humidity']
                            st.session_state['humidity_num'] = st.session_state['humidity']
                            st.session_state['wind_slider'] = st.session_state['wind_speed']
                            st.session_state['wind_num'] = st.session_state['wind_speed']
                            st.session_state['pressure_slider'] = st.session_state['pressure']
                            st.session_state['pressure_num'] = st.session_state['pressure']
                            st.session_state['cloud_slider'] = st.session_state['cloud_cover']
                            st.session_state['cloud_num'] = st.session_state['cloud_cover']
                            
                            w_code = weather_data['weather_code']
                            if w_code in [0, 1]:
                                st.session_state['weather_cond'] = "Sunny"
                            elif w_code in [2, 3, 45, 48]:
                                st.session_state['weather_cond'] = "Cloudy"
                            else:
                                st.session_state['weather_cond'] = "Rainy"
                                
                            # Parse actual local time of the city from Open-Meteo response
                            local_time_str = weather_data['time']
                            local_dt = datetime.datetime.strptime(local_time_str, "%Y-%m-%dT%H:%M")
                            
                            st.session_state['hour_idx'] = local_dt.hour
                            st.session_state['day_idx'] = local_dt.weekday()
                            st.session_state['month_idx'] = local_dt.month
                            st.session_state['live_city'] = f"{res_name}, {country}"
                            st.session_state['live_time'] = local_dt.strftime("%I:%M %p, %A (%B %d)")
                            
                            st.toast(f"Successfully synced with {res_name}!", icon="🌐")
                            st.rerun()
                        else:
                            st.error("Target area not found.")
                    except Exception as e:
                        st.error(f"Weather sync failed: {e}")
                        
        st.markdown("</div>", unsafe_allow_html=True)

        # 2. Main Live Dash split layout
        col_live_info, col_live_dash = st.columns([1, 1.2])
        
        with col_live_info:
            # Synced details card
            if 'live_city' in st.session_state:
                st.markdown(f"""
                    <div class="glass-card" style="height: 100%;">
                        <h3 style="color:#fbbf24; margin-top:0px; font-weight:700; margin-bottom:1rem; font-size:1.2rem;">
                            📍 Synced Station Details
                        </h3>
                        <div style="font-size:1.6rem; font-weight: 800; color:#f8fafc; margin-bottom:1rem;">
                            {st.session_state['live_city']}
                        </div>
                        <div style="border-top:1px solid rgba(255,255,255,0.07); padding-top:1rem; display:grid; grid-template-columns: 1fr 1fr; gap:15px; font-size:0.95rem; color:#cbd5e1; line-height:1.6;">
                            <div>🌡️ Temperature:<br/><b style="font-size:1.15rem; color:#f1f5f9;">{st.session_state['temp']:.1f}°C</b></div>
                            <div>💧 Humidity:<br/><b style="font-size:1.15rem; color:#f1f5f9;">{st.session_state['humidity']:.0f}%</b></div>
                            <div>💨 Wind Speed:<br/><b style="font-size:1.15rem; color:#f1f5f9;">{st.session_state['wind_speed']:.1f} km/h</b></div>
                            <div>🧭 Baro Pressure:<br/><b style="font-size:1.15rem; color:#f1f5f9;">{st.session_state['pressure']:.0f} hPa</b></div>
                            <div>☁️ Cloud Cover:<br/><b style="font-size:1.15rem; color:#f1f5f9;">{st.session_state['cloud_cover']:.0f}%</b></div>
                            <div>🌈 Condition:<br/><b style="font-size:1.15rem; color:#fbbf24;">{st.session_state['weather_cond']}</b></div>
                        </div>
                        <div style="border-top:1px solid rgba(255,255,255,0.07); padding-top:0.8rem; margin-top:1rem; font-size:0.85rem; color:#94a3b8;">
                            🕒 <b>Local Time:</b> {st.session_state['live_time']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="glass-card" style="height: 100%; text-align:center; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                        <span style="font-size:3.5rem;">📡</span>
                        <h3 style="color:#94a3b8; font-weight:700; margin-top:0.5rem; margin-bottom:0.5rem;">No Location Synced</h3>
                        <p style="color:#64748b; font-size:0.9rem;">Quick-select Columbus at the top and click "Fetch Current Weather" to begin.</p>
                    </div>
                """, unsafe_allow_html=True)

        # Prediction execution
        weather_encoded_val = weather_map.get(weather_cond_val, 0)
        input_features = pd.DataFrame([[
            temp_val, humidity_val, wind_speed_val, pressure_val, cloud_cover_val, 
            weather_encoded_val, hour_idx_val, day_idx_val, month_idx_val, eval_year
        ]], columns=features)
        prediction = model.predict(input_features)[0]

        # Bounds for Averages
        if df_hist is not None:
            hist_avg = df_hist[(df_hist['Hour'] == hour_idx_val) & (df_hist['Month'] == month_idx_val)]['AEP_MW'].mean()
            hist_min = df_hist['AEP_MW'].min()
            hist_max = df_hist['AEP_MW'].max()
        else:
            hist_min, hist_max = 9580, 25700
            hist_avg = 15500

        # Demand levels and styling setup
        if prediction < low_cutoff:
            demand_level = "Low"
            demand_class = "demand-low"
            glow_color = "#34d399"
            pulse_speed = "2.5s"
        elif prediction > high_cutoff:
            demand_level = "High"
            demand_class = "demand-high"
            glow_color = "#f87171"
            pulse_speed = "1.0s"
        else:
            demand_level = "Medium"
            demand_class = "demand-medium"
            glow_color = "#fbbf24"
            pulse_speed = "1.8s"

        # Inject dynamic CSS variables based on prediction properties
        st.markdown(f"""
        <style>
            :root {{
                --glow-color: {glow_color} !important;
                --pulse-speed: {pulse_speed} !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        with col_live_dash:
            st.markdown("""
                <div class="glass-card glass-card-predicted" style="height: 100%;">
                    <h3 style="color:#a78bfa; margin-top:0px; font-weight:700; margin-bottom:1rem; font-size:1.2rem;">
                        📊 Synced Live Forecast Predictions
                    </h3>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); padding: 1.2rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center; margin-bottom: 1.2rem; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);">
                    <div class="metric-label">Forecast Grid Load</div>
                    <div class="metric-value">{prediction:,.1f} <span class="metric-unit">MW</span></div>
                    <div style="margin-top: 0.6rem;">
                        <span class="demand-badge {demand_class}">{demand_level} Demand Profile</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Plotly Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prediction,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Demand Gauge (MW)", 'font': {'size': 13, 'color': '#94a3b8', 'family': 'Outfit'}},
                gauge = {
                    'axis': {'range': [hist_min, hist_max], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                    'bar': {'color': glow_color, 'thickness': 0.25},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255,255,255,0.07)",
                    'steps': [
                        {'range': [hist_min, low_cutoff], 'color': 'rgba(16, 185, 129, 0.15)'},
                        {'range': [low_cutoff, high_cutoff], 'color': 'rgba(245, 158, 11, 0.15)'},
                        {'range': [high_cutoff, hist_max], 'color': 'rgba(239, 68, 68, 0.15)'}
                    ],
                    'threshold': {
                        'line': {'color': glow_color, 'width': 4},
                        'thickness': 0.75,
                        'value': prediction
                    }
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#f1f5f9", 'family': "Outfit"}, margin=dict(l=10, r=10, t=30, b=10), height=170)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- MODE 2: MANUAL SIMULATOR SYSTEM -----------------
    else:
        col_ctrl, col_dash = st.columns([1.1, 1.2])

        with col_ctrl:
            st.markdown("""
                <div class="glass-card">
                    <h3 style="color:#fbbf24; margin-top:0px; font-weight:700; margin-bottom:1.5rem; display:flex; align-items:center; gap:8px;">
                        🎛️ Manual Simulator Controls
                    </h3>
            """, unsafe_allow_html=True)
            
            # 1. Temperature Control Row
            col_t_sld, col_t_num = st.columns([3.2, 1])
            with col_t_sld:
                temp_val = st.slider(
                    "🌡️ Temperature (°C)", 
                    min_value=-15.0, 
                    max_value=40.0, 
                    value=st.session_state['temp'], 
                    step=0.5, 
                    key="temp_slider",
                    on_change=sync_temp_slider
                )
            with col_t_num:
                st.markdown("<div style='padding-top: 1.6rem;'></div>", unsafe_allow_html=True)
                temp_num = st.number_input(
                    "Temp Num", 
                    min_value=-15.0, 
                    max_value=40.0, 
                    value=st.session_state['temp'], 
                    step=0.5, 
                    label_visibility="collapsed", 
                    key="temp_num",
                    on_change=sync_temp_num
                )
            
            # 2. Humidity Control Row
            col_h_sld, col_h_num = st.columns([3.2, 1])
            with col_h_sld:
                humidity_val = st.slider(
                    "💧 Humidity (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=st.session_state['humidity'], 
                    step=1.0, 
                    key="humidity_slider",
                    on_change=sync_humidity_slider
                )
            with col_h_num:
                st.markdown("<div style='padding-top: 1.6rem;'></div>", unsafe_allow_html=True)
                humidity_num = st.number_input(
                    "Humid Num", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=st.session_state['humidity'], 
                    step=1.0, 
                    label_visibility="collapsed", 
                    key="humidity_num",
                    on_change=sync_humidity_num
                )
                
            # 3. Wind Speed Control Row
            col_w_sld, col_w_num = st.columns([3.2, 1])
            with col_w_sld:
                wind_speed_val = st.slider(
                    "💨 Wind Speed (km/h)", 
                    min_value=0.0, 
                    max_value=50.0, 
                    value=st.session_state['wind_speed'], 
                    step=0.5, 
                    key="wind_slider",
                    on_change=sync_wind_slider
                )
            with col_w_num:
                st.markdown("<div style='padding-top: 1.6rem;'></div>", unsafe_allow_html=True)
                wind_num = st.number_input(
                    "Wind Num", 
                    min_value=0.0, 
                    max_value=50.0, 
                    value=st.session_state['wind_speed'], 
                    step=0.5, 
                    label_visibility="collapsed", 
                    key="wind_num",
                    on_change=sync_wind_num
                )
                
            # 4. Barometric Pressure Control Row
            col_p_sld, col_p_num = st.columns([3.2, 1])
            with col_p_sld:
                pressure_val = st.slider(
                    "🧭 Barometric Pressure (hPa)", 
                    min_value=980.0, 
                    max_value=1050.0, 
                    value=st.session_state['pressure'], 
                    step=1.0, 
                    key="pressure_slider",
                    on_change=sync_pressure_slider
                )
            with col_p_num:
                st.markdown("<div style='padding-top: 1.6rem;'></div>", unsafe_allow_html=True)
                pressure_num = st.number_input(
                    "Press Num", 
                    min_value=980.0, 
                    max_value=1050.0, 
                    value=st.session_state['pressure'], 
                    step=1.0, 
                    label_visibility="collapsed", 
                    key="pressure_num",
                    on_change=sync_pressure_num
                )
                
            # 5. Cloud Cover Control Row
            col_c_sld, col_c_num = st.columns([3.2, 1])
            with col_c_sld:
                cloud_cover_val = st.slider(
                    "☁️ Cloud Cover (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=st.session_state['cloud_cover'], 
                    step=1.0, 
                    key="cloud_slider",
                    on_change=sync_cloud_slider
                )
            with col_c_num:
                st.markdown("<div style='padding-top: 1.6rem;'></div>", unsafe_allow_html=True)
                cloud_num = st.number_input(
                    "Cloud Num", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=st.session_state['cloud_cover'], 
                    step=1.0, 
                    label_visibility="collapsed", 
                    key="cloud_num",
                    on_change=sync_cloud_num
                )
            
            weather_options = ["Sunny", "Cloudy", "Rainy"]
            weather_cond_val = st.selectbox(
                "🌈 Sky Condition",
                options=weather_options,
                index=weather_options.index(st.session_state['weather_cond'])
            )

            st.markdown("---")
            st.markdown("<h4 style='color:#a78bfa; font-weight:700; margin-top:0px;'>📅 Time & Seasonal Profiles</h4>", unsafe_allow_html=True)
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = st.selectbox("📅 Weekday Profile", options=days, index=st.session_state['day_idx'])
            day_idx_val = days.index(selected_day)
            
            hours = [
                "12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
                "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"
            ]
            selected_hour = st.selectbox("⏰ Time Window (Hour)", options=hours, index=st.session_state['hour_idx'])
            hour_idx_val = hours.index(selected_hour)
            
            months = [
                "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"
            ]
            selected_month = st.selectbox("🍂 Seasonal Month", options=months, index=st.session_state['month_idx'] - 1)
            month_idx_val = months.index(selected_month) + 1
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Sync manual settings back to session state so switching modes keeps them
        st.session_state['temp'] = temp_val
        st.session_state['humidity'] = humidity_val
        st.session_state['wind_speed'] = wind_speed_val
        st.session_state['pressure'] = pressure_val
        st.session_state['cloud_cover'] = cloud_cover_val
        st.session_state['weather_cond'] = weather_cond_val
        st.session_state['day_idx'] = day_idx_val
        st.session_state['hour_idx'] = hour_idx_val
        st.session_state['month_idx'] = month_idx_val

        # Run Prediction
        weather_encoded_val = weather_map.get(weather_cond_val, 0)
        input_features = pd.DataFrame([[
            temp_val, humidity_val, wind_speed_val, pressure_val, cloud_cover_val, 
            weather_encoded_val, hour_idx_val, day_idx_val, month_idx_val, eval_year
        ]], columns=features)
        prediction = model.predict(input_features)[0]

        # Bounds for comparison
        if df_hist is not None:
            hist_avg = df_hist[(df_hist['Hour'] == hour_idx_val) & (df_hist['Month'] == month_idx_val)]['AEP_MW'].mean()
            hist_min = df_hist['AEP_MW'].min()
            hist_max = df_hist['AEP_MW'].max()
        else:
            hist_min, hist_max = 9580, 25700
            hist_avg = 15500

        # Demand profile checks and styling variables
        if prediction < low_cutoff:
            demand_level = "Low"
            demand_class = "demand-low"
            glow_color = "#34d399"
            pulse_speed = "2.5s"
        elif prediction > high_cutoff:
            demand_level = "High"
            demand_class = "demand-high"
            glow_color = "#f87171"
            pulse_speed = "1.0s"
        else:
            demand_level = "Medium"
            demand_class = "demand-medium"
            glow_color = "#fbbf24"
            pulse_speed = "1.8s"

        # Inject dynamic CSS variables based on prediction properties
        st.markdown(f"""
        <style>
            :root {{
                --glow-color: {glow_color} !important;
                --pulse-speed: {pulse_speed} !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        with col_dash:
            st.markdown("""
                <div class="glass-card glass-card-predicted" style="height: 100%;">
                    <h3 style="color:#a78bfa; margin-top:0px; font-weight:700; margin-bottom:1.5rem; display:flex; align-items:center; gap:8px;">
                        📺 Simulator Outputs Console
                    </h3>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center; margin-bottom: 1.5rem; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);">
                    <div class="metric-label">Simulated Grid Load</div>
                    <div class="metric-value">{prediction:,.1f} <span class="metric-unit">MW</span></div>
                    <div style="margin-top: 0.8rem;">
                        <span class="demand-badge {demand_class}">{demand_level} Demand Profile</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Plotly Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prediction,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Demand Gauge (MW)", 'font': {'size': 14, 'color': '#94a3b8', 'family': 'Outfit'}},
                gauge = {
                    'axis': {'range': [hist_min, hist_max], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                    'bar': {'color': glow_color, 'thickness': 0.25},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255,255,255,0.07)",
                    'steps': [
                        {'range': [hist_min, low_cutoff], 'color': 'rgba(16, 185, 129, 0.15)'},
                        {'range': [low_cutoff, high_cutoff], 'color': 'rgba(245, 158, 11, 0.15)'},
                        {'range': [high_cutoff, hist_max], 'color': 'rgba(239, 68, 68, 0.15)'}
                    ],
                    'threshold': {
                        'line': {'color': glow_color, 'width': 4},
                        'thickness': 0.75,
                        'value': prediction
                    }
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#f1f5f9", 'family': "Outfit"}, margin=dict(l=10, r=10, t=40, b=10), height=200)
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Plotly Bar Chart comparing prediction vs historical baseline
            if df_hist is not None:
                df_bar = pd.DataFrame({
                    'Metric': ['Min', 'Typical Avg', 'Model Output', 'Max'],
                    'Grid Load (MW)': [hist_min, hist_avg, prediction, hist_max]
                })
                
                fig_bar = px.bar(
                    df_bar, 
                    x='Metric', 
                    y='Grid Load (MW)',
                    color='Metric',
                    color_discrete_map={
                        'Min': '#475569',
                        'Typical Avg': '#6366f1',
                        'Model Output': glow_color,
                        'Max': '#ef4444'
                    },
                    text_auto=',.0f'
                )
                
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#94a3b8", 'family': "Outfit"},
                    showlegend=False,
                    margin=dict(l=10, r=10, t=30, b=10),
                    height=210,
                    xaxis={'title': '', 'showgrid': False},
                    yaxis={'title': 'Consumption (MW)', 'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.04)'}
                )
                
                fig_bar.update_traces(
                    textposition='outside',
                    textfont=dict(color='#f1f5f9', size=8),
                    marker=dict(line=dict(width=1, color='rgba(255,255,255,0.08)'))
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- SECTION: Common Visualizations & AI Insights -----------------
    if st.session_state['predict_mode'] == 'live':
        col_bar_l, col_ins_l = st.columns([1, 1.2])
        with col_bar_l:
            st.markdown("""
                <div class="glass-card" style="height: 100%;">
                    <h4 style="color:#fbbf24; margin-top:0px; font-weight:700; margin-bottom:1rem; font-size:1.1rem;">
                        📊 Comparison vs. Historical Bounds
                    </h4>
            """, unsafe_allow_html=True)
            if df_hist is not None:
                df_bar = pd.DataFrame({
                    'Metric': ['Min', 'Typical Avg', 'Model Output', 'Max'],
                    'Grid Load (MW)': [hist_min, hist_avg, prediction, hist_max]
                })
                fig_bar = px.bar(
                    df_bar, 
                    x='Metric', 
                    y='Grid Load (MW)',
                    color='Metric',
                    color_discrete_map={'Min': '#475569', 'Typical Avg': '#6366f1', 'Model Output': glow_color, 'Max': '#ef4444'},
                    text_auto=',.0f'
                )
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#94a3b8", 'family': "Outfit"}, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=210, xaxis={'title': '', 'showgrid': False}, yaxis={'title': 'Consumption (MW)', 'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.04)'})
                fig_bar.update_traces(textposition='outside', textfont=dict(color='#f1f5f9', size=8), marker=dict(line=dict(width=1, color='rgba(255,255,255,0.08)')))
                st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_ins_l:
            if df_hist is not None:
                diff_pct = ((prediction - hist_avg) / hist_avg) * 100
                direction = "above" if diff_pct > 0 else "below"
                color_class = "color: #f87171;" if diff_pct > 0 else "color: #34d399;"
                
                st.markdown(f"""
                    <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; padding: 1.5rem 2rem;">
                        <div class="metric-label">Historical Deviation Analysis</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #f1f5f9; margin-bottom: 0.4rem;">
                            {hist_avg:,.0f} MW <span style="font-size:0.9rem; color:#94a3b8; font-weight:400;">(Typical Average)</span>
                        </div>
                        <div style="font-size: 1.1rem; font-weight: 700; {color_class}">
                            {abs(diff_pct):.1f}% {direction} typical load bounds
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.8rem; margin-bottom: 0px; line-height: 1.45;">
                            This indicates that current meteorological forces are causing a {'surplus' if diff_pct > 0 else 'reduction'} in energy consumption patterns relative to typical weather states for this seasonal time window.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

    # ----------------- COGNITIVE AI INSIGHTS CARD -----------------
    st.markdown("""
        <div class="glass-card" style="margin-top: 1.5rem;">
            <h3 style="color:#fbbf24; margin-top:0px; font-weight:700; display:flex; align-items:center; gap:8px;">
                💡 Cognitive AI Insights
            </h3>
    """, unsafe_allow_html=True)

    # Generate AI summary text
    temp_insight = ""
    weather_insight = ""
    time_insight = ""

    if temp_val > 30:
        temp_insight = f"Thermal peaks ({temp_val:.1f}°C) trigger intensive cooling systems and grid-wide AC strains."
    elif temp_val < 5:
        temp_insight = f"Sub-zero weather ({temp_val:.1f}°C) causes heavy base load heating draws across utility grids."
    elif 15 <= temp_val <= 22:
        temp_insight = f"Temperatures in the mild zone ({temp_val:.1f}°C) provide thermal comfort, keeping grid heating/cooling loads at low baseline states."
    else:
        temp_insight = f"Moderate temperatures ({temp_val:.1f}°C) signify stable baseline grid loads."

    if weather_cond_val == "Sunny" and temp_val > 25:
        weather_insight = "Intense solar radiation creates greenhouse effects on commercial properties, increasing climate control loads."
    elif weather_cond_val == "Rainy":
        weather_insight = "Rainy conditions stimulate residential home occupancy and appliance usage, raising grid loads."
    elif weather_cond_val == "Cloudy":
        weather_insight = "Overcast skies minimize direct solar heating while limiting grid-connected solar power generation."

    if 7 <= hour_idx_val <= 9:
        time_insight = "This aligns with the morning grid wake-up curve (7 AM - 9 AM) as commercial loads begin."
    elif 17 <= hour_idx_val <= 21:
        time_insight = "This falls into the sharp residential evening peak (5 PM - 9 PM) as households activate appliances, entertainment, and HVAC systems."
    elif 0 <= hour_idx_val <= 5:
        time_insight = "This sits in the overnight grid valley (12 AM - 5 AM), the lowest baseload period."
    else:
        time_insight = "This aligns with standard daytime load curves."

    insight_text = f"<b>Prediction Rationale:</b> {temp_insight} {weather_insight} {time_insight}"

    if demand_level == "High":
        insight_text += f"<br/><br/><b>Grid Advice:</b> Since predicted consumption is <b>High ({prediction:,.0f} MW)</b>, grid dispatchers should stand by to activate auxiliary peaker plants or schedule energy imports from neighbouring zones to prevent power shortages."
    elif demand_level == "Low":
        insight_text += f"<br/><br/><b>Grid Advice:</b> Predicted load is <b>Low ({prediction:,.0f} MW)</b>. This provides a prime maintenance window for thermal generators or scheduling grid equipment inspections."
    else:
        insight_text += f"<br/><br/><b>Grid Advice:</b> Grid demand is in the <b>Normal range ({prediction:,.0f} MW)</b>. Normal operations are recommended. Renewable inputs should comfortably cover standard demand distributions."

    st.markdown(f"""
        <div class="insight-block">
            <div class="insight-title">⚡ Neural Inference Summary</div>
            <div style="font-size: 0.95rem; line-height: 1.6; color: #cbd5e1;">
                {insight_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- SECTION: Historical Grid Analytics -----------------
    st.markdown("""
        <div class="glass-card" style="margin-top: 1.5rem;">
            <h3 style="color:#fbbf24; margin-top:0px; font-weight:700; margin-bottom:0.5rem; display:flex; align-items:center; gap:8px;">
                📉 Historical Grid Analytics & Trends
            </h3>
            <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:1.5rem;">
                Deep-dive into the patterns extracted from 14 years of historical utility demand and climatic datasets.
            </p>
    """, unsafe_allow_html=True)

    if df_hist is not None:
        # Row 1: Two Columns for Temp vs Demand and Hourly Patterns
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("""
                <div style="background: rgba(15, 23, 42, 0.4); padding: 1.2rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.05); height: 120px; margin-bottom: 1rem;">
                    <h4 style="color:#f8fafc; font-weight:700; margin-top:0px; margin-bottom:0.3rem;">🌡️ Temperature vs. Demand</h4>
                    <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:0px; line-height: 1.4;">
                        Demonstrates the V-shaped thermal response curve: consumption peaks during hot summer cooling (AC) and cold winter heating.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.image(os.path.join(BASE_DIR, "dataset", "temp_vs_energy.png"), use_container_width=True)
            
        with col_g2:
            st.markdown("""
                <div style="background: rgba(15, 23, 42, 0.4); padding: 1.2rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.05); height: 120px; margin-bottom: 1rem;">
                    <h4 style="color:#f8fafc; font-weight:700; margin-top:0px; margin-bottom:0.3rem;">⏰ Hourly Consumption Patterns</h4>
                    <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:0px; line-height: 1.4;">
                        Identifies typical daily consumption curves, showing morning wake-up rises and high evening residential peaks across different weather states.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.image(os.path.join(BASE_DIR, "dataset", "hourly_consumption.png"), use_container_width=True)
            
        # Row 2: Full Width for Monthly Variations
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.4); padding: 1.2rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1rem;">
                <h4 style="color:#f8fafc; font-weight:700; margin-top:0px; margin-bottom:0.3rem;">📅 Monthly Variations & Seasonality</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:0px; line-height: 1.4;">
                    Visualizes monthly distribution medians. July/August (mid-summer) and December/January (mid-winter) represent utility peak seasons.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.image(os.path.join(BASE_DIR, "dataset", "monthly_consumption.png"), use_container_width=True)

    else:
        st.info("Historical data visualizations are not available.")

    st.markdown("</div>", unsafe_allow_html=True)
