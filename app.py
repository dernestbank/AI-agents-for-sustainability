import os
import json
import time
import tempfile
import shutil
from io import BytesIO
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

#bootstrap
load_dotenv()
os.makedirs("data", exist_ok=True)

st.set_page_config(
    page_title="A4S",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "data/emissions.json"
REQUIRED_COLUMNS = ["date", "scope", "category", "activity", "quantity", "unit", "emission_factor"]
ALLOWED_SCOPES = ["Scope 1", "Scope 2", "Scope 3"]

#session state
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"
if "emissions_data" not in st.session_state:
    try:
        raw = open(DATA_PATH, "r", encoding="utf-8").read().strip() if os.path.exists(DATA_PATH) else "[]"
        st.session_state.emissions_data = pd.DataFrame(json.loads(raw or "[]"))
    except Exception:
        try:
            shutil.copy(DATA_PATH, f"data/emissions_backup_{int(time.time())}.json")
        except Exception:
            pass
        st.session_state.emissions_data = pd.DataFrame()

#styling
PROD_CSS = """
:root {
  --bg: #0a0e13;
  --elev: #141920;
  --elev-hover: #1a2230;
  --fg: #f0f4f8;
  --muted: #8b9dad;
  --primary: #4ade80;
  --primary-hover: #65e899;
  --primary-dark: #22c55e;
  --border: #1e2734;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --gradient: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
}

/* Reset & Base */
* { margin: 0; padding: 0; box-sizing: border-box; }
#MainMenu, footer { display: none; }
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: var(--fg);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

section.main .block-container {
  padding: 2rem 2.5rem;
  max-width: 1600px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #283041; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--bg);
  border-right: 1px solid var(--border);
  padding: 1.5rem;
}

[data-testid="stSidebar"] .stRadio label {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stRadio label:hover {
  background: var(--elev);
}

/* Typography */
h1 { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
h2 { font-size: 1.875rem; font-weight: 700; letter-spacing: -0.01em; margin: 2rem 0 1rem 0; }
h3 { font-size: 1.5rem; font-weight: 600; margin: 1.5rem 0 0.75rem 0; }
h4 { font-size: 1.125rem; font-weight: 600; margin: 1rem 0 0.5rem 0; }
h5 { font-size: 1rem; font-weight: 600; }
h1, h2, h3, h4, h5 { color: var(--fg); }

/* Professional Cards */
.stCard {
  background: var(--elev);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced Metric Cards */
.metric-card {
  background: var(--elev);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.3);
  border-color: var(--primary);
}

.metric-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient);
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--fg);
  line-height: 1.2;
}

/* Premium Buttons */
.stButton>button, button[data-kind="primary"] {
  background: var(--gradient) !important;
  color: #0a0e13 !important;
  border: none !important;
  border-radius: 10px;
  padding: 0.75rem 1.5rem;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(74, 222, 128, 0.2);
}

.stButton>button:hover, button[data-kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(74, 222, 128, 0.3);
  filter: brightness(1.05);
}

.stButton>button:active, button[data-kind="primary"]:active {
  transform: translateY(0);
}

/* Override Streamlit's primary button color */
button[kind="primary"] {
  background: var(--gradient) !important;
  color: #0a0e13 !important;
}

/* Secondary Button */
button[kind="secondary"] {
  background: var(--elev) !important;
  color: var(--fg) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}

button[kind="secondary"]:hover {
  background: var(--elev-hover) !important;
  transform: translateY(-1px);
}

/* Premium Inputs */
.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input,
.stDateInput>div>div>input {
  background: var(--elev) !important;
  color: var(--fg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 0.625rem 0.875rem !important;
  font-size: 0.95rem !important;
  transition: all 0.2s ease !important;
}

.stTextInput>div>div>input:hover,
.stTextArea textarea:hover,
.stSelectbox>div>div:hover,
.stNumberInput>div>div>input:hover,
.stDateInput>div>div>input:hover {
  border-color: var(--primary) !important;
  background: var(--elev-hover) !important;
}

.stTextInput>div>div>input:focus,
.stTextArea textarea:focus,
.stNumberInput>div>div>input:focus,
.stDateInput>div>div>input:focus,
.stSelectbox>div>div:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.15) !important;
  outline: none !important;
}

/* Premium Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--elev);
  border-radius: 10px;
  padding: 0.5rem;
  gap: 0.5rem;
  border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  padding: 0.625rem 1.25rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
  background: var(--gradient) !important;
  color: #0a0e13 !important;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(74, 222, 128, 0.2);
}

.stTabs [aria-selected="false"] {
  color: var(--muted);
}

.stTabs [aria-selected="false"]:hover {
  background: var(--elev-hover);
  color: var(--fg);
}

/* Enhanced Tables */
.dataframe, .stDataFrame {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--elev);
}

.dataframe thead {
  background: var(--elev-hover);
}

.dataframe tbody tr:hover {
  background: var(--elev-hover);
}

/* Info Messages */
.stAlert {
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 1rem 1.25rem;
}

/* File Uploader */
.stFileUploader {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 2rem;
  background: var(--elev);
  transition: all 0.2s ease;
}

.stFileUploader:hover {
  border-color: var(--primary);
  background: var(--elev-hover);
}

/* Radio & Checkbox */
.stRadio label,
.stCheckbox label {
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

/* Footer */
.app-footer {
  text-align: center;
  color: var(--muted);
  font-size: 0.75rem;
  padding: 2rem 0 1rem 0;
  font-weight: 500;
}

/* Section Dividers */
hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}

/* Success/Error States */
.stSuccess {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--success);
  color: var(--success);
}

.stError {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--danger);
  color: var(--danger);
}

.stWarning {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--warning);
  color: var(--warning);
}

/* Loading States */
.stSpinner>div {
  border-color: var(--primary);
}

/* Form Enhancements */
.stForm {
  padding: 1.5rem 0;
}

/* Caption Styling */
.stMarkdown>small {
  color: var(--muted);
  font-size: 0.875rem;
}

/* Container Spacing */
div[data-testid="stVerticalBlock"] {
  gap: 1rem;
}

/* Badge/Label Styles */
.caption-text {
  color: var(--muted);
  font-size: 0.875rem;
  font-weight: 500;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stCard, .metric-card {
  animation: fadeIn 0.5s ease-out;
}

/* Enhanced selectbox */
.stSelectbox [data-baseweb="select"] {
  background: var(--elev) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 8px !important;
}

.stSelectbox:hover [data-baseweb="select"] {
  border-color: var(--primary) !important;
  background: var(--elev-hover) !important;
}

/* Slider styling */
.stSlider {
  padding: 1rem 0;
}

.stSlider [data-baseweb="slider"] {
  color: var(--primary);
}

/* Date input styling */
.stDateInput>div>div>input:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.15) !important;
}

/* Enhanced dividers */
.stDivider {
  border-color: var(--border);
  margin: 2rem 0;
}

/* Better spacing for sections */
section.main > div > div {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

/* Loading states enhancement */
.stSpinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

/* Info box styling */
.stInfo {
  background: rgba(74, 222, 128, 0.08);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: var(--primary);
  border-radius: 12px;
  padding: 1.25rem;
}

.stWarning {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: var(--warning);
}

.stError {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--danger);
}

.stSuccess {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--success);
}
"""
st.markdown(f"<style>{PROD_CSS}</style>", unsafe_allow_html=True)

#plot helpers
def darkify(fig):
    # Professional color palette
    colors = ['#4ade80', '#22c55e', '#10b981', '#34d399', '#6ee7b7', '#86efac']
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(color="#f0f4f8", size=12, family="Inter"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(color="#8b9dad")
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
        colorway=colors,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="#141920",
            bordercolor="#1e2734",
            font_size=12,
            font_family="Inter"
        )
    )
    return fig

#persistence
def atomic_save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = json.dumps(obj, indent=2, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="emissions_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(path):
            ts = int(time.time())
            shutil.copy(path, f"{path}.bak.{ts}")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass


def persist_dataframe(df: pd.DataFrame) -> bool:
    try:
        atomic_save_json(DATA_PATH, df.to_dict(orient="records"))
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

#helpers
@st.cache_data(ttl=120)
def scope_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "emissions_kgCO2e" not in df.columns:
        return pd.DataFrame(columns=["scope", "emissions_kgCO2e"])
    g = df.groupby("scope", as_index=False)["emissions_kgCO2e"].sum()
    return g.sort_values("emissions_kgCO2e", ascending=False)


def download_csv(df: pd.DataFrame) -> BytesIO:
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf

#header / topbar
st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

#sidebar
with st.sidebar:
    st.markdown(
        """
        <div style='padding: 1.5rem 0; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;'>
            <div style='font-weight: 800; font-size: 24px; letter-spacing: -0.02em; margin-bottom: 0.5rem; background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>A4S</div>
            <div style='color: var(--muted); font-size: 0.875rem; font-weight: 500;'>Carbon Accounting Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation", unsafe_allow_html=True)
    
    nav = st.radio(
        "",
        ["Dashboard", "Data Entry", "Settings", "AI Insights"],
        captions=[
            "Overview and analytics",
            "Add emissions data",
            "Company settings",
            "AI-powered insights",
        ],
        index=["Dashboard", "Data Entry", "Settings", "AI Insights"].index(st.session_state.active_page),
        label_visibility="collapsed"
    )
    if nav != st.session_state.active_page:
        st.session_state.active_page = nav
        st.rerun()

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class='app-footer'>
          © 2025 ProcEm Engine<br>
          <span style='font-size: 11px; opacity: 0.7;'>AI-Powered Sustainability Platform</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

#pages
if st.session_state.active_page == "Dashboard":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.25rem;'>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--muted); font-size: 1.125rem; margin-bottom: 2rem;'>Monitor your carbon footprint and track emissions analytics</p>", unsafe_allow_html=True)

    df = st.session_state.emissions_data.copy()
    if df.empty:
        st.markdown(
            """
            <div class='stCard' style='text-align: center; padding: 3rem; background: linear-gradient(135deg, rgba(74, 222, 128, 0.05) 0%, rgba(34, 197, 94, 0.05) 100%); border: 2px dashed var(--border);'>
                <h3 style='color: var(--primary); margin-bottom: 0.75rem;'>Welcome to A4S</h3>
                <p style='color: var(--muted); margin-bottom: 1.5rem; font-size: 1rem;'>Start by adding emissions data or uploading a CSV file</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if "emissions_kgCO2e" in df.columns:
            df["emissions_kgCO2e"] = pd.to_numeric(df["emissions_kgCO2e"], errors="coerce").fillna(0)
        total = float(df.get("emissions_kgCO2e", pd.Series([0])).sum())

        # Metrics Row with improved spacing
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3, gap="medium")
        with m1:
            st.markdown("<div class='metric-card'><div class='metric-accent'></div>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Total Emissions</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{total:,.2f}<span style='font-size: 1.25rem; opacity: 0.8;'> kgCO2e</span></div></div>", unsafe_allow_html=True)
        with m2:
            latest = "—"
            if "date" in df.columns and not df["date"].isna().all():
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                d = df["date"].max()
                latest = d.strftime("%Y-%m-%d") if pd.notna(d) else "—"
            st.markdown("<div class='metric-card'><div class='metric-accent'></div>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Latest Entry</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value' style='font-size: 1.5rem;'>{latest}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown("<div class='metric-card'><div class='metric-accent'></div>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Total Entries</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{len(df):,}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

        # Charts Section
        st.markdown("<h2 style='font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1.5rem 0; color: var(--fg);'>Analytics Overview</h2>", unsafe_allow_html=True)
        
        # Scope Breakdown Chart - Full Width
        st.markdown("<div class='stCard'><h3 style='margin-top: 0; margin-bottom: 1rem; color: var(--primary);'>Emissions by Scope</h3>", unsafe_allow_html=True)
        if total > 0 and "scope" in df.columns:
            sb = scope_breakdown(df)
            if not sb.empty:
                fig1 = px.pie(sb, values="emissions_kgCO2e", names="scope", hole=.45)
                darkify(fig1)
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No scope data available.")
        else:
            st.info("No emissions recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Category and Time Series - Side by Side
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='stCard'><h3 style='margin-top: 0; margin-bottom: 1rem; color: var(--primary);'>Emissions by Category</h3>", unsafe_allow_html=True)
            if total > 0 and "category" in df.columns:
                cat = df.groupby("category")["emissions_kgCO2e"].sum().reset_index().sort_values("emissions_kgCO2e", ascending=False)
                if not cat.empty:
                    fig2 = px.bar(cat, x="category", y="emissions_kgCO2e", labels={"emissions_kgCO2e": "kgCO2e", "category": "Category"})
                    darkify(fig2)
                    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("No category data available.")
            else:
                st.info("No emissions recorded yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='stCard'><h3 style='margin-top: 0; margin-bottom: 1rem; color: var(--primary);'>Emissions Over Time</h3>", unsafe_allow_html=True)
            if total > 0 and "date" in df.columns:
                tdf = df.copy()
                tdf["date"] = pd.to_datetime(tdf["date"], errors="coerce")
                tdf = tdf.dropna(subset=["date"])
                if not tdf.empty:
                    tdf["month"] = tdf["date"].dt.to_period("M").astype(str)
                    ts = tdf.groupby(["month", "scope"])["emissions_kgCO2e"].sum().reset_index()
                    if not ts.empty:
                        fig3 = px.line(ts, x="month", y="emissions_kgCO2e", color="scope", markers=True,
                                       labels={"month": "Month", "emissions_kgCO2e": "kgCO2e"})
                        darkify(fig3)
                        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info("Not enough data to plot time series.")
                else:
                    st.info("No valid dates found.")
            else:
                st.info("No emissions recorded yet.")
            st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_page == "Data Entry":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.25rem;'>Data Entry</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--muted); font-size: 1.125rem; margin-bottom: 2rem;'>Add new emissions data or upload CSV files</p>", unsafe_allow_html=True)
    tabs = st.tabs(["Manual Entry", "CSV Upload"])

    # Manual entry
    with tabs[0]:
        st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.5rem;'>Add New Emission Entry</h3>", unsafe_allow_html=True)
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        with st.form("emission_form", border=False):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown("<h4 style='color: var(--primary); font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);'>Basic Information</h4>", unsafe_allow_html=True)
                date = st.date_input("Date", datetime.now())
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                scope = st.selectbox("Scope", ALLOWED_SCOPES)
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                category = st.text_input("Category")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                activity = st.text_input("Activity", placeholder="e.g., Office Electricity, Company Vehicle")
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                
                st.markdown("<h4 style='color: var(--primary); font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);'>Location Details</h4>", unsafe_allow_html=True)
                country = st.text_input("Country/Region", placeholder="e.g., US, UK, IN")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                facility = st.text_input("Facility/Location", placeholder="e.g., HQ, Plant 2")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                responsible = st.text_input("Responsible Person", placeholder="Name of owner")
                
            with col2:
                st.markdown("<h4 style='color: var(--primary); font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);'>Emission Calculation</h4>", unsafe_allow_html=True)
                quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                unit = st.text_input("Unit", placeholder="e.g., kWh, liter, km")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                st.caption("Provide an emission factor in kgCO2e per unit.")
                emission_factor = st.number_input("Emission Factor (kgCO2e/unit)", min_value=0.0, value=0.0, format="%.4f")
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                
                st.markdown("<h4 style='color: var(--primary); font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);'>Quality & Verification</h4>", unsafe_allow_html=True)
                data_quality = st.select_slider("Data Quality", options=["Low", "Medium", "High"], value="Medium")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                verification_status = st.selectbox("Verification Status", ["Unverified", "Internally Verified", "Third-Party Verified"])
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                notes = st.text_area("Notes", placeholder="Data source, methodology, assumptions…", height=100)

            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            cta1, cta2 = st.columns([1, 1])
            with cta1:
                submitted = st.form_submit_button("Add Entry", type="primary", use_container_width=True)
            with cta2:
                _ = st.form_submit_button("Clear Form", type="secondary", use_container_width=True)

            if submitted:
                if quantity <= 0:
                    st.error("Quantity must be greater than zero.")
                elif not unit.strip():
                    st.error("Unit is required.")
                elif scope not in ALLOWED_SCOPES:
                    st.error("Invalid scope.")
                else:
                    try:
                        emissions = float(quantity) * float(emission_factor)
                        new_row = pd.DataFrame([{
                            "date": date.strftime("%Y-%m-%d"),
                            "scope": scope,
                            "category": category,
                            "activity": activity,
                            "quantity": float(quantity),
                            "unit": unit,
                            "emission_factor": float(emission_factor),
                            "emissions_kgCO2e": emissions,
                            "country": country,
                            "facility": facility,
                            "responsible_person": responsible,
                            "data_quality": data_quality,
                            "verification_status": verification_status,
                            "notes": notes,
                        }])
                        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_row], ignore_index=True)
                        if persist_dataframe(st.session_state.emissions_data):
                            st.success("Entry added successfully.")
                            st.session_state.active_page = "Dashboard"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error adding entry: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
        
        if not st.session_state.emissions_data.empty:
            st.markdown("<h3>Existing Emissions Data</h3>", unsafe_allow_html=True)
            st.markdown("<div class='stCard'>", unsafe_allow_html=True)
            st.dataframe(st.session_state.emissions_data, use_container_width=True, hide_index=False)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            d1, d2 = st.columns([3, 1])
            with d1:
                buf = download_csv(st.session_state.emissions_data)
                st.download_button("Download current CSV", data=buf, file_name="emissions_export.csv", mime="text/csv")
            with d2:
                idx = st.number_input("Row index", min_value=0, max_value=len(st.session_state.emissions_data)-1, step=1)
                if st.button("Delete", type="primary"):
                    try:
                        st.session_state.emissions_data = st.session_state.emissions_data.drop(int(idx)).reset_index(drop=True)
                        if persist_dataframe(st.session_state.emissions_data):
                            st.success(f"Deleted row {idx}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

    # CSV Upload
    with tabs[1]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Upload CSV File</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Upload a CSV file with your emissions data. The file must contain the required columns.</p>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded is not None:
            max_mb = 5
            size_ok = getattr(uploaded, "size", 0) <= max_mb * 1024 * 1024
            if not size_ok:
                st.error(f"File too large. Limit is {max_mb} MB.")
            else:
                try:
                    dfu = pd.read_csv(uploaded)
                    missing = [c for c in REQUIRED_COLUMNS if c not in dfu.columns]
                    if missing:
                        st.error(f"CSV must contain columns: {', '.join(REQUIRED_COLUMNS)}")
                    else:
                        dfu["quantity"] = pd.to_numeric(dfu["quantity"], errors="coerce")
                        dfu["emission_factor"] = pd.to_numeric(dfu["emission_factor"], errors="coerce")
                        dfu["date"] = pd.to_datetime(dfu["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                        if "emissions_kgCO2e" not in dfu.columns:
                            dfu["emissions_kgCO2e"] = (dfu["quantity"].fillna(0) * dfu["emission_factor"].fillna(0)).clip(lower=0)
                        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, dfu], ignore_index=True)
                        if persist_dataframe(st.session_state.emissions_data):
                            st.success("CSV uploaded successfully.")
                            st.session_state.active_page = "Dashboard"
                            st.rerun()
                except Exception as e:
                    st.error(f"Error processing CSV: {e}")

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("---", unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 1rem 0 0.5rem 0;'>Need a template?</h4>", unsafe_allow_html=True)
        sample = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-20"],
            "scope": ["Scope 2", "Scope 1"],
            "category": ["Electricity", "Mobile Combustion"],
            "activity": ["Office Electricity", "Company Vehicle"],
            "quantity": [1000, 50],
            "unit": ["kWh", "liter"],
            "emission_factor": [0.82, 2.31495],
            "notes": ["Monthly electricity bill", "Fleet vehicle fuel"],
        })
        st.download_button(
            label="Download Sample CSV Template",
            data=sample.to_csv(index=False).encode("utf-8"),
            file_name="sample_emissions.csv",
            mime="text/csv",
        )
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_page == "Settings":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.25rem;'>Settings</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--muted); font-size: 1.125rem; margin-bottom: 3rem;'>Manage your organization profile and preferences</p>", unsafe_allow_html=True)
    st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Company Information</h3>", unsafe_allow_html=True)
    with st.form("company_info_form"):
        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("<h4 style='color: var(--muted); font-size: 14px; text-transform: uppercase; margin-bottom: 0.5rem;'>Company Details</h4>", unsafe_allow_html=True)
            company_name = st.text_input("Company Name")
            industry = st.text_input("Industry")
            location = st.text_input("Location")
        with b:
            st.markdown("<h4 style='color: var(--muted); font-size: 14px; text-transform: uppercase; margin-bottom: 0.5rem;'>Contact Information</h4>", unsafe_allow_html=True)
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Save Settings", type="primary", use_container_width=True)
        if submitted:
            st.success("Settings saved successfully.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_page == "AI Insights":
    st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0.25rem;'>AI Insights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--muted); font-size: 1.125rem; margin-bottom: 2rem;'>Leverage AI for data mapping, offset recommendations, regulatory insights, and optimization</p>", unsafe_allow_html=True)
    try:
        from ai_agents import CarbonFootprintAgents
        if "ai_agents" not in st.session_state:
            st.session_state.ai_agents = CarbonFootprintAgents()
    except Exception:
        st.warning("AI agents not configured. Ensure ai_agents.py and API keys are set.")

    tabs = st.tabs(["Data Assistant", "Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])

    with tabs[0]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Data Entry Assistant</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Get help classifying emissions and mapping them to the correct scope categories.</p>", unsafe_allow_html=True)
        desc = st.text_area("Describe your emission activity", placeholder="Example: Diesel generators used for backup power at our office. How should this be categorized?", height=120)
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Get Assistance", key="data_assistant_btn", type="primary", use_container_width=True):
            if desc:
                with st.spinner("Analyzing..."):
                    try:
                        result = st.session_state.ai_agents.run_data_entry_crew(desc)
                        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='stCard' style='background: var(--elev-hover);'>{str(result)}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Check your API key and try again.")
            else:
                st.warning("Please provide a description.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Report Summary Generator</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Generate a comprehensive, human-readable summary of your emissions data.</p>", unsafe_allow_html=True)
        if st.session_state.emissions_data.empty:
            st.warning("No emissions data available. Please add data first.")
        else:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Generate Summary", key="report_summary_btn", type="primary", use_container_width=True):
                with st.spinner("Summarizing..."):
                    try:
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_report_summary_crew(emissions_str)
                        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='stCard' style='background: var(--elev-hover);'>{str(result)}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Check your API key and try again.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Carbon Offset Advisor</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Get recommendations for verified carbon offset options based on your profile.</p>", unsafe_allow_html=True)
        if st.session_state.emissions_data.empty:
            st.warning("No emissions data available. Please add data first.")
        else:
            total = st.session_state.emissions_data.get("emissions_kgCO2e", pd.Series([0])).sum()
            st.markdown(f"<div class='metric-card' style='padding: 1.5rem; margin-bottom: 2rem;'><div class='metric-label'>Total Emissions to Offset</div><div class='metric-value' style='font-size: 24px;'>{total:.2f} kgCO2e</div></div>", unsafe_allow_html=True)
            col1, _ = st.columns(2)
            with col1:
                loc = st.text_input("Location", placeholder="e.g., City, Country")
                industry = st.selectbox("Industry", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"])
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Get Offset Recommendations", key="offset_advisor_btn", type="primary", use_container_width=True):
                if loc:
                    with st.spinner("Finding options..."):
                        try:
                            result = st.session_state.ai_agents.run_offset_advice_crew(total, loc, industry)
                            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='stCard' style='background: var(--elev-hover);'>{str(result)}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Check your API key and try again.")
                else:
                    st.warning("Please enter your location.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Regulation Radar</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Get insights on current and upcoming carbon regulations relevant to your business.</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            reg_loc = st.text_input("Company Location", placeholder="e.g., City, Country")
            reg_industry = st.selectbox("Industry Sector", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"], key="reg_industry")
        with col2:
            export_markets = st.multiselect("Export Markets", ["European Union", "Japan", "United States", "China", "Indonesia", "India", "Other"])
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Check Regulations", key="regulation_radar_btn", type="primary", use_container_width=True):
            if reg_loc and export_markets:
                with st.spinner("Analyzing..."):
                    try:
                        result = st.session_state.ai_agents.run_regulation_check_crew(reg_loc, reg_industry, ", ".join(export_markets))
                        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='stCard' style='background: var(--elev-hover);'>{str(result)}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Check your API key and try again.")
            else:
                st.warning("Enter a location and select at least one export market.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[4]:
        st.markdown("<div class='stCard' style='padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; color: var(--primary); font-size: 1.5rem;'>Emission Optimizer</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--muted); margin-bottom: 1.5rem;'>Get AI-powered recommendations to reduce your carbon footprint.</p>", unsafe_allow_html=True)
        if st.session_state.emissions_data.empty:
            st.warning("No emissions data available. Please add data first.")
        else:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Generate Optimization Recommendations", key="emission_optimizer_btn", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    try:
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_optimization_crew(emissions_str)
                        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='stCard' style='background: var(--elev-hover);'>{str(result)}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Check your API key and try again.")
        st.markdown("</div>", unsafe_allow_html=True)
