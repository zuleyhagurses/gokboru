"""
Gökbörü: Görev Kontrol Merkezi
Streamlit Panosu — localhost:8000'de FastAPI arka ucu ile bağlantı
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Gökbörü | Görev Kontrol Merkezi",
    page_icon="🇹🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styling ──────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: #080c14 !important;
    color: #c8d8e8 !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #060a14 100%) !important;
    border-right: 1px solid #1a2a40 !important;
}
section[data-testid="stSidebar"] * {
    color: #8aa8c8 !important;
}
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    color: #4a8ab8 !important;
    text-transform: uppercase !important;
}

/* ── Slider accent ── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #0077ff) !important;
}

/* ── Main content ── */
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    background-color: #080c14 !important;
}

/* ── Header ── */
.launch-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #e0f0ff;
    text-transform: uppercase;
    border-bottom: 2px solid #1a3a60;
    padding-bottom: 0.4rem;
    margin-bottom: 0.2rem;
}
.launch-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.25em;
    color: #2a6a9a;
    text-transform: uppercase;
    margin-bottom: 1.8rem;
}

/* ── Status Banner ── */
.status-banner {
    border-radius: 6px;
    padding: 1.4rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.6rem;
    border-left: 6px solid;
}
.status-go {
    background: linear-gradient(135deg, #001a0a 0%, #002a12 100%);
    border-color: #00e676;
    box-shadow: 0 0 32px rgba(0,230,118,0.15), inset 0 0 60px rgba(0,230,118,0.04);
}
.status-conditional {
    background: linear-gradient(135deg, #1a1400 0%, #2a1e00 100%);
    border-color: #ffbb00;
    box-shadow: 0 0 32px rgba(255,187,0,0.15), inset 0 0 60px rgba(255,187,0,0.04);
}
.status-nogo {
    background: linear-gradient(135deg, #1a0000 0%, #2a0a08 100%);
    border-color: #ff3d3d;
    box-shadow: 0 0 32px rgba(255,61,61,0.15), inset 0 0 60px rgba(255,61,61,0.04);
}
.status-icon { font-size: 2.8rem; }
.status-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.status-go .status-label    { color: #00e676; }
.status-conditional .status-label { color: #ffbb00; }
.status-nogo .status-label  { color: #ff3d3d; }
.status-score {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    color: #4a7a9a;
    margin-top: 0.2rem;
}
.override-badge {
    margin-left: auto;
    background: rgba(255,61,61,0.12);
    border: 1px solid #ff3d3d;
    border-radius: 4px;
    padding: 0.3rem 0.8rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #ff6060;
    letter-spacing: 0.15em;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.3em;
    color: #2a5a7a;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 0.5rem;
    border-left: 3px solid #1a4a6a;
    padding-left: 0.6rem;
}

/* ── Metrics row ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.6rem;
}
.metric-card {
    background: linear-gradient(135deg, #0c1520 0%, #0a1018 100%);
    border: 1px solid #1a2a40;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #0077ff, transparent);
}
.metric-card-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #2a5a7a;
    text-transform: uppercase;
}
.metric-card-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    color: #00aaff;
    line-height: 1.1;
}
.metric-card-unit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #2a5a7a;
}

/* ── Log panel ── */
.log-panel {
    background: #060a10;
    border: 1px solid #1a2a40;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.9;
    color: #5a9a6a;
    margin-top: 0.5rem;
    min-height: 100px;
    white-space: pre-wrap;
    position: relative;
}
.log-panel::before {
    content: 'SİMÜLASYON KAYDI';
    position: absolute;
    top: -0.6rem; left: 1rem;
    background: #060a10;
    padding: 0 0.5rem;
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    color: #1a4a6a;
}

/* ── Error panel ── */
.error-panel {
    background: #120a0a;
    border: 1px solid #4a1a1a;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #cc4444;
    text-align: center;
    letter-spacing: 0.1em;
}

/* ── Sidebar divider ── */
.sidebar-section {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: #0a4a6a;
    text-transform: uppercase;
    padding: 0.5rem 0 0.3rem 0;
    border-top: 1px solid #0a1a2a;
    margin-top: 0.5rem;
}

/* ── Plotly containers ── */
.js-plotly-plot, .plotly {
    border-radius: 6px !important;
}

/* ── Override Streamlit button ── */
.stButton>button {
    background: linear-gradient(135deg, #0a2a4a, #0a1a2a) !important;
    border: 1px solid #1a4a7a !important;
    color: #60aadd !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}
.stButton>button:hover {
    border-color: #00aaff !important;
    color: #00ccff !important;
    box-shadow: 0 0 12px rgba(0,170,255,0.2) !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────

API_URL = "http://localhost:8000/api/v1/simulate-launch"
AI_API_URL = "http://localhost:8000/api/v1/ai-predict"
AI_METRICS_URL = "http://localhost:8000/api/v1/ai/metrics"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono, monospace", color="#4a7a9a", size=11),
)

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;'
        'font-weight:700;letter-spacing:0.18em;color:#60aadd;'
        'text-transform:uppercase;margin-bottom:0.2rem;">⚙ PARAMETRELER</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;'
        'letter-spacing:0.2em;color:#1a4a6a;margin-bottom:1rem;">MİSYON KONFİGÜRASYONU</div>',
        unsafe_allow_html=True,
    )

    site_name = st.text_input("SİTE ADI", value="Cape Canaveral LC-39A")

    # ── Meteorological ────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">🌤 METEOROLOJİ</div>', unsafe_allow_html=True)
    wind_speed    = st.slider("Rüzgar Hızı (knot)",       0.0,  60.0,  12.5, 0.5)
    wind_dir      = st.slider("Rüzgar Yönü (°)",         0.0, 360.0, 270.0, 1.0)
    humidity      = st.slider("Nem (%)",                 0.0, 100.0,  55.0, 1.0)
    cloud_cov     = st.slider("Bulut Örtüsü (%)",         0.0, 100.0,  20.0, 1.0)
    lightning     = st.slider("Yıldırım Olasılığı (%)",   0.0, 100.0,   5.0, 0.5)
    temperature   = st.slider("Sıcaklık (°C)",          -30.0,  55.0,  24.0, 0.5)

    # ── Geographic ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">🌍 COĞRAFİ</div>', unsafe_allow_html=True)
    latitude      = st.slider("Enlem (°)",               -90.0,  90.0,  28.5, 0.1)
    longitude     = st.slider("Boylam (°)",             -180.0, 180.0, -80.6, 0.1)
    dist_city     = st.slider("Şehre Uzaklık (km)",       0.0, 1000.0,  65.0, 5.0)
    elevation     = st.slider("Yükseklik (m)",           -500.0, 5000.0,   3.0, 10.0)

    # ── Logistic ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">📦 LOJİSTİK</div>', unsafe_allow_html=True)
    fuel          = st.slider("Yakıt Durumu (%)",         0.0, 100.0,  98.0, 1.0)
    infra         = st.slider("Altyapı Hazırlığı (%)",    0.0, 100.0, 95.0, 1.0)
    range_safety  = st.checkbox("Menzil Güvenliği Onaylı", value=True)
    crew          = st.slider("Mürettebat Hazırlığı (%)", 0.0, 100.0,  92.0, 1.0)
    supply        = st.slider("Tedarik Zinciri Endeksi (%)", 0.0, 100.0,  88.0, 1.0)

    # ── Environmental ─────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">🌱 ÇEVRESEL ETKİ</div>', unsafe_allow_html=True)
    noise_level   = st.slider("Gürültü Seviyesi (dB)",    0.0, 200.0,  140.0, 1.0)
    air_quality   = st.slider("Hava Kalitesi Endeksi",    0.0, 500.0,  80.0, 5.0)
    ecosystem_dist = st.slider("Koruma Alanına Uzaklık (km)", 0.0, 1000.0, 100.0, 10.0)
    water_risk    = st.slider("Su Kirliliği Riski (%)",   0.0, 100.0,  15.0, 1.0)
    carbon_emit   = st.slider("Karbon Emisyonu (kg CO2)", 0.0, 10000.0, 2500.0, 100.0)

    # ── Weights ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">⚖ PUAN AĞIRLIKLARI</div>', unsafe_allow_html=True)
    w_met = st.slider("Meteorolojik Ağırlık", 0.0, 1.0, 0.40, 0.05)
    w_geo = st.slider("Coğrafi Ağırlık",     0.0, 1.0, 0.30, 0.05)
    # Otomatik lojistik ağırlık hesapla
    w_log = round(max(0.0, min(1.0, round(1.0 - w_met - w_geo, 2))), 2)
    st.markdown(
        '<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;'
        f'color:#1a5a3a;letter-spacing:0.1em;">LOJİSTİK AĞIRLIK (OTOMATİK): {w_log:.2f}</div>',
        unsafe_allow_html=True
    )

# ─── Build request payload ────────────────────────────────────────────────────

payload = {
    "site_name": site_name,
    "meteorological": {
        "wind_speed_knots": wind_speed,
        "wind_direction_deg": wind_dir,
        "humidity_percent": humidity,
        "cloud_coverage_percent": cloud_cov,
        "lightning_probability_percent": lightning,
        "temperature_celsius": temperature,
    },
    "geographic": {
        "latitude_deg": latitude,
        "longitude_deg": longitude,
        "distance_to_nearest_city_km": dist_city,
        "elevation_m": elevation,
    },
    "logistic": {
        "fuel_availability_percent": fuel,
        "infrastructure_readiness_percent": infra,
        "range_safety_cleared": range_safety,
        "crew_readiness_percent": crew,
        "supply_chain_index": supply,
    },
    "environmental": {
        "noise_level_db": noise_level,
        "air_quality_index": air_quality,
        "ecosystem_proximity_km": ecosystem_dist,
        "water_contamination_risk": water_risk,
        "carbon_footprint_kg": carbon_emit,
    },
    "weights": {
        "meteorological": w_met,
        "geographic": w_geo,
        "logistic": w_log,
    },
}

# ─── Call backend ─────────────────────────────────────────────────────────────

data = None
error_msg = None

# Validate weights first
if abs(w_met + w_geo + w_log - 1.0) > 0.05:
    error_msg = "⚠ AĞIRLIK TOPLAM HATASI — Meteorolojik + Coğrafi ağırlıkları ≤ 1.0 olmalı"
else:
    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
        else:
            error_msg = f"BACKEND ERROR [{resp.status_code}]: {resp.text[:300]}"
    except requests.exceptions.ConnectionError:
        error_msg = (
            "CONNECTION REFUSED — Backend is not running.\n"
            "Start it with:  uvicorn app.main:app --reload --port 8000"
        )
    except requests.exceptions.Timeout:
        error_msg = "TIMEOUT — Backend took too long to respond."
    except Exception as exc:
        error_msg = f"UNEXPECTED ERROR: {str(exc)}"
ai_prediction = None
ai_metrics = None
ai_warning = None

if data is not None:
    try:
        ai_resp = requests.post(AI_API_URL, json=payload, timeout=5)
        if ai_resp.status_code == 200:
            ai_prediction = ai_resp.json().get("predicted_status")
        else:
            ai_warning = f"AI tahmini alınamadı: {ai_resp.status_code}"
    except requests.exceptions.RequestException:
        ai_warning = "AI servisine bağlanamadı. Model eğitilmiş olmayabilir."

    try:
        metrics_resp = requests.get(AI_METRICS_URL, timeout=5)
        if metrics_resp.status_code == 200:
            ai_metrics = metrics_resp.json()
    except requests.exceptions.RequestException:
        pass
# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown('<div class="launch-header">🇹🇷 Gökbörü</div>', unsafe_allow_html=True)
st.markdown('<div class="launch-subtitle">Görev Kontrol Merkezi  //  Fırlatma Karar Destek Sistemi</div>',
            unsafe_allow_html=True)

# ─── Error State ──────────────────────────────────────────────────────────────

if error_msg:
    st.markdown(f'<div class="error-panel">⚠&nbsp;&nbsp;{error_msg}</div>', unsafe_allow_html=True)
    st.stop()

# ─── Extract data ─────────────────────────────────────────────────────────────

score       = data["launch_readiness_score"]
status      = data["status"]
rec         = data["recommendation"]
override    = data["safety_override"]
met_score   = data["meteorological_breakdown"]["normalized_score"]
geo_score   = data["geographic_breakdown"]["normalized_score"]
log_score   = data["logistic_breakdown"]["normalized_score"]
env_score   = data["environmental_breakdown"]["normalized_score"]
rot_vel     = data["geographic_breakdown"]["rotational_velocity_boost_ms"]
sim_id      = data["simulation_id"]
timestamp   = data["timestamp"]

# ─── Status Banner ────────────────────────────────────────────────────────────

STATUS_META = {
    "GO":          ("status-go",          "✅",  "FIRLATMA ONAYLANDI"),
    "CONDITIONAL": ("status-conditional", "⚠️",  "KOŞULLU ONAY"),
    "NO-GO":       ("status-nogo",        "🚫", "İPTAL - HAYIR"),
}
css_cls, icon, label = STATUS_META[status]
override_html = (
    '<span class="override-badge">⚡ SAFETY OVERRIDE ACTIVE</span>'
    if override["triggered"] else ""
)

ai_panel = ""
if ai_prediction:
    ai_panel = (
        f"<div style='margin-top:0.8rem;padding:0.9rem 1rem;background:#081316;"
        f"border:1px solid #0f2a40;border-radius:6px;color:#a8d6ff;'>"
        f"<strong>AI Tahmini:</strong> {ai_prediction}"
        f"</div>"
    )
elif ai_warning:
    ai_panel = (
        f"<div style='margin-top:0.8rem;padding:0.9rem 1rem;background:#110a0a;"
        f"border:1px solid #4a1a1a;border-radius:6px;color:#ffcfb8;'>"
        f"<strong>{ai_warning}</strong>"
        f"</div>"
    )

st.markdown(f"""
<div class="status-banner {css_cls}">
    <div class="status-icon">{icon}</div>
    <div>
        <div class="status-label">{label}</div>
        <div class="status-score">
            HAZIRLIK PUANI: {score:.2f} / 100 &nbsp;|&nbsp;
            SIM KİMLİĞİ: {sim_id[:8].upper()} &nbsp;|&nbsp;
            {datetime.fromisoformat(timestamp.replace('Z','')) .strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>
    {override_html}
</div>
""", unsafe_allow_html=True)

if ai_panel:
    st.markdown(ai_panel, unsafe_allow_html=True)

if ai_metrics is not None:
    st.markdown('<div class="section-title" style="margin-top:1rem;">AI MODEL PERFORMANSI</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='log-panel'>"
        f"<strong>Doğruluk:</strong> {ai_metrics['accuracy']:.4f}<br>"
        f"<strong>Model:</strong> {ai_metrics['ai_model_path']}<br>"
        f"<strong>Dataset:</strong> {ai_metrics['ai_dataset_path']}<br><br>"
        f"<pre style='white-space:pre-wrap; font-family:Share Tech Mono, monospace; font-size:0.75rem;'>"
        f"{ai_metrics['report']}"
        f"</pre>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ─── Metric Cards ─────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">ALT SİSTEM PUANLARI</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

def metric_card(col, label, value, unit="/ 100"):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-label">{label}</div>
        <div class="metric-card-value">{value:.1f}<span class="metric-card-unit"> {unit}</span></div>
    </div>""", unsafe_allow_html=True)

metric_card(c1, "🌤 METEOROLOJİ", met_score)
metric_card(c2, "🌍 COĞRAFİ", geo_score)
metric_card(c3, "📦 LOJİSTİK", log_score)
metric_card(c4, "🌱 ÇEVRE", env_score)
c5.markdown(f"""
<div class="metric-card">
    <div class="metric-card-label">🌀 ROTASYONEL</div>
    <div class="metric-card-value">{rot_vel:.1f}<span class="metric-card-unit"> m/s</span></div>
</div>""", unsafe_allow_html=True)

# ─── Charts ───────────────────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:1.4rem;">TELEMETRY ANALYSIS</div>',
            unsafe_allow_html=True)

col_gauge, col_radar = st.columns([1, 1])

# ── Gauge Chart ───────────────────────────────────────────────────────────────
with col_gauge:
    needle_color = "#00e676" if status == "GO" else ("#ffbb00" if status == "CONDITIONAL" else "#ff3d3d")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 75, "valueformat": ".1f",
               "font": {"family": "Share Tech Mono", "size": 13},
               "increasing": {"color": "#00e676"},
               "decreasing": {"color": "#ff3d3d"}},
        number={"font": {"family": "Rajdhani", "size": 52, "color": "#e0f0ff"},
                "suffix": "", "valueformat": ".1f"},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#1a3a60",
                "tickvals": [0, 25, 50, 75, 100],
                "ticktext": ["0", "25", "50", "75", "100"],
                "tickfont": {"family": "Share Tech Mono", "size": 10, "color": "#2a5a7a"},
            },
            "bar": {"color": needle_color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50], "color": "rgba(255,61,61,0.10)"},
                {"range": [50, 75], "color": "rgba(255,187,0,0.10)"},
                {"range": [75,100], "color": "rgba(0,230,118,0.10)"},
            ],
            "threshold": {
                "line": {"color": "#ffffff", "width": 2},
                "thickness": 0.85,
                "value": score,
            },
        },
        title={"text": "FIRLATMA HAZIRLIK PUANI",
               "font": {"family": "Share Tech Mono", "size": 11, "color": "#2a5a7a"}},
    ))
    gauge.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        margin=dict(l=30, r=30, t=60, b=10),
    )
    st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

# ── Radar Chart ───────────────────────────────────────────────────────────────
with col_radar:
    categories = ["METEOROLOJİ", "COĞRAFİ", "LOJİSTİK", "ÇEVRE", "METEOROLOJİ"]
    values = [met_score, geo_score, log_score, env_score, met_score]

    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        name="Mevcut Misyon",
        line=dict(color="#00aaff", width=2),
        fillcolor="rgba(0,170,255,0.10)",
        marker=dict(size=7, color="#00ccff",
                    line=dict(color="#ffffff", width=1)),
    ))
    # Reference "ideal" ring at 80
    radar.add_trace(go.Scatterpolar(
        r=[80, 80, 80, 80, 80],
        theta=categories,
        fill="toself",
        name="Hedef (80)",
        line=dict(color="#2a5a4a", width=1, dash="dot"),
        fillcolor="rgba(0,150,80,0.04)",
        marker=dict(size=0),
    ))
    radar.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(family="Share Tech Mono", size=9, color="#1a4a6a"),
                gridcolor="#0a1e34",
                linecolor="#0a1e34",
                tickvals=[0, 25, 50, 75, 100],
            ),
            angularaxis=dict(
                tickfont=dict(family="Share Tech Mono", size=10, color="#3a7aaa"),
                gridcolor="#0a1e34",
                linecolor="#0a2040",
            ),
        ),
        legend=dict(
            font=dict(family="Share Tech Mono", size=9, color="#2a5a7a"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        title=dict(
            text="ALAN PUANI KARŞILAŞTIRMASI",
            font=dict(family="Share Tech Mono", size=11, color="#2a5a7a"),
        ),
        margin=dict(l=40, r=40, t=60, b=20),
    )
    st.plotly_chart(radar, use_container_width=True, config={"displayModeBar": False})

# ─── Detailed Breakdown Bar Chart ─────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:0.5rem;">BİLEŞEN ANALİZİ</div>',
            unsafe_allow_html=True)

met_bd  = data["meteorological_breakdown"]
geo_bd  = data["geographic_breakdown"]
log_bd  = data["logistic_breakdown"]
env_bd  = data["environmental_breakdown"]

bar_labels = [
    "Rüzgar", "Nem", "Bulut Örtüsü", "Yıldırım", "Sıcaklık",
    "Hız Artışı", "Güvenlik Mesafesi", "Yükseklik",
    "Yakıt", "Altyapı", "Menzil Güvenliği", "Mürettebat", "Tedarik Zinciri",
    "Gürültü", "Hava Kalitesi", "Ekosistem", "Su Kirliliği", "Karbon",
]
bar_values = [
    met_bd["raw_wind_score"],
    met_bd["raw_humidity_score"],
    met_bd["raw_cloud_score"],
    met_bd["raw_lightning_penalty"],
    met_bd["raw_temperature_score"],
    geo_bd["velocity_score"],
    geo_bd["safety_distance_score"],
    geo_bd["elevation_score"],
    log_bd["fuel_score"],
    log_bd["infrastructure_score"],
    log_bd["range_safety_score"],
    log_bd["crew_score"],
    log_bd["supply_chain_score"],
    env_bd["noise_score"],
    env_bd["air_quality_score"],
    env_bd["ecosystem_score"],
    env_bd["water_contamination_score"],
    env_bd["carbon_footprint_score"],
]
bar_groups = (
    ["Meteorolojik"] * 5 +
    ["Coğrafi"] * 3 +
    ["Lojistik"] * 5 +
    ["Çevresel"] * 5
)
color_map = {
    "Meteorolojik": "#00aaff",
    "Coğrafi":     "#00e6b0",
    "Lojistik":       "#ffaa00",
    "Çevresel":      "#90ee90",
}
bar_colors = [color_map[g] for g in bar_groups]

bar_fig = go.Figure(go.Bar(
    x=bar_labels,
    y=bar_values,
    marker=dict(
        color=bar_colors,
        line=dict(color="rgba(255,255,255,0.05)", width=1),
        opacity=0.85,
    ),
    text=[f"{v:.1f}" for v in bar_values],
    textposition="outside",
    textfont=dict(family="Share Tech Mono", size=9, color="#4a7a9a"),
    hovertemplate="<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>",
))
bar_fig.add_hline(
    y=75, line_dash="dot", line_color="rgba(0,230,118,0.4)", line_width=1,
    annotation_text="GO threshold", annotation_font_size=9,
    annotation_font_color="#2a7a4a",
)
bar_fig.add_hline(
    y=50, line_dash="dot", line_color="rgba(255,187,0,0.35)", line_width=1,
    annotation_text="CONDITIONAL threshold", annotation_font_size=9,
    annotation_font_color="#7a6a1a",
)
bar_fig.update_layout(
    **PLOTLY_LAYOUT,
    height=300,
    yaxis=dict(range=[0, 115], gridcolor="#0a1a2a", linecolor="#0a1e34",
               tickfont=dict(family="Share Tech Mono", size=9)),
    xaxis=dict(tickfont=dict(family="Share Tech Mono", size=9, color="#3a6a8a"),
               linecolor="#0a1e34"),
    showlegend=False,
    title=dict(text="TÜM BİLEŞEN PUANLARI",
               font=dict(family="Share Tech Mono", size=11, color="#2a5a7a")),
    bargap=0.35,
    margin=dict(l=20, r=20, t=50, b=60),
)
st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

# ─── Simülasyon Kaydı ───────────────────────────────────────────────────────

st.markdown('<div class="section-title" style="margin-top:1rem;">SİMÜLASYON KAYDI</div>',
            unsafe_allow_html=True)

override_line = ""
if override["triggered"]:
    override_line = f"\n[GÜVENLIK ÖNCESİ]  {override['reason']}\n"

log_text = (
    f"[{datetime.fromisoformat(timestamp.replace('Z','')).strftime('%Y-%m-%d %H:%M:%S')} UTC]  "
    f"SIM_KİMLİĞİ={sim_id.upper()}\n"
    f"SİTE: {data['site_name']}\n"
    f"AĞIRLLIKLAR: MET={w_met:.2f}  COĞ={w_geo:.2f}  LOJ={w_log:.2f}\n"
    f"{override_line}"
    f"\n{rec}\n\n"
    f"MET_PUANI={met_score:.2f}   COĞ_PUANI={geo_score:.2f}   LOJ_PUANI={log_score:.2f}   ÇEVRE_PUANI={env_score:.2f}\n"
    f"BİLEŞİK_PUAN={score:.4f}   DURUM={status}"
)

st.markdown(f'<div class="log-panel">{log_text}</div>', unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-top:2.5rem;padding-top:1rem;border-top:1px solid #0a1a2a;
     font-family:Share Tech Mono,monospace;font-size:0.62rem;
     letter-spacing:0.2em;color:#0a2a3a;text-align:center;">
    GÖKBÖRÜ v1.0.0  //  GÖREV KONTROL SİSTEMİ  //  TÜM HAKLARI SAKLIDIR
</div>
""", unsafe_allow_html=True)