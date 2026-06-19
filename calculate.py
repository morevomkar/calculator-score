Overwrite the file with the full updated app

Overwrite the file with the full updated app
bash

cat > /mnt/user-data/outputs/statistical_tests_app.py << 'PYEOF'
import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import re

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Statistical Tests Calculator", page_icon="📊", layout="wide")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0f1117; color: #e8eaf0; }
    h1,h2,h3 { font-family:'Inter',sans-serif; font-weight:700; }
    .hero-title {
        font-size:2.6rem; font-weight:700;
        background:linear-gradient(135deg,#6ee7f7 0%,#a78bfa 50%,#f472b6 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        margin-bottom:0.25rem;
    }
    .hero-sub { font-size:1.05rem; color:#94a3b8; margin-bottom:1.5rem; }
    .result-card {
        background:#1e2130; border:1px solid #2e3350; border-radius:12px;
        padding:1.4rem 1.8rem; margin-top:1.1rem;
    }
    .result-card h4 { color:#a78bfa; font-size:0.82rem; text-transform:uppercase; letter-spacing:.1em; margin-bottom:.4rem; }
    .result-value { font-family:'JetBrains Mono',monospace; font-size:1.55rem; font-weight:600; color:#6ee7f7; }
    .verdict-pass {
        background:#0d2b1f; border:1px solid #22c55e; border-radius:8px;
        padding:.85rem 1.1rem; color:#4ade80; font-weight:600; margin-top:1rem;
    }
    .verdict-fail {
        background:#2b0d0d; border:1px solid #ef4444; border-radius:8px;
        padding:.85rem 1.1rem; color:#f87171; font-weight:600; margin-top:1rem;
    }
    .upload-box {
        background:#161b2e; border:1.5px dashed #3b4270; border-radius:10px;
        padding:1rem 1.2rem; margin-bottom:1rem;
    }
    .upload-box p { color:#94a3b8; font-size:0.85rem; margin:0; }
    .stTabs [data-baseweb="tab"] { font-weight:600; font-size:.93rem; color:#94a3b8; border-radius:8px 8px 0 0; }
    .stTabs [aria-selected="true"] { color:#a78bfa !important; border-bottom:2px solid #a78bfa !important; }
    .stTextArea textarea, .stNumberInput input {
        background:#1e2130 !important; border:1px solid #2e3350 !important;
        color:#e8eaf0 !important; border-radius:8px !important; font-family:'JetBrains Mono',monospace !important;
    }
    label, .stSelectbox label { color:#94a3b8 !important; font-size:.87rem !important; font-weight:500 !important; }
    .section-divider { border:none; border-top:1px solid #2e3350; margin:1.4rem 0; }
    .badge {
        display:inline-block; background:#1e2130; border:1px solid #2e3350; border-radius:20px;
        padding:.22rem .7rem; font-size:.76rem; color:#94a3b8; margin-right:.35rem; margin-bottom:.9rem;
    }
    .col-pill {
        display:inline-block; background:#1e2130; border:1px solid #3b4270; border-radius:6px;
        padding:.18rem .55rem; font-size:.78rem; color:#6ee7f7; margin:.2rem .2rem .2rem 0; cursor:default;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def parse_data(text):
    tokens = re.split(r'[\s,]+', text.strip())
    return [float(t) for t in tokens if t]

def dark_fig(w=7, h=3.6):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#1e2130')
    for sp in ax.spines.values(): sp.set_color('#2e3350')
    ax.tick_params(colors='#94a3b8', labelsize=9)
    ax.xaxis.label.set_color('#94a3b8')
    ax.yaxis.label.set_color('#94a3b8')
    ax.title.set_color('#e8eaf0')
    return fig, ax

def fig_to_st(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=140)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

def load_excel(file):
    """Return (df, sheet_names) from uploaded Excel/CSV."""
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
        return {'Sheet1': df}, ['Sheet1']
    xls = pd.ExcelFile(file)
    sheets = xls.sheet_names
    return {s: xls.parse(s) for s in sheets}, sheets

def show_col_pills(df):
    pills = " ".join(f'<span class="col-pill">{c}</span>' for c in df.columns)
    st.markdown(f"**Columns:** {pills}", unsafe_allow_html=True)

def excel_uploader(key, help_text="Upload .xlsx, .xls, or .csv"):
    st.markdown(f'<div class="upload-box"><p>📂 {help_text}</p></div>', unsafe_allow_html=True)
    return st.file_uploader("", type=['xlsx','xls','csv'], key=key, label_visibility='collapsed')

PALETTE = ['#a78bfa','#f472b6','#6ee7f7','#34d399','#fb923c','#facc15','#38bdf8','#e879f9','#4ade80','#f87171']

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Statistical Tests Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Z-Score · T-Test · One-Way ANOVA · Chi-Square &nbsp;|&nbsp; Manual input <em>or</em> Excel/CSV import</div>', unsafe_allow_html=True)
st.markdown('<span class="badge">scipy.stats</span><span class="badge">numpy</span><span class="badge">pandas</span><span class="badge">matplotlib</span>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔢  Z-Score", "📏  T-Test", "📐  ANOVA", "🔲  Chi-Square"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Z-SCORE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Z-Score Calculator")
    src = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], horizontal=True, key="z_src")

    if src == "Manual input":
        mode = st.radio("Mode", ["Single value", "Full dataset"], horizontal=True, key="z_mode")
        if mode == "Single value":
            c1,c2,c3 = st.columns(3)
            x_val = c1.number_input("Observed value (x)", value=0.0, format="%.4f")
            mu    = c2.number_input("Population mean (μ)", value=0.0, format="%.4f")
            sigma = c3.number_input("Std deviation (σ)", value=1.0, min_value=0.0001, format="%.4f")
            data_arr = None
        else:
            raw = st.text_area("Dataset (comma/space separated)", placeholder="12.5, 14.1, 13.0, 11.8 …", height=90)
            data_arr = np.array(parse_data(raw)) if raw.strip() else None
            mu = sigma = None
        alpha_z = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="z_alpha")
        col_sel = None

    else:
        file = excel_uploader("z_file", "Upload your Excel/CSV — each numeric column treated as a dataset")
        col_sel = None; data_arr = None; mu = sigma = None
        alpha_z = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="z_alpha_xl")
        if file:
            sheets, snames = load_excel(file)
            sheet = st.selectbox("Sheet", snames, key="z_sheet")
            df_xl = sheets[sheet].select_dtypes(include='number')
            show_col_pills(df_xl)
            col_sel = st.selectbox("Column to analyse", df_xl.columns.tolist(), key="z_col")
            data_arr = df_xl[col_sel].dropna().values
            st.dataframe(df_xl[[col_sel]].describe().T.round(4), use_container_width=True)

    if st.button("Calculate Z-Score", key="z_run"):
        try:
            if src == "Manual input" and 'mode' in dir() and mode == "Single value":
                z = (x_val - mu) / sigma
                p2 = 2*(1-stats.norm.cdf(abs(z)))
                pct = stats.norm.cdf(z)*100
                c1,c2,c3 = st.columns(3)
                c1.markdown(f'<div class="result-card"><h4>Z-Score</h4><div class="result-value">{z:.4f}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="result-card"><h4>p-value (two-tailed)</h4><div class="result-value">{p2:.4f}</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="result-card"><h4>Percentile</h4><div class="result-value">{pct:.2f}%</div></div>', unsafe_allow_html=True)
                verdict = "✅ Not significant (|z| < 1.96)" if abs(z)<1.96 else "❌ Significant (|z| ≥ 1.96)"
                st.markdown(f'<div class="{"verdict-pass" if abs(z)<1.96 else "verdict-fail"}">{verdict}</div>', unsafe_allow_html=True)
                fig,ax = dark_fig()
                xr = np.linspace(-4,4,400)
                ax.plot(xr, stats.norm.pdf(xr), color='#a78bfa', lw=2)
                ax.fill_between(xr, stats.norm.pdf(xr), where=(np.abs(xr)>=1.96), color='#ef4444', alpha=.35, label='Critical region')
                ax.axvline(z, color='#6ee7f7', lw=2, ls='--', label=f'z={z:.3f}')
                ax.legend(facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
                ax.set_title('Standard Normal Distribution'); fig_to_st(fig)
            else:
                if data_arr is None or len(data_arr)==0:
                    st.warning("No data to analyse."); st.stop()
                z_scores = stats.zscore(data_arr)
                z_crit = stats.norm.ppf(1-alpha_z/2)
                mu_d, sig_d = data_arr.mean(), data_arr.std(ddof=0)
                c1,c2,c3 = st.columns(3)
                c1.markdown(f'<div class="result-card"><h4>Mean</h4><div class="result-value">{mu_d:.4f}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="result-card"><h4>Std Dev</h4><div class="result-value">{sig_d:.4f}</div></div>', unsafe_allow_html=True)
                n_out = int(np.sum(np.abs(z_scores)>z_crit))
                c3.markdown(f'<div class="result-card"><h4>Outliers (|z|>{z_crit:.2f})</h4><div class="result-value">{n_out}</div></div>', unsafe_allow_html=True)
                lbl = col_sel if col_sel else "Value"
                df_out = pd.DataFrame({lbl: data_arr, "Z-Score": z_scores.round(4), "Outlier": np.abs(z_scores)>z_crit})
                st.dataframe(df_out, use_container_width=True)
                fig,ax = dark_fig(8,3.6)
                colors = ['#ef4444' if abs(z)>z_crit else '#a78bfa' for z in z_scores]
                ax.bar(range(len(z_scores)), z_scores, color=colors, width=.7)
                ax.axhline(z_crit, color='#f472b6', ls='--', lw=1, label=f'±{z_crit:.2f}')
                ax.axhline(-z_crit, color='#f472b6', ls='--', lw=1)
                patch = mpatches.Patch(color='#ef4444', label='Outlier')
                ax.legend(handles=[patch], facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
                ax.set_title('Z-Scores per Data Point'); fig_to_st(fig)
        except Exception as e:
            st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — T-TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### T-Test")
    t_type = st.radio("Test type", ["One-sample", "Independent two-sample", "Paired"], horizontal=True, key="t_type")
    t_src  = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], horizontal=True, key="t_src")
    alpha_t = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="t_alpha")

    g1_arr = g2_arr = mu0 = None

    if t_src == "Manual input":
        if t_type == "One-sample":
            mu0 = st.number_input("Hypothesised mean (μ₀)", value=0.0, format="%.4f")
            raw1 = st.text_area("Sample data", placeholder="10.2, 9.8, 10.5, 11.0, 9.7 …", height=90, key="t_raw1")
            g1_arr = np.array(parse_data(raw1)) if raw1.strip() else None
        else:
            c1, c2 = st.columns(2)
            lbl1 = "Before" if t_type=="Paired" else "Group 1"
            lbl2 = "After"  if t_type=="Paired" else "Group 2"
            raw1 = c1.text_area(lbl1, placeholder="10, 12, 11 …", height=100, key="t_raw1b")
            raw2 = c2.text_area(lbl2, placeholder="14, 13, 15 …", height=100, key="t_raw2b")
            g1_arr = np.array(parse_data(raw1)) if raw1.strip() else None
            g2_arr = np.array(parse_data(raw2)) if raw2.strip() else None

    else:
        file_t = excel_uploader("t_file", "Upload Excel/CSV with one or two numeric columns")
        if file_t:
            sheets_t, snames_t = load_excel(file_t)
            sheet_t = st.selectbox("Sheet", snames_t, key="t_sheet")
            df_t = sheets_t[sheet_t].select_dtypes(include='number')
            show_col_pills(df_t)
            num_cols = df_t.columns.tolist()
            if t_type == "One-sample":
                mu0   = st.number_input("Hypothesised mean (μ₀)", value=0.0, format="%.4f", key="t_mu0_xl")
                col_t1 = st.selectbox("Sample column", num_cols, key="t_col1")
                g1_arr = df_t[col_t1].dropna().values
            else:
                col_t1 = st.selectbox("Column 1", num_cols, index=0, key="t_col1b")
                col_t2 = st.selectbox("Column 2", num_cols, index=min(1,len(num_cols)-1), key="t_col2b")
                g1_arr = df_t[col_t1].dropna().values
                g2_arr = df_t[col_t2].dropna().values
            st.dataframe(df_t.describe().T.round(4), use_container_width=True)

    if st.button("Run T-Test", key="t_run"):
        try:
            if t_type == "One-sample":
                if g1_arr is None: st.warning("Enter sample data."); st.stop()
                t_stat, p_val = stats.ttest_1samp(g1_arr, mu0)
                dof = len(g1_arr)-1
                labels = ["Sample mean", f"μ₀ = {mu0}"]
                arrs   = [g1_arr]
            elif t_type == "Independent two-sample":
                if g1_arr is None or g2_arr is None: st.warning("Enter data for both groups."); st.stop()
                t_stat, p_val = stats.ttest_ind(g1_arr, g2_arr)
                dof = len(g1_arr)+len(g2_arr)-2
                labels = ["Group 1","Group 2"]; arrs = [g1_arr, g2_arr]
            else:
                if g1_arr is None or g2_arr is None: st.warning("Enter data for both columns."); st.stop()
                if len(g1_arr)!=len(g2_arr): st.error("Paired test requires equal-length samples."); st.stop()
                t_stat, p_val = stats.ttest_rel(g1_arr, g2_arr)
                dof = len(g1_arr)-1
                labels = ["Before","After"]; arrs = [g1_arr, g2_arr]

            c1,c2,c3 = st.columns(3)
            c1.markdown(f'<div class="result-card"><h4>t-Statistic</h4><div class="result-value">{t_stat:.4f}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="result-card"><h4>p-value (two-tailed)</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="result-card"><h4>Degrees of Freedom</h4><div class="result-value">{dof}</div></div>', unsafe_allow_html=True)

            t_crit = stats.t.ppf(1-alpha_t/2, dof)
            sig = p_val < alpha_t
            verdict = f"❌ Reject H₀ — Significant difference (p={p_val:.4f} < α={alpha_t})" if sig else f"✅ Fail to reject H₀ — No significant difference (p={p_val:.4f} ≥ α={alpha_t})"
            st.markdown(f'<div class="{"verdict-fail" if sig else "verdict-pass"}">{verdict}</div>', unsafe_allow_html=True)

            # Summary table
            rows = []
            for lbl, arr in zip(labels[:len(arrs)], arrs):
                rows.append({"Group": lbl, "N": len(arr), "Mean": round(arr.mean(),4),
                              "Std Dev": round(arr.std(ddof=1),4), "SE": round(arr.std(ddof=1)/np.sqrt(len(arr)),4)})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

            # Distribution plot
            fig, ax = dark_fig(8, 3.5)
            xr = np.linspace(-4, 4, 400)
            ax.plot(xr, stats.t.pdf(xr, dof), color='#a78bfa', lw=2, label=f't-dist (df={dof})')
            ax.fill_between(xr, stats.t.pdf(xr, dof), where=(np.abs(xr)>=t_crit), color='#ef4444', alpha=.35, label=f'Critical (α={alpha_t})')
            ax.axvline(t_stat, color='#6ee7f7', lw=2, ls='--', label=f't={t_stat:.3f}')
            ax.legend(facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
            ax.set_title('t-Distribution'); fig_to_st(fig)

            # Box / bar chart
            if len(arrs) == 2:
                fig2, ax2 = dark_fig(7, 3.5)
                bp = ax2.boxplot(arrs, patch_artist=True, medianprops=dict(color='#6ee7f7', lw=2))
                for patch, color in zip(bp['boxes'], PALETTE):
                    patch.set_facecolor(color); patch.set_alpha(0.6)
                for w in bp['whiskers']: w.set_color('#94a3b8')
                for c in bp['caps']:     c.set_color('#94a3b8')
                ax2.set_xticks([1,2]); ax2.set_xticklabels(labels, color='#e8eaf0')
                ax2.set_title('Group Distributions'); fig_to_st(fig2)

        except Exception as e:
            st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANOVA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### One-Way ANOVA")
    st.markdown("Test whether **3 or more group means** differ significantly.")
    a_src = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], horizontal=True, key="a_src")
    alpha_anova = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="anova_alpha")

    parsed_groups = []
    group_names   = []

    if a_src == "Manual input":
        n_groups = st.number_input("Number of groups", min_value=2, max_value=10, value=3, step=1)
        cols = st.columns(min(int(n_groups), 4))
        raw_groups = []
        for i in range(int(n_groups)):
            with cols[i % 4]:
                name = st.text_input(f"Group {i+1} label", value=f"Group {i+1}", key=f"gname_{i}")
                raw  = st.text_area(f"Data for {name}", placeholder="5, 7, 6.5, 8", key=f"gdata_{i}", height=80)
                group_names.append(name); raw_groups.append(raw)
    else:
        file_a = excel_uploader("a_file", "Upload Excel/CSV — select which columns represent groups")
        if file_a:
            sheets_a, snames_a = load_excel(file_a)
            sheet_a = st.selectbox("Sheet", snames_a, key="a_sheet")
            df_a = sheets_a[sheet_a].select_dtypes(include='number')
            show_col_pills(df_a)
            selected_cols = st.multiselect("Select group columns (≥ 2)", df_a.columns.tolist(), key="a_cols")
            group_names = selected_cols
            raw_groups  = []
            for sc in selected_cols:
                raw_groups.append(",".join(map(str, df_a[sc].dropna().tolist())))
            st.dataframe(df_a[selected_cols].describe().T.round(4) if selected_cols else pd.DataFrame(), use_container_width=True)

    if st.button("Run ANOVA", key="anova_btn"):
        try:
            parsed_groups = [np.array(parse_data(g)) for g in raw_groups if g.strip()]
            if len(parsed_groups) < 2:
                st.warning("Fill in at least 2 groups."); st.stop()
            f_stat, p_val = stats.f_oneway(*parsed_groups)
            df_between = len(parsed_groups)-1
            df_within  = sum(len(g) for g in parsed_groups)-len(parsed_groups)
            c1,c2,c3 = st.columns(3)
            c1.markdown(f'<div class="result-card"><h4>F-Statistic</h4><div class="result-value">{f_stat:.4f}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="result-card"><h4>df (between / within)</h4><div class="result-value">{df_between} / {df_within}</div></div>', unsafe_allow_html=True)
            sig = p_val < alpha_anova
            verdict = ("❌ Reject H₀ — Significant difference between group means." if sig else
                       "✅ Fail to reject H₀ — No significant difference between group means.")
            st.markdown(f'<div class="{"verdict-fail" if sig else "verdict-pass"}">{verdict}</div>', unsafe_allow_html=True)
            summary = pd.DataFrame({
                "Group":   group_names[:len(parsed_groups)],
                "N":       [len(g) for g in parsed_groups],
                "Mean":    [round(g.mean(),4) for g in parsed_groups],
                "Std Dev": [round(g.std(ddof=1),4) for g in parsed_groups],
                "Min":     [g.min() for g in parsed_groups],
                "Max":     [g.max() for g in parsed_groups],
            })
            st.dataframe(summary, use_container_width=True)
            fig, ax = dark_fig(8, 4)
            bp = ax.boxplot(parsed_groups, patch_artist=True, notch=False,
                            medianprops=dict(color='#6ee7f7', linewidth=2))
            for patch, color in zip(bp['boxes'], PALETTE):
                patch.set_facecolor(color); patch.set_alpha(0.6)
            for w in bp['whiskers']: w.set_color('#94a3b8')
            for c in bp['caps']:     c.set_color('#94a3b8')
            for f in bp['fliers']:   f.set(marker='o', color='#ef4444', alpha=.6)
            ax.set_xticks(range(1, len(parsed_groups)+1))
            ax.set_xticklabels(group_names[:len(parsed_groups)], color='#e8eaf0', fontsize=9)
            ax.set_title('Group Distributions (Box Plot)'); ax.set_ylabel('Value')
            fig_to_st(fig)
        except Exception as e:
            st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHI-SQUARE
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Chi-Square Test")
    chi_mode = st.radio("Test type", ["Goodness of Fit", "Test of Independence"], horizontal=True, key="chi_mode")
    chi_src  = st.radio("Data source", ["Manual input", "Upload Excel / CSV"], horizontal=True, key="chi_src")
    alpha_chi = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="chi_alpha")

    if chi_mode == "Goodness of Fit":
        # ── Goodness of Fit ──────────────────────────────────────────────
        observed = expected_arr = None

        if chi_src == "Manual input":
            obs_raw = st.text_area("Observed counts", placeholder="30, 20, 25, 25", height=80, key="chi_obs")
            exp_raw = st.text_area("Expected counts (blank = uniform)", placeholder="25, 25, 25, 25", height=80, key="chi_exp")
        else:
            file_chi = excel_uploader("chi_gof_file", "Upload Excel/CSV — one column = observed counts, another (optional) = expected counts")
            obs_raw = exp_raw = ""
            if file_chi:
                sheets_chi, snames_chi = load_excel(file_chi)
                sheet_chi = st.selectbox("Sheet", snames_chi, key="chi_sheet_gof")
                df_chi = sheets_chi[sheet_chi].select_dtypes(include='number')
                show_col_pills(df_chi)
                num_cols_chi = df_chi.columns.tolist()
                obs_col = st.selectbox("Observed counts column", num_cols_chi, key="chi_obs_col")
                exp_col = st.selectbox("Expected counts column (optional — select same as observed to skip)", num_cols_chi, key="chi_exp_col")
                obs_raw = ",".join(map(str, df_chi[obs_col].dropna().tolist()))
                exp_raw = "" if exp_col == obs_col else ",".join(map(str, df_chi[exp_col].dropna().tolist()))
                st.dataframe(df_chi[[obs_col]].describe().T.round(2), use_container_width=True)

        if st.button("Run Goodness of Fit", key="chi_gof_btn"):
            try:
                observed = np.array(parse_data(obs_raw))
                expected_arr = (np.array(parse_data(exp_raw)) if exp_raw.strip()
                                else np.full(len(observed), observed.sum()/len(observed)))
                if len(expected_arr) != len(observed):
                    st.error("Observed and expected must have the same number of categories."); st.stop()
                chi2, p_val = stats.chisquare(observed, f_exp=expected_arr)
                dof = len(observed)-1
                c1,c2,c3 = st.columns(3)
                c1.markdown(f'<div class="result-card"><h4>χ² Statistic</h4><div class="result-value">{chi2:.4f}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="result-card"><h4>Degrees of Freedom</h4><div class="result-value">{dof}</div></div>', unsafe_allow_html=True)
                sig = p_val < alpha_chi
                verdict = ("❌ Reject H₀ — Observed does NOT fit expected distribution." if sig else
                           "✅ Fail to reject H₀ — Observed fits expected distribution.")
                st.markdown(f'<div class="{"verdict-fail" if sig else "verdict-pass"}">{verdict}</div>', unsafe_allow_html=True)
                cats = [f"Cat {i+1}" for i in range(len(observed))]
                fig, ax = dark_fig(8, 3.5)
                x = np.arange(len(cats))
                ax.bar(x-.2, observed, .38, label='Observed', color='#a78bfa', alpha=.85)
                ax.bar(x+.2, expected_arr, .38, label='Expected', color='#f472b6', alpha=.85)
                ax.set_xticks(x); ax.set_xticklabels(cats, color='#e8eaf0', fontsize=9)
                ax.set_title('Observed vs Expected Frequencies')
                ax.legend(facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
                fig_to_st(fig)
            except Exception as e:
                st.error(f"Error: {e}")

    else:
        # ── Test of Independence ─────────────────────────────────────────
        table = None; r_lbls = c_lbls = None

        if chi_src == "Manual input":
            st.caption("Paste counts — one row per line, values comma-separated.\nExample:\n10, 20, 30\n15, 25, 10")
            rows_raw = st.text_area("Contingency table", height=130, key="chi_cont", placeholder="10, 20, 30\n15, 25, 10")
            rl = st.text_input("Row labels (optional)", placeholder="Male, Female", key="chi_rl")
            cl = st.text_input("Column labels (optional)", placeholder="Low, Medium, High", key="chi_cl")
        else:
            file_chi2 = excel_uploader("chi_ind_file",
                "Upload Excel/CSV — rows = categories (e.g. Gender), columns = variables (e.g. Low/Med/High)")
            rows_raw = ""; rl = ""; cl = ""
            if file_chi2:
                sheets_c2, snames_c2 = load_excel(file_chi2)
                sheet_c2 = st.selectbox("Sheet", snames_c2, key="chi_sheet_ind")
                df_c2 = sheets_c2[sheet_c2]
                show_col_pills(df_c2)
                num_only = df_c2.select_dtypes(include='number')
                sel_cols = st.multiselect("Select numeric columns that form the contingency table",
                                          num_only.columns.tolist(), key="chi_ind_cols")
                row_lbl_col = st.selectbox("Row label column (optional)", ["— none —"] + df_c2.columns.tolist(), key="chi_rl_col")
                if sel_cols:
                    sub = num_only[sel_cols].dropna()
                    rows_raw = "\n".join(",".join(map(str, row)) for row in sub.values.tolist())
                    cl = ",".join(sel_cols)
                    rl = ",".join(str(v) for v in df_c2[row_lbl_col].dropna().tolist()) if row_lbl_col != "— none —" else ""
                    st.dataframe(sub, use_container_width=True)

        if st.button("Run Independence Test", key="chi_ind_btn"):
            try:
                lines = [l.strip() for l in rows_raw.strip().split('\n') if l.strip()]
                table = np.array([[float(v) for v in parse_data(l)] for l in lines])
                chi2, p_val, dof, expected = stats.chi2_contingency(table)
                c1,c2,c3 = st.columns(3)
                c1.markdown(f'<div class="result-card"><h4>χ² Statistic</h4><div class="result-value">{chi2:.4f}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="result-card"><h4>Degrees of Freedom</h4><div class="result-value">{dof}</div></div>', unsafe_allow_html=True)
                sig = p_val < alpha_chi
                verdict = ("❌ Reject H₀ — Variables are significantly associated." if sig else
                           "✅ Fail to reject H₀ — Variables appear independent.")
                st.markdown(f'<div class="{"verdict-fail" if sig else "verdict-pass"}">{verdict}</div>', unsafe_allow_html=True)
                r_lbls = [s.strip() for s in rl.split(',')] if rl.strip() else [f"Row {i+1}" for i in range(table.shape[0])]
                c_lbls = [s.strip() for s in cl.split(',')] if cl.strip() else [f"Col {j+1}" for j in range(table.shape[1])]
                r_lbls = r_lbls[:table.shape[0]]
                c_lbls = c_lbls[:table.shape[1]]
                while len(r_lbls)<table.shape[0]: r_lbls.append(f"Row {len(r_lbls)+1}")
                while len(c_lbls)<table.shape[1]: c_lbls.append(f"Col {len(c_lbls)+1}")
                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                cl1, cl2 = st.columns(2)
                with cl1:
                    st.markdown("**Observed**")
                    st.dataframe(pd.DataFrame(table, index=r_lbls, columns=c_lbls), use_container_width=True)
                with cl2:
                    st.markdown("**Expected**")
                    st.dataframe(pd.DataFrame(expected.round(2), index=r_lbls, columns=c_lbls), use_container_width=True)
                fig, axes = plt.subplots(1,2, figsize=(10,3.5))
                fig.patch.set_facecolor('#0f1117')
                for ax, mat, title, cmap in zip(axes, [table, expected], ['Observed','Expected'], ['Purples','RdPu']):
                    ax.set_facecolor('#1e2130')
                    im = ax.imshow(mat, cmap=cmap, aspect='auto')
                    ax.set_xticks(range(len(c_lbls))); ax.set_xticklabels(c_lbls, color='#e8eaf0', fontsize=9)
                    ax.set_yticks(range(len(r_lbls))); ax.set_yticklabels(r_lbls, color='#e8eaf0', fontsize=9)
                    for i in range(mat.shape[0]):
                        for j in range(mat.shape[1]):
                            ax.text(j, i, f'{mat[i,j]:.1f}', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
                    ax.set_title(title, color='#e8eaf0', fontsize=10)
                    fig.colorbar(im, ax=ax).ax.yaxis.set_tick_params(color='#94a3b8')
                plt.tight_layout(); fig_to_st(fig)
            except Exception as e:
                st.error(f"Error parsing table: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown('<p style="color:#475569;font-size:0.8rem;text-align:center;">Built with Streamlit · scipy.stats · numpy · pandas · matplotlib</p>', unsafe_allow_html=True)
PYEOF
echo "Done"
Output

Done
