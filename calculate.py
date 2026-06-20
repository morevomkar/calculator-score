import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import io
import re

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StatLab Pro · Statistical Tests",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    scroll-behavior: smooth;
}

/* ── App background: deep grid ─────────────────────────── */
.stApp {
    background-color: #06080f;
    background-image:
        linear-gradient(rgba(99,102,241,.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,.07) 1px, transparent 1px);
    background-size: 40px 40px;
    color: #e2e8f0;
    min-height: 100vh;
}

/* ── Hero banner ───────────────────────────────────────── */
.hero-wrap {
    background: linear-gradient(135deg, #0d1117 0%, #111827 40%, #0d1b2e 100%);
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 2.8rem 3rem 2.4rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content:'';
    position:absolute; inset:0;
    background: radial-gradient(ellipse 60% 60% at 80% 50%, rgba(99,102,241,.18) 0%, transparent 70%),
                radial-gradient(ellipse 40% 50% at 20% 30%, rgba(6,182,212,.12) 0%, transparent 70%);
    pointer-events:none;
}
.hero-eyebrow {
    font-size:.72rem; font-weight:600; letter-spacing:.18em; text-transform:uppercase;
    color:#6366f1; margin-bottom:.7rem;
    display:flex; align-items:center; gap:.5rem;
}
.hero-eyebrow::before { content:''; display:inline-block; width:24px; height:2px; background:#6366f1; }
.hero-title {
    font-size: 2.8rem; font-weight:700; line-height:1.1;
    background: linear-gradient(100deg, #e0f2fe 0%, #a5b4fc 40%, #67e8f9 80%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    margin-bottom:.6rem;
}
.hero-sub { font-size:1rem; color:#64748b; max-width:560px; line-height:1.6; }
.hero-chips { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1.4rem; }
.chip {
    background: rgba(99,102,241,.12); border:1px solid rgba(99,102,241,.3);
    color:#a5b4fc; border-radius:999px; padding:.25rem .8rem;
    font-size:.75rem; font-weight:500; letter-spacing:.04em;
    font-family:'JetBrains Mono', monospace;
}

/* ── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: .35rem;
    gap: .25rem;
    margin-bottom: 1.4rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600; font-size:.88rem;
    color: #475569;
    border-radius: 10px;
    padding: .55rem 1.4rem;
    border: none !important;
    background: transparent;
    transition: all .2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #0891b2) !important;
    color: #fff !important;
    box-shadow: 0 4px 18px rgba(79,70,229,.35);
}
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }
.stTabs [data-baseweb="tab-border"]    { display:none !important; }

/* ── Section cards ─────────────────────────────────────── */
.card {
    background: #0d1117;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}
.card-title {
    font-size:.72rem; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
    color:#6366f1; margin-bottom:1rem; display:flex; align-items:center; gap:.5rem;
}
.card-title::before { content:''; width:18px; height:2px; background:#6366f1; display:inline-block; }

/* ── Source toggle pills ───────────────────────────────── */
.stRadio > div { gap:.5rem !important; }
.stRadio [data-testid="stMarkdownContainer"] p { margin:0; }

/* ── Stat result cards ─────────────────────────────────── */
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:1.2rem 0; }
.stat-card {
    background: linear-gradient(145deg, #0f172a, #111827);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: var(--accent, linear-gradient(90deg,#6366f1,#06b6d4));
}
.stat-card.accent-purple { --accent: linear-gradient(90deg,#8b5cf6,#6366f1); }
.stat-card.accent-cyan   { --accent: linear-gradient(90deg,#06b6d4,#0891b2); }
.stat-card.accent-pink   { --accent: linear-gradient(90deg,#ec4899,#a855f7); }
.stat-card.accent-emerald{ --accent: linear-gradient(90deg,#10b981,#059669); }
.stat-label {
    font-size:.7rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
    color:#475569; margin-bottom:.5rem;
}
.stat-value {
    font-family:'JetBrains Mono',monospace; font-size:1.65rem; font-weight:600;
    color:#e0f2fe; line-height:1;
}
.stat-sub { font-size:.72rem; color:#475569; margin-top:.3rem; }

/* ── Verdict banners ────────────────────────────────────── */
.verdict {
    border-radius: 12px; padding: 1rem 1.4rem;
    font-size:.92rem; font-weight:600; margin: 1rem 0;
    display:flex; align-items:center; gap:.75rem;
    border: 1px solid;
}
.verdict-pass {
    background: rgba(16,185,129,.08); border-color: rgba(16,185,129,.35); color:#34d399;
}
.verdict-fail {
    background: rgba(239,68,68,.08); border-color: rgba(239,68,68,.35); color:#f87171;
}
.verdict-icon { font-size:1.3rem; }

/* ── Upload box ─────────────────────────────────────────── */
.upload-zone {
    background: rgba(99,102,241,.04);
    border: 1.5px dashed rgba(99,102,241,.35);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    text-align:center; color:#475569; font-size:.85rem;
    margin-bottom:1rem; transition: border-color .2s;
}
.upload-zone:hover { border-color: rgba(99,102,241,.6); }

/* ── Column pills ───────────────────────────────────────── */
.pills-wrap { display:flex; flex-wrap:wrap; gap:.4rem; margin:.5rem 0 1rem; }
.col-pill {
    background: rgba(6,182,212,.1); border:1px solid rgba(6,182,212,.3);
    color:#67e8f9; border-radius:6px; padding:.2rem .6rem;
    font-size:.72rem; font-family:'JetBrains Mono',monospace; cursor:default;
}

/* ── Divider ─────────────────────────────────────────────── */
.divider { border:none; border-top:1px solid #1e293b; margin:1.4rem 0; }

/* ── Streamlit overrides ─────────────────────────────────── */
.stTextArea textarea, .stNumberInput input, .stTextInput input {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .85rem !important;
    transition: border-color .2s !important;
}
.stTextArea textarea:focus, .stNumberInput input:focus, .stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.15) !important;
}
.stSelectbox > div > div {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
.stMultiSelect > div {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background: rgba(99,102,241,.25) !important;
    border: 1px solid rgba(99,102,241,.4) !important;
    border-radius: 6px !important;
}
.stSlider [data-testid="stSlider"] > div > div > div { background: #6366f1 !important; }
.stSlider [data-testid="stThumbValue"] { color: #a5b4fc !important; }
label, .stSelectbox label, .stMultiSelect label, .stTextArea label,
.stTextInput label, .stNumberInput label, .stRadio label {
    color: #64748b !important; font-size: .8rem !important;
    font-weight: 500 !important; letter-spacing:.03em !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #0891b2) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    padding: .6rem 2rem !important;
    letter-spacing: .03em !important;
    box-shadow: 0 4px 16px rgba(79,70,229,.3) !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 24px rgba(79,70,229,.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Dataframe ───────────────────────────────────────────── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid #1e293b !important; border-radius: 10px !important; }

/* ── Warning / Error ─────────────────────────────────────── */
.stAlert { border-radius: 10px !important; }

/* ── Section title ───────────────────────────────────────── */
.section-title {
    font-size:1.35rem; font-weight:700; color:#e0f2fe;
    margin-bottom:.25rem; line-height:1.2;
}
.section-desc { font-size:.85rem; color:#475569; margin-bottom:1.4rem; line-height:1.5; }

/* ── Footer ──────────────────────────────────────────────── */
.footer {
    text-align:center; color:#1e293b; font-size:.75rem;
    padding:2rem 0 1rem; letter-spacing:.05em;
}

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width:768px) {
    .hero-title { font-size:1.9rem; }
    .stat-grid  { grid-template-columns:1fr 1fr; }
}
@media (max-width:480px) {
    .stat-grid  { grid-template-columns:1fr; }
    .hero-wrap  { padding:1.8rem 1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def parse_data(text):
    tokens = re.split(r'[\s,]+', text.strip())
    return [float(t) for t in tokens if t]

ACCENT_COLORS = {
    'purple': '#8b5cf6', 'indigo': '#6366f1', 'cyan': '#06b6d4',
    'pink': '#ec4899',   'emerald': '#10b981', 'amber': '#f59e0b',
}
BG_DARK  = '#06080f'
BG_CARD  = '#0d1117'
BG_CARD2 = '#0f172a'
BORDER   = '#1e293b'
TEXT_DIM = '#475569'
PALETTE  = ['#8b5cf6','#06b6d4','#ec4899','#10b981','#f59e0b','#f43f5e','#38bdf8','#a3e635','#fb923c','#e879f9']

def dark_fig(w=8, h=3.8, cols=1):
    if cols == 1:
        fig, ax = plt.subplots(figsize=(w, h))
        axes = [ax]
    else:
        fig, axes = plt.subplots(1, cols, figsize=(w, h))
    fig.patch.set_facecolor(BG_DARK)
    for ax in (axes if cols > 1 else [axes[0]]):
        ax.set_facecolor(BG_CARD2)
        for sp in ax.spines.values():
            sp.set_color(BORDER)
        ax.tick_params(colors=TEXT_DIM, labelsize=8.5)
        ax.xaxis.label.set_color(TEXT_DIM)
        ax.yaxis.label.set_color(TEXT_DIM)
        ax.title.set_color('#cbd5e1')
        ax.grid(axis='y', color=BORDER, linewidth=.6, alpha=.7)
        ax.set_axisbelow(True)
    return (fig, axes[0]) if cols == 1 else (fig, axes)

def fig_to_st(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor=BG_DARK)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

def load_excel(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
        return {'Sheet1': df}, ['Sheet1']
    xls = pd.ExcelFile(file)
    sheets = xls.sheet_names
    return {s: xls.parse(s) for s in sheets}, sheets

def show_col_pills(df):
    pills = "".join(f'<span class="col-pill">{c}</span>' for c in df.columns)
    st.markdown(f'<div class="pills-wrap">{pills}</div>', unsafe_allow_html=True)

def excel_uploader(key, hint="Upload .xlsx, .xls, or .csv"):
    st.markdown(f'<div class="upload-zone">📂 {hint}</div>', unsafe_allow_html=True)
    return st.file_uploader("", type=['xlsx','xls','csv'], key=key, label_visibility='collapsed')

def stat_cards(*items):
    """items = list of (label, value, sub, accent_class)"""
    accents = ['accent-purple','accent-cyan','accent-pink','accent-emerald']
    cols = st.columns(len(items))
    for i, (lbl, val, sub, acc) in enumerate(items):
        with cols[i]:
            st.markdown(
                f'<div class="stat-card {acc}">'
                f'<div class="stat-label">{lbl}</div>'
                f'<div class="stat-value">{val}</div>'
                f'<div class="stat-sub">{sub}</div>'
                f'</div>', unsafe_allow_html=True)

def verdict_banner(sig, pass_msg, fail_msg):
    if sig:
        st.markdown(f'<div class="verdict verdict-fail"><span class="verdict-icon">❌</span>{fail_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="verdict verdict-pass"><span class="verdict-icon">✅</span>{pass_msg}</div>', unsafe_allow_html=True)

def card(title, body_fn, icon="◈"):
    st.markdown(f'<div class="card"><div class="card-title">{icon}&nbsp;{title}</div>', unsafe_allow_html=True)
    body_fn()
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">StatLab Pro</div>
  <div class="hero-title">Statistical Tests Calculator</div>
  <div class="hero-sub">
    Professional-grade Z-Score · T-Test · One-Way ANOVA · Chi-Square analysis —
    paste numbers manually or import directly from Excel &amp; CSV.
  </div>
  <div class="hero-chips">
    <span class="chip">scipy.stats</span>
    <span class="chip">numpy</span>
    <span class="chip">pandas</span>
    <span class="chip">matplotlib</span>
    <span class="chip">openpyxl</span>
  </div>
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs(["🔢  Z-Score", "📏  T-Test", "📐  One-Way ANOVA", "🔲  Chi-Square"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Z-SCORE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Z-Score Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Standardise a data point against its distribution — or flag outliers across an entire dataset.</div>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        st.markdown('<div class="card-title">⚙ Configuration</div>', unsafe_allow_html=True)
        src_z = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], horizontal=False, key="z_src")
        alpha_z = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="z_alpha")
        if src_z == "Manual input":
            mode_z = st.radio("Mode", ["Single value", "Full dataset"], horizontal=False, key="z_mode")
        run_z = st.button("▶  Calculate Z-Score", key="z_run", use_container_width=True)

    with c_right:
        st.markdown('<div class="card-title">📥 Input Data</div>', unsafe_allow_html=True)
        col_sel_z = None; data_arr_z = None; mu_z = sigma_z = None

        if src_z == "Manual input":
            if mode_z == "Single value":
                cc1, cc2, cc3 = st.columns(3)
                x_val_z = cc1.number_input("Observed value (x)", value=0.0, format="%.4f", key="zx")
                mu_z    = cc2.number_input("Population mean (μ)", value=0.0, format="%.4f", key="zmu")
                sigma_z = cc3.number_input("Std deviation (σ)", value=1.0, min_value=0.0001, format="%.4f", key="zsig")
            else:
                raw_z = st.text_area("Dataset (comma / space separated)", placeholder="12.5, 14.1, 13.0, 11.8, 15.3 …", height=110, key="z_raw")
                data_arr_z = np.array(parse_data(raw_z)) if raw_z.strip() else None
        else:
            file_z = excel_uploader("z_file", "Drop your Excel / CSV here — each numeric column = one dataset")
            if file_z:
                sheets_z, snames_z = load_excel(file_z)
                s_z = st.selectbox("Sheet", snames_z, key="z_sheet")
                df_xl = sheets_z[s_z].select_dtypes(include='number')
                show_col_pills(df_xl)
                col_sel_z = st.selectbox("Column to analyse", df_xl.columns.tolist(), key="z_col")
                data_arr_z = df_xl[col_sel_z].dropna().values
                st.dataframe(df_xl[[col_sel_z]].describe().T.round(4), use_container_width=True)

    if run_z:
        try:
            is_single = (src_z == "Manual input" and mode_z == "Single value")
            if is_single:
                z = (x_val_z - mu_z) / sigma_z
                p2 = 2*(1-stats.norm.cdf(abs(z)))
                pct = stats.norm.cdf(z)*100
                stat_cards(
                    ("Z-Score",           f"{z:.4f}",   "Standardised distance",   "accent-purple"),
                    ("p-value (2-tail)",  f"{p2:.4f}",  "Under null hypothesis",   "accent-cyan"),
                    ("Percentile",        f"{pct:.2f}%","Below this value",        "accent-pink"),
                )
                verdict_banner(abs(z)>=1.96,
                    f"Not significant — |z| = {abs(z):.4f} < 1.96, p = {p2:.4f} ≥ α = {alpha_z}",
                    f"Significant — |z| = {abs(z):.4f} ≥ 1.96, p = {p2:.4f} < α = {alpha_z}")
                fig, ax = dark_fig(8, 3.5)
                xr = np.linspace(-4,4,400)
                ax.plot(xr, stats.norm.pdf(xr), color='#6366f1', lw=2, label='N(0,1)')
                ax.fill_between(xr, stats.norm.pdf(xr), where=(xr>= 1.96), color='#ef4444', alpha=.3, label='Critical')
                ax.fill_between(xr, stats.norm.pdf(xr), where=(xr<=-1.96), color='#ef4444', alpha=.3)
                ax.axvline(z, color='#06b6d4', lw=2, ls='--', label=f'z = {z:.3f}')
                ax.fill_between(xr, stats.norm.pdf(xr), where=(np.abs(xr)<=abs(z)), alpha=.08, color='#6366f1')
                ax.set_title('Standard Normal Distribution', fontsize=11, pad=10)
                ax.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
                fig_to_st(fig)
            else:
                if data_arr_z is None or len(data_arr_z) == 0:
                    st.warning("⚠ No data found — enter values or upload a file."); st.stop()
                z_scores = stats.zscore(data_arr_z)
                z_crit = stats.norm.ppf(1-alpha_z/2)
                mu_d, sig_d = data_arr_z.mean(), data_arr_z.std(ddof=0)
                n_out = int(np.sum(np.abs(z_scores)>z_crit))
                stat_cards(
                    ("Mean",              f"{mu_d:.4f}",  f"N = {len(data_arr_z)}",    "accent-purple"),
                    ("Std Deviation",     f"{sig_d:.4f}", "Population (ddof=0)",        "accent-cyan"),
                    (f"Outliers |z|>{z_crit:.2f}", f"{n_out}", f"α = {alpha_z}", "accent-pink"),
                )
                lbl_z = col_sel_z if col_sel_z else "Value"
                df_out = pd.DataFrame({lbl_z: data_arr_z, "Z-Score": z_scores.round(4),
                                       "Outlier": np.abs(z_scores) > z_crit})
                st.dataframe(df_out.style.apply(
                    lambda col: ['background: rgba(239,68,68,.12); color:#f87171' if v else '' for v in col],
                    subset=['Outlier']), use_container_width=True)

                fig, (ax1, ax2) = dark_fig(12, 3.8, cols=2)
                colors = ['#ef4444' if abs(z)>z_crit else '#6366f1' for z in z_scores]
                ax1.bar(range(len(z_scores)), z_scores, color=colors, width=.7, alpha=.85)
                ax1.axhline( z_crit, color='#f59e0b', ls='--', lw=1.2, label=f'+{z_crit:.2f}')
                ax1.axhline(-z_crit, color='#f59e0b', ls='--', lw=1.2, label=f'-{z_crit:.2f}')
                patch_out = mpatches.Patch(color='#ef4444', label='Outlier')
                patch_ok  = mpatches.Patch(color='#6366f1', label='Normal')
                ax1.legend(handles=[patch_ok, patch_out], facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
                ax1.set_title('Z-Scores per Data Point', fontsize=10, pad=8)
                ax1.set_xlabel('Index'); ax1.set_ylabel('Z-Score')

                ax2.hist(data_arr_z, bins=min(20,len(data_arr_z)//2+1), color='#6366f1', alpha=.8, edgecolor=BG_DARK, linewidth=.5)
                ax2.axvline(mu_d, color='#06b6d4', lw=2, ls='--', label=f'μ={mu_d:.2f}')
                ax2.axvline(mu_d+z_crit*sig_d, color='#f59e0b', lw=1.5, ls=':', label='+z_crit')
                ax2.axvline(mu_d-z_crit*sig_d, color='#f59e0b', lw=1.5, ls=':')
                ax2.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
                ax2.set_title('Distribution Histogram', fontsize=10, pad=8)
                ax2.set_xlabel(lbl_z); ax2.set_ylabel('Count')
                plt.tight_layout(pad=1.5)
                fig_to_st(fig)
        except Exception as e:
            st.error(f"⚠ Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — T-TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">T-Test</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Compare a sample mean to a target value, or test whether two groups differ significantly.</div>', unsafe_allow_html=True)

    c_left2, c_right2 = st.columns([1, 2], gap="large")

    with c_left2:
        st.markdown('<div class="card-title">⚙ Configuration</div>', unsafe_allow_html=True)
        t_type  = st.radio("Test type", ["One-sample", "Independent two-sample", "Paired"], key="t_type")
        t_src   = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], key="t_src")
        alpha_t = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="t_alpha")
        run_t   = st.button("▶  Run T-Test", key="t_run", use_container_width=True)

    with c_right2:
        st.markdown('<div class="card-title">📥 Input Data</div>', unsafe_allow_html=True)
        g1_t = g2_t = mu0_t = None

        if t_src == "Manual input":
            if t_type == "One-sample":
                mu0_t = st.number_input("Hypothesised mean (μ₀)", value=0.0, format="%.4f", key="t_mu0")
                raw1_t = st.text_area("Sample data", placeholder="10.2, 9.8, 10.5, 11.0, 9.7 …", height=100, key="t_r1")
                g1_t = np.array(parse_data(raw1_t)) if raw1_t.strip() else None
            else:
                lbl_t1 = "Before" if t_type=="Paired" else "Group 1"
                lbl_t2 = "After"  if t_type=="Paired" else "Group 2"
                cc1,cc2 = st.columns(2)
                r1 = cc1.text_area(lbl_t1, placeholder="10, 12, 11 …", height=110, key="t_r1b")
                r2 = cc2.text_area(lbl_t2, placeholder="14, 13, 15 …", height=110, key="t_r2b")
                g1_t = np.array(parse_data(r1)) if r1.strip() else None
                g2_t = np.array(parse_data(r2)) if r2.strip() else None
        else:
            ft = excel_uploader("t_file", "Upload Excel / CSV with one or two numeric columns")
            if ft:
                sh_t, sn_t = load_excel(ft)
                s_t  = st.selectbox("Sheet", sn_t, key="t_sheet")
                df_t = sh_t[s_t].select_dtypes(include='number')
                show_col_pills(df_t)
                nc_t = df_t.columns.tolist()
                if t_type == "One-sample":
                    mu0_t   = st.number_input("Hypothesised mean (μ₀)", value=0.0, format="%.4f", key="t_mu0_xl")
                    ct1     = st.selectbox("Sample column", nc_t, key="t_c1")
                    g1_t    = df_t[ct1].dropna().values
                else:
                    ct1 = st.selectbox("Column 1", nc_t, index=0, key="t_c1b")
                    ct2 = st.selectbox("Column 2", nc_t, index=min(1,len(nc_t)-1), key="t_c2b")
                    g1_t = df_t[ct1].dropna().values
                    g2_t = df_t[ct2].dropna().values
                st.dataframe(df_t.describe().T.round(4), use_container_width=True)

    if run_t:
        try:
            if t_type == "One-sample":
                if g1_t is None: st.warning("Enter sample data."); st.stop()
                t_stat, p_val = stats.ttest_1samp(g1_t, mu0_t)
                dof = len(g1_t)-1; arrs_t = [g1_t]; lbls_t = ["Sample", f"μ₀={mu0_t}"]
            elif t_type == "Independent two-sample":
                if g1_t is None or g2_t is None: st.warning("Enter both groups."); st.stop()
                t_stat, p_val = stats.ttest_ind(g1_t, g2_t)
                dof = len(g1_t)+len(g2_t)-2; arrs_t = [g1_t, g2_t]; lbls_t = ["Group 1","Group 2"]
            else:
                if g1_t is None or g2_t is None: st.warning("Enter both columns."); st.stop()
                if len(g1_t)!=len(g2_t): st.error("Paired test needs equal-length samples."); st.stop()
                t_stat, p_val = stats.ttest_rel(g1_t, g2_t)
                dof = len(g1_t)-1; arrs_t = [g1_t, g2_t]; lbls_t = ["Before","After"]

            t_crit = stats.t.ppf(1-alpha_t/2, dof)
            sig_t  = p_val < alpha_t
            stat_cards(
                ("t-Statistic",     f"{t_stat:.4f}", t_type,              "accent-purple"),
                ("p-value (2-tail)",f"{p_val:.4f}",  f"α = {alpha_t}",   "accent-cyan"),
                ("Degrees of Freedom", str(dof),     "df",                "accent-pink"),
            )
            verdict_banner(sig_t,
                f"No significant difference — p = {p_val:.4f} ≥ α = {alpha_t}",
                f"Significant difference found — p = {p_val:.4f} < α = {alpha_t}")

            rows_t = []
            for lb, arr in zip(lbls_t[:len(arrs_t)], arrs_t):
                rows_t.append({"Group": lb, "N": len(arr), "Mean": round(arr.mean(),4),
                               "Std Dev": round(arr.std(ddof=1),4), "SE": round(arr.std(ddof=1)/np.sqrt(len(arr)),4)})
            st.dataframe(pd.DataFrame(rows_t), use_container_width=True)

            fig, axes_t = dark_fig(12, 3.8, cols=2)
            ax_d, ax_b = axes_t
            xr = np.linspace(stats.t.ppf(.001,dof), stats.t.ppf(.999,dof), 400)
            ax_d.plot(xr, stats.t.pdf(xr,dof), color='#6366f1', lw=2, label=f't-dist (df={dof})')
            ax_d.fill_between(xr, stats.t.pdf(xr,dof), where=(np.abs(xr)>=t_crit), color='#ef4444', alpha=.3, label=f'Critical (α={alpha_t})')
            ax_d.axvline(t_stat, color='#06b6d4', lw=2, ls='--', label=f't={t_stat:.3f}')
            ax_d.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
            ax_d.set_title('t-Distribution', fontsize=10, pad=8)

            if len(arrs_t)==2:
                bp = ax_b.boxplot(arrs_t, patch_artist=True, medianprops=dict(color='#06b6d4',lw=2),
                                  whiskerprops=dict(color=TEXT_DIM), capprops=dict(color=TEXT_DIM),
                                  flierprops=dict(marker='o',color='#ef4444',alpha=.6,markersize=5))
                for patch, color in zip(bp['boxes'], ['#8b5cf6','#06b6d4']):
                    patch.set_facecolor(color); patch.set_alpha(0.5)
                ax_b.set_xticks([1,2]); ax_b.set_xticklabels(lbls_t, color='#cbd5e1')
                ax_b.set_title('Group Distributions', fontsize=10, pad=8)
            else:
                ax_b.hist(arrs_t[0], bins=min(20,len(arrs_t[0])//2+2), color='#6366f1', alpha=.8,
                          edgecolor=BG_DARK, linewidth=.4)
                ax_b.axvline(arrs_t[0].mean(), color='#06b6d4', lw=2, ls='--', label='Mean')
                ax_b.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
                ax_b.set_title('Sample Distribution', fontsize=10, pad=8)
            plt.tight_layout(pad=1.5); fig_to_st(fig)
        except Exception as e:
            st.error(f"⚠ Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANOVA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">One-Way ANOVA</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Test whether the means of <strong>3 or more independent groups</strong> differ significantly.</div>', unsafe_allow_html=True)

    c_left3, c_right3 = st.columns([1, 2], gap="large")

    with c_left3:
        st.markdown('<div class="card-title">⚙ Configuration</div>', unsafe_allow_html=True)
        a_src    = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], key="a_src")
        alpha_a  = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="anova_alpha")
        run_a    = st.button("▶  Run ANOVA", key="anova_btn", use_container_width=True)

    with c_right3:
        st.markdown('<div class="card-title">📥 Input Data</div>', unsafe_allow_html=True)
        raw_groups_a = []; group_names_a = []

        if a_src == "Manual input":
            n_gr = int(st.number_input("Number of groups", min_value=2, max_value=10, value=3, step=1))
            gcols = st.columns(min(n_gr, 4))
            for i in range(n_gr):
                with gcols[i % 4]:
                    nm = st.text_input(f"Label {i+1}", value=f"Group {i+1}", key=f"gn_{i}")
                    rw = st.text_area(f"Data — {nm}", placeholder="5,7,6,8", key=f"gd_{i}", height=80)
                    group_names_a.append(nm); raw_groups_a.append(rw)
        else:
            fa = excel_uploader("a_file", "Upload Excel / CSV — select columns that represent each group")
            if fa:
                sh_a, sn_a = load_excel(fa)
                s_a = st.selectbox("Sheet", sn_a, key="a_sheet")
                df_a = sh_a[s_a].select_dtypes(include='number')
                show_col_pills(df_a)
                sel_a = st.multiselect("Select group columns (≥ 2)", df_a.columns.tolist(), key="a_cols")
                group_names_a = sel_a
                raw_groups_a  = [",".join(map(str, df_a[sc].dropna().tolist())) for sc in sel_a]
                if sel_a:
                    st.dataframe(df_a[sel_a].describe().T.round(4), use_container_width=True)

    if run_a:
        try:
            parsed_a = [np.array(parse_data(g)) for g in raw_groups_a if g.strip()]
            if len(parsed_a) < 2: st.warning("Fill in at least 2 groups."); st.stop()
            f_stat, p_val = stats.f_oneway(*parsed_a)
            df_bet = len(parsed_a)-1
            df_wit = sum(len(g) for g in parsed_a)-len(parsed_a)
            eta_sq = (f_stat*df_bet) / (f_stat*df_bet + df_wit)
            stat_cards(
                ("F-Statistic",  f"{f_stat:.4f}", f"df₁={df_bet}, df₂={df_wit}", "accent-purple"),
                ("p-value",      f"{p_val:.4f}",  f"α = {alpha_a}",              "accent-cyan"),
                ("η² Effect",    f"{eta_sq:.4f}", "Effect size (eta-squared)",   "accent-pink"),
            )
            verdict_banner(p_val<alpha_a,
                f"No significant difference — p = {p_val:.4f} ≥ α = {alpha_a}",
                f"Significant difference between group means — p = {p_val:.4f} < α = {alpha_a}")

            summary_a = pd.DataFrame({
                "Group":   group_names_a[:len(parsed_a)],
                "N":       [len(g) for g in parsed_a],
                "Mean":    [round(g.mean(),4) for g in parsed_a],
                "Std Dev": [round(g.std(ddof=1),4) for g in parsed_a],
                "Min":     [round(g.min(),4) for g in parsed_a],
                "Max":     [round(g.max(),4) for g in parsed_a],
            })
            st.dataframe(summary_a, use_container_width=True)

            fig, (ax_box, ax_bar) = dark_fig(12, 4, cols=2)
            bp = ax_box.boxplot(parsed_a, patch_artist=True, notch=False,
                                medianprops=dict(color='#06b6d4', linewidth=2),
                                whiskerprops=dict(color=TEXT_DIM), capprops=dict(color=TEXT_DIM),
                                flierprops=dict(marker='o', color='#ef4444', alpha=.6, markersize=4))
            for patch, color in zip(bp['boxes'], PALETTE):
                patch.set_facecolor(color); patch.set_alpha(0.55)
            ax_box.set_xticks(range(1,len(parsed_a)+1))
            ax_box.set_xticklabels(group_names_a[:len(parsed_a)], color='#cbd5e1', fontsize=8.5)
            ax_box.set_title('Group Distributions', fontsize=10, pad=8)
            ax_box.set_ylabel('Value')

            means_a = [g.mean() for g in parsed_a]
            sems_a  = [g.std(ddof=1)/np.sqrt(len(g)) for g in parsed_a]
            bars = ax_bar.bar(range(len(means_a)), means_a, color=PALETTE[:len(means_a)],
                              alpha=.75, width=.6, edgecolor=BG_DARK)
            ax_bar.errorbar(range(len(means_a)), means_a, yerr=sems_a, fmt='none',
                            color='#e2e8f0', capsize=5, lw=1.5)
            ax_bar.set_xticks(range(len(means_a)))
            ax_bar.set_xticklabels(group_names_a[:len(parsed_a)], color='#cbd5e1', fontsize=8.5)
            ax_bar.set_title('Group Means ± SE', fontsize=10, pad=8)
            ax_bar.set_ylabel('Mean')
            plt.tight_layout(pad=1.5); fig_to_st(fig)
        except Exception as e:
            st.error(f"⚠ Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHI-SQUARE
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Chi-Square Test</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Test whether observed frequencies fit an expected distribution, or whether two categorical variables are independent.</div>', unsafe_allow_html=True)

    c_left4, c_right4 = st.columns([1, 2], gap="large")

    with c_left4:
        st.markdown('<div class="card-title">⚙ Configuration</div>', unsafe_allow_html=True)
        chi_mode  = st.radio("Test type", ["Goodness of Fit", "Test of Independence"], key="chi_mode")
        chi_src   = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], key="chi_src")
        alpha_chi = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="chi_alpha")
        if chi_mode == "Goodness of Fit":
            run_chi = st.button("▶  Run Goodness of Fit", key="chi_gof_btn", use_container_width=True)
        else:
            run_chi = st.button("▶  Run Independence Test", key="chi_ind_btn", use_container_width=True)

    with c_right4:
        st.markdown('<div class="card-title">📥 Input Data</div>', unsafe_allow_html=True)

        if chi_mode == "Goodness of Fit":
            obs_raw_chi = exp_raw_chi = ""
            if chi_src == "Manual input":
                obs_raw_chi = st.text_area("Observed counts", placeholder="30, 20, 25, 25", height=80, key="chi_obs")
                exp_raw_chi = st.text_area("Expected counts (blank = uniform)", placeholder="25, 25, 25, 25", height=80, key="chi_exp")
            else:
                fc = excel_uploader("chi_gof_file", "One column = observed counts; second column = expected (optional)")
                if fc:
                    sh_c, sn_c = load_excel(fc)
                    s_c = st.selectbox("Sheet", sn_c, key="chi_sheet_gof")
                    df_c = sh_c[s_c].select_dtypes(include='number')
                    show_col_pills(df_c)
                    nc_c = df_c.columns.tolist()
                    obs_c = st.selectbox("Observed column", nc_c, key="chi_obs_col")
                    exp_c = st.selectbox("Expected column (select same to skip)", nc_c, key="chi_exp_col")
                    obs_raw_chi = ",".join(map(str, df_c[obs_c].dropna().tolist()))
                    exp_raw_chi = "" if exp_c==obs_c else ",".join(map(str, df_c[exp_c].dropna().tolist()))
                    st.dataframe(df_c[[obs_c]].describe().T.round(2), use_container_width=True)

            if run_chi:
                try:
                    obs_chi = np.array(parse_data(obs_raw_chi))
                    exp_chi = (np.array(parse_data(exp_raw_chi)) if exp_raw_chi.strip()
                               else np.full(len(obs_chi), obs_chi.sum()/len(obs_chi)))
                    if len(exp_chi)!=len(obs_chi): st.error("Observed & expected must have same length."); st.stop()
                    chi2, p_val = stats.chisquare(obs_chi, f_exp=exp_chi)
                    dof_chi = len(obs_chi)-1
                    stat_cards(
                        ("χ² Statistic", f"{chi2:.4f}", "Test statistic",       "accent-purple"),
                        ("p-value",      f"{p_val:.4f}", f"α = {alpha_chi}",    "accent-cyan"),
                        ("df",           str(dof_chi),  "Degrees of freedom",   "accent-pink"),
                    )
                    verdict_banner(p_val<alpha_chi,
                        f"Observed fits expected distribution — p = {p_val:.4f} ≥ α = {alpha_chi}",
                        f"Observed does NOT fit expected — p = {p_val:.4f} < α = {alpha_chi}")

                    cats = [f"Cat {i+1}" for i in range(len(obs_chi))]
                    residuals = (obs_chi - exp_chi) / np.sqrt(exp_chi)

                    fig, (ax_bar2, ax_res) = dark_fig(12, 3.8, cols=2)
                    x = np.arange(len(cats))
                    ax_bar2.bar(x-.22, obs_chi, .42, label='Observed', color='#6366f1', alpha=.85, edgecolor=BG_DARK)
                    ax_bar2.bar(x+.22, exp_chi, .42, label='Expected', color='#06b6d4', alpha=.85, edgecolor=BG_DARK)
                    ax_bar2.set_xticks(x); ax_bar2.set_xticklabels(cats, color='#cbd5e1', fontsize=9)
                    ax_bar2.set_title('Observed vs Expected', fontsize=10, pad=8)
                    ax_bar2.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)

                    rcolors = ['#ef4444' if abs(r)>2 else '#10b981' for r in residuals]
                    ax_res.bar(range(len(residuals)), residuals, color=rcolors, alpha=.85, edgecolor=BG_DARK, width=.6)
                    ax_res.axhline(2,  color='#f59e0b', ls='--', lw=1, label='±2 (flag)')
                    ax_res.axhline(-2, color='#f59e0b', ls='--', lw=1)
                    ax_res.set_xticks(range(len(cats))); ax_res.set_xticklabels(cats, color='#cbd5e1', fontsize=9)
                    ax_res.set_title('Pearson Residuals', fontsize=10, pad=8)
                    ax_res.legend(facecolor=BG_CARD2, edgecolor=BORDER, labelcolor='#cbd5e1', fontsize=8)
                    plt.tight_layout(pad=1.5); fig_to_st(fig)
                except Exception as e:
                    st.error(f"⚠ Error: {e}")

        else:  # Test of Independence
            rows_raw_chi = rl_chi = cl_chi = ""

            if chi_src == "Manual input":
                st.caption("One row per line, comma-separated.  e.g.  10, 20, 30 ↵ 15, 25, 10")
                rows_raw_chi = st.text_area("Contingency table", height=130, key="chi_cont",
                                            placeholder="10, 20, 30\n15, 25, 10")
                rl_chi = st.text_input("Row labels (optional)", placeholder="Male, Female", key="chi_rl")
                cl_chi = st.text_input("Col labels (optional)", placeholder="Low, Medium, High", key="chi_cl")
            else:
                fc2 = excel_uploader("chi_ind_file", "Upload contingency table — numeric columns = column categories")
                if fc2:
                    sh_c2, sn_c2 = load_excel(fc2)
                    s_c2 = st.selectbox("Sheet", sn_c2, key="chi_sheet_ind")
                    df_c2 = sh_c2[s_c2]
                    show_col_pills(df_c2)
                    nm2 = df_c2.select_dtypes(include='number')
                    sel_c2 = st.multiselect("Numeric columns forming the table", nm2.columns.tolist(), key="chi_ind_cols")
                    rl_src = st.selectbox("Row label column (optional)", ["— none —"]+df_c2.columns.tolist(), key="chi_rl_col")
                    if sel_c2:
                        sub2 = nm2[sel_c2].dropna()
                        rows_raw_chi = "\n".join(",".join(map(str,r)) for r in sub2.values.tolist())
                        cl_chi = ",".join(sel_c2)
                        rl_chi = ",".join(str(v) for v in df_c2[rl_src].dropna().tolist()) if rl_src!="— none —" else ""
                        st.dataframe(sub2, use_container_width=True)

            if run_chi:
                try:
                    lines_c = [l.strip() for l in rows_raw_chi.strip().split('\n') if l.strip()]
                    tbl = np.array([[float(v) for v in parse_data(l)] for l in lines_c])
                    chi2, p_val, dof_c, expected_c = stats.chi2_contingency(tbl)
                    v_stat = np.sqrt(chi2/(tbl.sum()*(min(tbl.shape)-1)))

                    stat_cards(
                        ("χ² Statistic",    f"{chi2:.4f}",  "Test statistic",         "accent-purple"),
                        ("p-value",         f"{p_val:.4f}", f"α = {alpha_chi}",        "accent-cyan"),
                        ("Cramér's V",      f"{v_stat:.4f}","Effect size",             "accent-pink"),
                        ("df",              str(dof_c),     "Degrees of freedom",      "accent-emerald"),
                    )
                    verdict_banner(p_val<alpha_chi,
                        f"Variables appear independent — p = {p_val:.4f} ≥ α = {alpha_chi}",
                        f"Significant association found — p = {p_val:.4f} < α = {alpha_chi}")

                    nr = tbl.shape[0]; nc_dim = tbl.shape[1]
                    r_lbls = ([s.strip() for s in rl_chi.split(',')] if rl_chi.strip()
                               else [f"Row {i+1}" for i in range(nr)])[:nr]
                    c_lbls = ([s.strip() for s in cl_chi.split(',')] if cl_chi.strip()
                               else [f"Col {j+1}" for j in range(nc_dim)])[:nc_dim]
                    while len(r_lbls)<nr: r_lbls.append(f"Row {len(r_lbls)+1}")
                    while len(c_lbls)<nc_dim: c_lbls.append(f"Col {len(c_lbls)+1}")

                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.markdown("**Observed**")
                        st.dataframe(pd.DataFrame(tbl, index=r_lbls, columns=c_lbls), use_container_width=True)
                    with cc2:
                        st.markdown("**Expected**")
                        st.dataframe(pd.DataFrame(expected_c.round(2), index=r_lbls, columns=c_lbls), use_container_width=True)

                    resid = (tbl - expected_c) / np.sqrt(expected_c)
                    fig, axes_chi = dark_fig(14, 3.8, cols=3)
                    ax_obs, ax_exp, ax_res = axes_chi
                    for ax, mat, title, cmap_name in [
                        (ax_obs, tbl,         'Observed',          'Blues'),
                        (ax_exp, expected_c,  'Expected',          'Purples'),
                        (ax_res, resid,       'Standardised Resid','RdYlGn'),
                    ]:
                        im = ax.imshow(mat, cmap=cmap_name, aspect='auto')
                        ax.set_xticks(range(len(c_lbls))); ax.set_xticklabels(c_lbls, color='#cbd5e1', fontsize=8, rotation=30, ha='right')
                        ax.set_yticks(range(len(r_lbls))); ax.set_yticklabels(r_lbls, color='#cbd5e1', fontsize=8)
                        for i in range(mat.shape[0]):
                            for j in range(mat.shape[1]):
                                ax.text(j, i, f'{mat[i,j]:.1f}', ha='center', va='center',
                                        color='white', fontsize=8, fontweight='bold')
                        ax.set_title(title, color='#e2e8f0', fontsize=10, pad=8)
                        plt.colorbar(im, ax=ax).ax.yaxis.set_tick_params(color=TEXT_DIM, labelcolor=TEXT_DIM)
                    plt.tight_layout(pad=1.5); fig_to_st(fig)
                except Exception as e:
                    st.error(f"⚠ Error parsing table: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider"><div class="footer">StatLab Pro · Z-Score · T-Test · ANOVA · Chi-Square · Built with Streamlit + scipy</div>', unsafe_allow_html=True)
