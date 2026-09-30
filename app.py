"""Credential-free AWS cost optimization prototype built with Streamlit."""

from datetime import datetime
from pathlib import Path
import secrets
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="AWS Cost Optimization",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


ACTION_DB_PATH = Path(__file__).with_name("action_history.db")


def initialise_action_database() -> None:
    """Create the lightweight local audit store used by this prototype."""
    with sqlite3.connect(ACTION_DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                saving REAL NOT NULL,
                sample TEXT NOT NULL,
                updated TEXT NOT NULL
            )
            """
        )


def record_action(action: str, status: str, saving: float, sample: str) -> dict:
    """Persist one user decision locally and return the matching UI record."""
    event = {
        "action": action,
        "status": status,
        "saving": saving,
        "sample": sample,
        "updated": datetime.now().strftime("%b %d, %H:%M"),
    }
    with sqlite3.connect(ACTION_DB_PATH) as connection:
        connection.execute(
            "INSERT INTO action_history (action, status, saving, sample, updated) VALUES (?, ?, ?, ?, ?)",
            (event["action"], event["status"], event["saving"], event["sample"], event["updated"]),
        )
    return event


def load_action_history() -> list[dict]:
    with sqlite3.connect(ACTION_DB_PATH) as connection:
        rows = connection.execute(
            "SELECT action, status, saving, sample, updated FROM action_history ORDER BY id DESC"
        ).fetchall()
    return [dict(zip(["action", "status", "saving", "sample", "updated"], row)) for row in rows]


initialise_action_database()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "demo_seed" not in st.session_state:
    st.session_state.demo_seed = secrets.randbelow(900_000) + 100_000
if "action_status" not in st.session_state:
    st.session_state.action_status = {}
if "action_events" not in st.session_state:
    st.session_state.action_events = load_action_history()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
      :root { --ink:#f5f1ec; --muted:#a39a91; --line:#302a25; --orange:#ff842e; --panel:rgba(19,17,16,.94); }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
      .stApp { min-height:100vh; background:#050505; isolation:isolate; position:relative; overflow:hidden; }
      .stApp::before,.stApp::after { content:""; position:fixed; inset:0; z-index:0; pointer-events:none; background-repeat:repeat; }
      .stApp::before { opacity:.7; background-image:radial-gradient(circle,rgba(255,126,35,.95) 0 1px,transparent 1.8px),radial-gradient(circle,rgba(255,157,72,.7) 0 1.3px,transparent 2px),radial-gradient(circle,rgba(232,91,21,.75) 0 .8px,transparent 1.7px); background-size:97px 113px,157px 139px,211px 187px; background-position:0 0,42px 65px,101px 23px; animation:fall-a 32s linear infinite; }
      .stApp::after { opacity:.38; background-image:radial-gradient(circle,rgba(255,186,112,.8) 0 1px,transparent 2px),radial-gradient(circle,rgba(255,101,20,.9) 0 1.2px,transparent 2px); background-size:181px 163px,127px 197px; background-position:67px 33px,18px 91px; animation:fall-b 45s linear infinite; }
      @keyframes fall-a { to { background-position:0 440px,42px 505px,101px 463px; } }
      @keyframes fall-b { to { background-position:67px 510px,18px 571px; } }
      @keyframes enter { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
      .stApp > header { background:transparent; z-index:2; }
      .stApp main { position:relative; z-index:1; background:transparent; }
      .block-container { max-width:1440px; padding:2rem 2rem 3rem; animation:enter .55s ease-out both; }
      h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.045em; color:var(--ink); }
      .eyebrow { color:#ff9a50; font-size:.7rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; }
      .hero-title { font-family:'Manrope',sans-serif; font-size:2.5rem; line-height:1.1; font-weight:700; letter-spacing:-.06em; margin:.25rem 0 .55rem; }
      .subtle { color:#aaa198; font-size:.93rem; }
      .kpi { height:132px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:flex-start; background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1.05rem 1.2rem; box-shadow:0 8px 30px rgba(0,0,0,.35); }
      .kpi-label { color:#aaa198; font-size:.72rem; letter-spacing:.075em; font-weight:700; white-space:nowrap; }
      .kpi-value { font-family:'Manrope',sans-serif; font-size:clamp(1.45rem,2vw,1.8rem); line-height:1.12; font-weight:700; letter-spacing:-.055em; padding:.42rem 0 .2rem; white-space:nowrap; }
      .kpi-value small { font-size:.82rem; color:#9b9289; letter-spacing:0; }
      .kpi-foot { margin-top:auto; color:#8e857d; font-size:.72rem; line-height:1.2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
      .panel { background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:1.2rem 1.35rem .65rem; box-shadow:0 8px 30px rgba(0,0,0,.35); }
      .rec-card { background:rgba(17,15,14,.96); border:1px solid #332b25; border-radius:18px; padding:1.1rem 1.3rem; margin:.7rem 0; box-shadow:0 8px 25px rgba(0,0,0,.28); transition:transform .18s ease,border-color .18s ease; }
      .rec-card:hover { transform:translateY(-2px); border-color:#76401f; }
      .rec-title { font-family:'Manrope',sans-serif; font-size:1.12rem; font-weight:700; letter-spacing:-.03em; }
      .tag { display:inline-block; color:#ffb175; background:#392114; border-radius:999px; padding:.22rem .55rem; font-size:.66rem; font-weight:700; margin-bottom:.45rem; }
      .impact { font-family:'Manrope',sans-serif; color:#ff963f; font-size:1.35rem; font-weight:700; letter-spacing:-.04em; white-space:nowrap; }
      .status { border-radius:999px; padding:.25rem .58rem; background:#2c2824; color:#d0c5bb; font-size:.68rem; font-weight:700; display:inline-block; }
      div[data-testid="stTabs"] button { font-weight:600; color:#aaa198; }
      div[data-testid="stTabs"] button[aria-selected="true"] { color:#ff963f; }
      div.stButton > button { border-radius:10px; font-weight:600; border:1px solid #4a3324; background:#171311; color:#f4f0ea; transition:all .18s ease; }
      div.stButton > button:hover { border-color:#ff842e; color:#ff9a50; transform:translateY(-1px); }
      div.stButton > button[kind="primary"] { background:#e96816; border-color:#ff8a24; color:#fff8f0; }
      [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
      [data-testid="stCaptionContainer"] { color:#8e857d !important; }
      .login-card { background:linear-gradient(145deg,rgba(22,19,17,.98),rgba(12,11,10,.97)); border:1px solid #393029; border-radius:26px; padding:2rem; box-shadow:0 24px 90px rgba(0,0,0,.5),0 0 80px rgba(255,119,34,.07); }
      .login-mark { width:46px; height:46px; border:1px solid #75421f; border-radius:15px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#ff922e,#d44e0d); color:#fff; font-size:1.3rem; font-weight:800; box-shadow:0 0 30px rgba(255,120,38,.22); }
      .login-title { font-family:'Manrope',sans-serif; font-size:2.15rem; line-height:1.1; font-weight:700; letter-spacing:-.06em; margin:.8rem 0 .6rem; }
      .live-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#4dd59a; box-shadow:0 0 12px rgba(77,213,154,.85); margin-right:7px; }
      .sample-pill { display:inline-block; border:1px solid #3c3026; border-radius:99px; background:#15110e; padding:.3rem .65rem; color:#d5b293; font-size:.72rem; }
      @media (prefers-reduced-motion: reduce) { .stApp::before,.stApp::after,.block-container { animation:none; } *,*::before,*::after { scroll-behavior:auto !important; transition:none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)


if not st.session_state.authenticated:
    st.write("")
    st.write("")
    left, right = st.columns([1.05, .95], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="login-title" style="font-size:3.35rem">AWS Cost Optimizer</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtle" style="max-width:520px;font-size:1.04rem;line-height:1.7">Find the quiet waste hiding in your AWS bill. Explore a fresh, simulated account, review evidence-backed recommendations, and see the savings story update as you act.</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<span class="sample-pill"><span class="live-dot"></span>Sample data · generated for this session</span>', unsafe_allow_html=True)
        st.write("")
        st.markdown("**A working concept, in a safe sandbox**")
        st.caption("Live AWS credentials are not used. Decisions update this local account only.")
    with right:
        st.markdown('<div class="login-card"><div class="login-mark">✦</div><div class="eyebrow" style="margin-top:1.1rem">WELCOME BACK</div><div class="login-title">Sign in to your workspace</div><div class="subtle">Use the sample credentials to explore the cost console.</div></div>', unsafe_allow_html=True)
        with st.form("demo_login", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            st.selectbox("Connected environment", ["AWS account · 123456789012 · us-east-1"])
            submitted = st.form_submit_button("Enter dashboard  →", type="primary", use_container_width=True)
        if submitted:
            if username.strip() == "1234" and password == "1234":
                st.session_state.authenticated = True
                st.session_state.login_error = False
                st.rerun()
            else:
                st.session_state.login_error = True
        if st.session_state.get("login_error"):
            st.error("Those sample credentials don’t match. Use 1234 for both fields.")
        st.caption("Sample login: username `1234` · password `1234`")
    st.stop()


@st.cache_data(show_spinner=False)
def build_demo_data(seed: int):
    """Make a new coherent set of Cost Explorer and CloudWatch-like sample data."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=30, freq="D")
    base = rng.uniform(155, 235)
    trend = np.linspace(rng.uniform(-8, 3), rng.uniform(5, 28), len(dates))
    wave = 17 * np.sin(np.linspace(rng.uniform(0, 2), rng.uniform(3.5, 5.5), len(dates)))
    daily_spend = np.maximum(45, base + trend + wave + rng.normal(0, 15, len(dates)))
    spend = pd.DataFrame({"Date": dates, "Spend": daily_spend.round(2)})
    total_30d = float(spend["Spend"].sum())

    service_names = ["EC2", "S3", "RDS", "Data Transfer", "Other"]
    shares = rng.dirichlet([3.5, 2.3, 1.3, .9, 2.1])
    services = pd.DataFrame({"Service": service_names, "Monthly cost": (shares * total_30d).round(2)})
    services.loc[services.index[-1], "Monthly cost"] += total_30d - services["Monthly cost"].sum()
    services = services.sort_values("Monthly cost", ascending=True)

    hours = pd.date_range(end=pd.Timestamp.now().floor("h"), periods=15 * 24, freq="h")
    hour = hours.hour.to_numpy()
    weekday = hours.dayofweek.to_numpy()
    business_load = ((hour >= 8) & (hour <= 19) & (weekday < 5)).astype(float)
    low_utilization = rng.random() < .72
    cpu_base = rng.uniform(2.1, 3.6) if low_utilization else rng.uniform(5.1, 7.0)
    gpu_base = rng.uniform(.4, 1.4) if low_utilization else rng.uniform(2.4, 3.8)
    cpu = (cpu_base + business_load * rng.uniform(1.1, 2.7) + rng.normal(0, .8, len(hours))).clip(.2, 18)
    gpu = (gpu_base + business_load * rng.uniform(.15, .65) + rng.normal(0, .28, len(hours))).clip(0, 8)
    telemetry = pd.DataFrame({"Timestamp": hours, "CPU %": cpu, "GPU %": gpu})

    object_count = int(rng.integers(180, 420))
    object_age = rng.integers(2, 241, object_count)
    access_days = rng.choice([0, 1, 3, 7, 30, 60, 90], p=[.25, .12, .12, .13, .14, .12, .12], size=object_count)
    s3 = pd.DataFrame({"Age days": object_age, "Days since access": access_days})
    cold_count = int(((s3["Age days"] >= 90) & (s3["Days since access"] >= 30)).sum())
    eip_count = int(rng.integers(1, 4))
    previous_total = total_30d * (1 + rng.uniform(-.14, .17))
    budget = float(rng.integers(7800, 10800))
    return {
        "spend": spend,
        "services": services,
        "telemetry": telemetry,
        "cold_count": cold_count,
        "eip_count": eip_count,
        "total_30d": total_30d,
        "previous_total": previous_total,
        "budget": budget,
        "cpu_avg": float(telemetry["CPU %"].mean()),
        "gpu_avg": float(telemetry["GPU %"].mean()),
    }


seed = int(st.session_state.demo_seed)
data = build_demo_data(seed)
services_df = data["services"]
service_cost = dict(zip(services_df["Service"], services_df["Monthly cost"]))
ec2_triggered = data["cpu_avg"] < 5 and data["gpu_avg"] < 3
recommendations = []
if ec2_triggered:
    recommendations.append({
        "id": "ec2-rightsize", "service": "EC2 · RIGHTSIZING",
        "title": "Right-size underutilized instances",
        "description": f"4 instances averaged {data['cpu_avg']:.1f}% CPU and {data['gpu_avg']:.1f}% GPU across the 15-day CloudWatch sample. Consider a smaller family while preserving workload headroom.",
        "saving": round(service_cost["EC2"] * .13), "reason": "15-day CPU and GPU utilization", "confidence": "High confidence",
    })
if data["cold_count"] > 0:
    recommendations.append({
        "id": "s3-glacier", "service": "S3 · STORAGE LIFECYCLE",
        "title": "Move cold objects to Glacier",
        "description": f"{data['cold_count']} sampled objects are over 90 days old and have not been accessed for at least 30 days. A lifecycle policy can reduce storage cost.",
        "saving": max(18, round(min(service_cost["S3"] * .16, data["cold_count"] * .72))), "reason": "Simulated S3 access log", "confidence": "Low risk",
    })
recommendations.append({
    "id": "release-eip", "service": "EC2 · NETWORKING",
    "title": "Release unattached Elastic IPs",
    "description": f"{data['eip_count']} allocated public IPv4 addresses in this sample are unattached. Releasing unused addresses avoids hourly public IPv4 charges.",
    "saving": round(data["eip_count"] * 3.65), "reason": "Sample resource inventory", "confidence": "Safe to apply",
})

if st.session_state.get("status_seed") != seed:
    st.session_state.action_status = {item["id"]: "Active" for item in recommendations}
    st.session_state.status_seed = seed
else:
    for item in recommendations:
        st.session_state.action_status.setdefault(item["id"], "Active")

with st.container():
    brand_col, env_col, refresh_col, logout_col = st.columns([2.35, 1.45, 1.05, .7], vertical_alignment="center")
    with brand_col:
        st.markdown('<div class="eyebrow">CLOUD FINANCIAL OPERATIONS</div><div style="font:700 1.14rem Manrope;letter-spacing:-.04em">AWS Cost Optimization</div>', unsafe_allow_html=True)
    with env_col:
        st.markdown('<span class="sample-pill"><span class="live-dot"></span>AWS account · us-east-1</span>', unsafe_allow_html=True)
    with refresh_col:
        if st.button("↻  Refresh data", use_container_width=True, help="Generate a fresh telemetry sample for this session"):
            st.session_state.demo_seed = secrets.randbelow(900_000) + 100_000
            st.toast("Fresh sample telemetry generated", icon="✨")
            st.rerun()
    with logout_col:
        if st.button("Log out", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

st.markdown('<div class="eyebrow" style="margin-top:1.3rem">YOUR COST PICTURE · GENERATED SAMPLE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Find the spend that can work harder.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">A simulated AWS account with fresh telemetry, explainable recommendations, and a clear action trail.</div>', unsafe_allow_html=True)
st.write("")

total_spend = data["total_30d"]
daily_avg = float(data["spend"]["Spend"].mean())
total_savings = sum(item["saving"] for item in recommendations)
open_savings = sum(item["saving"] for item in recommendations if st.session_state.action_status[item["id"]] == "Active")
in_action_savings = sum(item["saving"] for item in recommendations if st.session_state.action_status[item["id"]] in {"Applied", "Scheduled"})
decisions = sum(st.session_state.action_status[item["id"]] != "Active" for item in recommendations)

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    st.markdown(f'<div class="kpi"><div class="kpi-label">LAST 30 DAYS</div><div class="kpi-value">${total_spend:,.0f}</div><div class="kpi-foot">1 AWS account · us-east-1</div></div>', unsafe_allow_html=True)
with k2:
    delta = (total_spend / data["previous_total"] - 1) * 100
    delta_word = "up" if delta >= 0 else "down"
    st.markdown(f'<div class="kpi"><div class="kpi-label">DAILY AVERAGE</div><div class="kpi-value">${daily_avg:,.0f}</div><div class="kpi-foot">{abs(delta):.1f}% {delta_word} vs prior sample</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi"><div class="kpi-label">TOTAL IDENTIFIED SAVINGS</div><div class="kpi-value">${open_savings:,.0f}<small> / mo</small></div><div class="kpi-foot">{sum(st.session_state.action_status[item["id"]] == "Active" for item in recommendations)} open recommendations</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi"><div class="kpi-label">SAVINGS IN ACTION</div><div class="kpi-value">${in_action_savings:,.0f}<small> / mo</small></div><div class="kpi-foot">Applied or scheduled · {decisions} decisions reviewed</div></div>', unsafe_allow_html=True)

st.write("")
dashboard_tab, actions_tab, chat_tab = st.tabs(["Overview", "Action Center", "AI Assistant"])

with dashboard_tab:
    range_col, _ = st.columns([1, 3])
    with range_col:
        display_days = st.selectbox("Spend trend window", [7, 14, 30], index=2, format_func=lambda value: f"Last {value} days")
    filtered_spend = data["spend"].tail(display_days)
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(f"**Daily AWS spend**  ·  Last {display_days} days")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_spend["Date"], y=filtered_spend["Spend"], mode="lines", line=dict(color="#ff842e", width=3), fill="tozeroy", fillcolor="rgba(255,132,46,.12)", hovertemplate="%{x|%b %d}<br>$%{y:,.2f}<extra></extra>"))
        fig.update_layout(height=310, margin=dict(l=0,r=8,t=12,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(color="#aaa198"), xaxis=dict(showgrid=False, tickfont=dict(color="#aaa198")), yaxis=dict(title=None, gridcolor="#302a25", tickprefix="$", tickfont=dict(color="#aaa198"), zeroline=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Spend by AWS service**  ·  Last 30 days")
        bar = px.bar(services_df, x="Monthly cost", y="Service", orientation="h", text="Monthly cost", color_discrete_sequence=["#ff842e"])
        bar.update_traces(texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False, marker_line_width=0)
        bar.update_layout(height=310, margin=dict(l=0,r=48,t=12,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(color="#aaa198"), xaxis=dict(visible=False, range=[0, max(services_df["Monthly cost"])*1.38]), yaxis=dict(title=None, autorange="reversed", tickfont=dict(color="#d1c8bf")))
        st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    budget_col, signal_col = st.columns([1, 1], gap="large")
    with budget_col:
        used_pct = min(total_spend / data["budget"], 1.0)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Budget pacing**  ·  Sample monthly target")
        st.progress(used_pct, text=f"${total_spend:,.0f} of ${data['budget']:,.0f} · {used_pct:.0%} used")
        st.caption("A pacing signal for the sample account. Connect billing data for an actual budget.")
        st.markdown('</div>', unsafe_allow_html=True)
    with signal_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Utilization signal**  ·  15-day CloudWatch sample")
        st.markdown(f"EC2 averaged **{data['cpu_avg']:.1f}% CPU** and **{data['gpu_avg']:.1f}% GPU**. " + ("The rightsizing rule found a sustained low-utilization opportunity." if ec2_triggered else "The rightsizing thresholds were not met in this sample."))
        st.markdown('</div>', unsafe_allow_html=True)
    st.caption(f"Sample #{seed % 10000:04d} · Randomized offline telemetry · No AWS credentials or live resource changes")

with actions_tab:
    current_items = [item for item in recommendations if st.session_state.action_status[item["id"]] == "Active"]
    resolved_items = [item for item in recommendations if st.session_state.action_status[item["id"]] != "Active"]
    st.markdown("### Optimization opportunities")
    st.markdown('<div class="subtle">Review the evidence, then apply, schedule, or dismiss each opportunity. Each decision is recorded locally.</div>', unsafe_allow_html=True)
    current_tab, completed_tab = st.tabs([f"Current actions · {len(current_items)}", f"Completed actions · {len(st.session_state.action_events)}"])
    with current_tab:
        st.caption("Estimated savings shown here are open opportunities. Accepting or dismissing one moves it to Completed Actions.")
        if not current_items:
            st.success("You’re all caught up. No open recommendations remain in this sample.")
        for item in current_items:
            with st.container(border=True):
                details, savings_col = st.columns([4.3, 1], vertical_alignment="center")
                with details:
                    st.markdown(f'<span class="tag">{item["service"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="rec-title">{item["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="subtle">{item["description"]}</div>', unsafe_allow_html=True)
                    st.caption(f'{item["confidence"]}  ·  Evidence: {item["reason"]}')
                with savings_col:
                    st.markdown(f'<div class="impact">${item["saving"]}<small style="font-size:.72rem;color:#999087"> / mo</small></div>', unsafe_allow_html=True)
                    st.caption("estimated")
                apply_col, schedule_col, ignore_col = st.columns([1, 1, 1])
                if apply_col.button("Apply action", key=f"apply-{item['id']}", type="primary", use_container_width=True):
                    st.session_state.action_status[item["id"]] = "Applied"
                    st.session_state.action_events.insert(0, record_action(item["title"], "Applied", item["saving"], f"#{seed % 10000:04d}"))
                    st.toast(f"Action applied · ${item['saving']}/mo opportunity captured", icon="✅")
                    st.rerun()
                if schedule_col.button("Schedule", key=f"schedule-{item['id']}", use_container_width=True):
                    st.session_state.action_status[item["id"]] = "Scheduled"
                    st.session_state.action_events.insert(0, record_action(item["title"], "Scheduled", item["saving"], f"#{seed % 10000:04d}"))
                    st.toast("Action added to the schedule", icon="🗓️")
                    st.rerun()
                if ignore_col.button("Ignore", key=f"ignore-{item['id']}", use_container_width=True):
                    st.session_state.action_status[item["id"]] = "Ignored"
                    st.session_state.action_events.insert(0, record_action(item["title"], "Dismissed", item["saving"], f"#{seed % 10000:04d}"))
                    st.toast("Recommendation dismissed", icon="✓")
                    st.rerun()
    with completed_tab:
        if not st.session_state.action_events:
            st.info("Actions you apply, schedule, or dismiss will appear here with their estimate and timestamp.")
        else:
            history_df = pd.DataFrame(st.session_state.action_events).rename(columns={"action": "Action", "status": "Status", "saving": "Estimated savings ($/mo)", "sample": "Sample", "updated": "Updated"})
            st.dataframe(history_df.iloc[::-1], hide_index=True, use_container_width=True)
            captured = sum(event["saving"] for event in st.session_state.action_events if event["status"].startswith(("Applied", "Scheduled")))
            st.caption(f"${captured:,}/mo in estimated savings have been applied or scheduled in this session. Values are illustrative, not realized AWS savings.")

with chat_tab:
    st.markdown("### Ask about this account")
    st.markdown('<div class="subtle">Answers use the sample data currently shown in your dashboard.</div>', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Try ‘Why is my bill high?’")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        query = prompt.lower()
        if any(term in query for term in ["high", "bill", "spend", "cost"]):
            largest = services_df.sort_values("Monthly cost", ascending=False).iloc[0]
            answer = f"The account spent **${total_spend:,.0f}** in the last 30 days, **{abs(delta):.1f}% {delta_word}** versus its prior sample. **{largest['Service']}** is the largest service at **${largest['Monthly cost']:,.0f}**. Review current recommendations for the sample’s specific savings signals."
        elif any(term in query for term in ["ec2", "cpu", "gpu", "instance"]):
            result = "The rightsizing rule triggered." if ec2_triggered else "The rightsizing thresholds were not met, so no EC2 action is recommended for this sample."
            answer = f"Across the simulated 15-day CloudWatch window, CPU averaged **{data['cpu_avg']:.1f}%** and GPU **{data['gpu_avg']:.1f}%**. {result}"
        elif any(term in query for term in ["s3", "glacier", "storage"]):
            answer = f"The sampled S3 access data found **{data['cold_count']}** objects older than 90 days with no access in at least 30 days. The current estimated tiering opportunity is included in the Action Center if its rule triggered."
        elif any(term in query for term in ["save", "recommend", "action"]):
            answer = f"There are **{len(current_items)}** open recommendations worth **${open_savings:,}/month** in this sample. **${in_action_savings:,}/month** is already applied or scheduled."
        else:
            answer = "I can explain the bill, EC2 utilization, S3 storage signals, or current savings recommendations."
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

st.markdown("<div style='text-align:center;color:#827970;font-size:.7rem;padding-top:2rem;letter-spacing:.08em'>AWS COST OPTIMIZER · LOCAL SAMPLE DATA</div>", unsafe_allow_html=True)
