import streamlit as st
import numpy as np
import pandas as pd

import io

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Statistical Tests Calculator",
    page_icon="📊",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0f1117;
        color: #e8eaf0;
    }

    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6ee7f7 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }

    .hero-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    .result-card {
        background: #1e2130;
        border: 1px solid #2e3350;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-top: 1.25rem;
    }

    .result-card h4 {
        color: #a78bfa;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .result-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 600;
        color: #6ee7f7;
    }

    .verdict-pass {
        background: #0d2b1f;
        border: 1px solid #22c55e;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        color: #4ade80;
        font-weight: 600;
        margin-top: 1rem;
    }

    .verdict-fail {
        background: #2b0d0d;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        color: #f87171;
        font-weight: 600;
        margin-top: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        color: #94a3b8;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #a78bfa !important;
        border-bottom: 2px solid #a78bfa !important;
    }

    .stTextArea textarea, .stNumberInput input {
        background: #1e2130 !important;
        border: 1px solid #2e3350 !important;
        color: #e8eaf0 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stSlider > div > div > div {
        background: #a78bfa !important;
    }

    label, .stSelectbox label {
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }

    .section-divider {
        border: none;
        border-top: 1px solid #2e3350;
        margin: 1.5rem 0;
    }

    .badge {
        display: inline-block;
        background: #1e2130;
        border: 1px solid #2e3350;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.78rem;
        color: #94a3b8;
        margin-right: 0.4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper ─────────────────────────────────────────────────────────────────
def parse_data(text):
    """Parse comma/newline/space separated numbers."""
    import re
    tokens = re.split(r'[\s,]+', text.strip())
    return [float(t) for t in tokens if t]


def dark_fig():
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#1e2130')
    for spine in ax.spines.values():
        spine.set_color('#2e3350')
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


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Statistical Tests Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Z-Score · One-Way ANOVA · Chi-Square — enter your data, get instant results</div>', unsafe_allow_html=True)

st.markdown('<span class="badge">scipy.stats</span><span class="badge">numpy</span><span class="badge">matplotlib</span>', unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔢  Z-Score", "📐  ANOVA", "🔲  Chi-Square"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Z-SCORE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Z-Score Calculator")
    st.markdown("Standardize a data point relative to its distribution. "
                "Enter either a single value (with mean/std) or a full dataset.")

    mode = st.radio("Input mode", ["Single value", "Full dataset"], horizontal=True)

    if mode == "Single value":
        col1, col2, col3 = st.columns(3)
        with col1:
            x_val = st.number_input("Observed value (x)", value=0.0, format="%.4f")
        with col2:
            mu = st.number_input("Population mean (μ)", value=0.0, format="%.4f")
        with col3:
            sigma = st.number_input("Standard deviation (σ)", value=1.0, min_value=0.0001, format="%.4f")

        if st.button("Calculate Z-Score", key="z1"):
            z = (x_val - mu) / sigma
            p_two = 2 * (1 - stats.norm.cdf(abs(z)))

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f'<div class="result-card"><h4>Z-Score</h4><div class="result-value">{z:.4f}</div></div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<div class="result-card"><h4>p-value (two-tailed)</h4><div class="result-value">{p_two:.4f}</div></div>', unsafe_allow_html=True)
            with col_c:
                pct = stats.norm.cdf(z) * 100
                st.markdown(f'<div class="result-card"><h4>Percentile</h4><div class="result-value">{pct:.2f}%</div></div>', unsafe_allow_html=True)

            verdict = "✅ Not significant (|z| < 1.96, p ≥ 0.05)" if abs(z) < 1.96 else "❌ Significant (|z| ≥ 1.96, p < 0.05)"
            cls = "verdict-pass" if abs(z) < 1.96 else "verdict-fail"
            st.markdown(f'<div class="{cls}">{verdict}</div>', unsafe_allow_html=True)

            # Plot
            fig, ax = dark_fig()
            x_range = np.linspace(-4, 4, 400)
            ax.plot(x_range, stats.norm.pdf(x_range), color='#a78bfa', linewidth=2)
            ax.fill_between(x_range, stats.norm.pdf(x_range),
                            where=(np.abs(x_range) >= 1.96), color='#ef4444', alpha=0.35, label='Critical (α=0.05)')
            ax.axvline(z, color='#6ee7f7', linewidth=2, linestyle='--', label=f'z = {z:.3f}')
            ax.set_xlabel('z'); ax.set_ylabel('Density'); ax.set_title('Standard Normal Distribution')
            ax.legend(facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
            fig_to_st(fig)

    else:
        data_input = st.text_area("Enter dataset (comma or space separated)",
                                  placeholder="12.5, 14.1, 13.0, 11.8, 15.3, 13.7 …", height=100)
        alpha_z = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="z_alpha")

        if st.button("Calculate Z-Scores", key="z2") and data_input.strip():
            try:
                data = np.array(parse_data(data_input))
                z_scores = stats.zscore(data)
                mu_d, sigma_d = data.mean(), data.std(ddof=0)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f'<div class="result-card"><h4>Mean</h4><div class="result-value">{mu_d:.4f}</div></div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<div class="result-card"><h4>Std Dev</h4><div class="result-value">{sigma_d:.4f}</div></div>', unsafe_allow_html=True)
                with col_c:
                    z_crit = stats.norm.ppf(1 - alpha_z / 2)
                    n_out = np.sum(np.abs(z_scores) > z_crit)
                    st.markdown(f'<div class="result-card"><h4>Outliers (|z|>{z_crit:.2f})</h4><div class="result-value">{n_out}</div></div>', unsafe_allow_html=True)

                df_out = pd.DataFrame({"Value": data, "Z-Score": z_scores.round(4),
                                       "Outlier": np.abs(z_scores) > z_crit})
                st.dataframe(df_out.style.applymap(
                    lambda v: 'color: #f87171' if v is True else '', subset=['Outlier']),
                    use_container_width=True)

                fig, ax = dark_fig()
                colors = ['#ef4444' if abs(z) > z_crit else '#a78bfa' for z in z_scores]
                ax.bar(range(len(z_scores)), z_scores, color=colors, width=0.7)
                ax.axhline(z_crit, color='#f472b6', linestyle='--', linewidth=1, label=f'+{z_crit:.2f}')
                ax.axhline(-z_crit, color='#f472b6', linestyle='--', linewidth=1, label=f'-{z_crit:.2f}')
                ax.set_xlabel('Index'); ax.set_ylabel('Z-Score'); ax.set_title('Z-Scores per Data Point')
                patch = mpatches.Patch(color='#ef4444', label='Outlier')
                ax.legend(handles=[patch], facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
                fig_to_st(fig)
            except Exception as e:
                st.error(f"Error parsing data: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANOVA
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### One-Way ANOVA")
    st.markdown("Test whether the means of **3 or more groups** differ significantly.")

    n_groups = st.number_input("Number of groups", min_value=2, max_value=10, value=3, step=1)
    alpha_anova = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="anova_alpha")

    groups = []
    group_names = []
    cols = st.columns(min(n_groups, 4))

    for i in range(n_groups):
        col_idx = i % min(n_groups, 4)
        with cols[col_idx]:
            name = st.text_input(f"Group {i+1} label", value=f"Group {i+1}", key=f"gname_{i}")
            raw = st.text_area(f"Data for {name}", placeholder="e.g. 5, 7, 6.5, 8", key=f"gdata_{i}", height=90)
            group_names.append(name)
            groups.append(raw)

    if st.button("Run ANOVA", key="anova_btn"):
        try:
            parsed = [np.array(parse_data(g)) for g in groups if g.strip()]
            if len(parsed) < 2:
                st.warning("Please fill in at least 2 groups.")
            else:
                f_stat, p_val = stats.f_oneway(*parsed)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f'<div class="result-card"><h4>F-Statistic</h4><div class="result-value">{f_stat:.4f}</div></div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
                with col_c:
                    df_between = len(parsed) - 1
                    df_within = sum(len(g) for g in parsed) - len(parsed)
                    st.markdown(f'<div class="result-card"><h4>df (between / within)</h4><div class="result-value">{df_between} / {df_within}</div></div>', unsafe_allow_html=True)

                verdict = ("✅ Fail to reject H₀ — No significant difference between group means."
                           if p_val >= alpha_anova else
                           "❌ Reject H₀ — Significant difference exists between group means.")
                cls = "verdict-pass" if p_val >= alpha_anova else "verdict-fail"
                st.markdown(f'<div class="{cls}">{verdict}</div>', unsafe_allow_html=True)

                # Summary table
                summary = pd.DataFrame({
                    "Group": group_names[:len(parsed)],
                    "N": [len(g) for g in parsed],
                    "Mean": [g.mean().round(4) for g in parsed],
                    "Std Dev": [g.std(ddof=1).round(4) for g in parsed],
                    "Min": [g.min() for g in parsed],
                    "Max": [g.max() for g in parsed],
                })
                st.dataframe(summary, use_container_width=True)

                # Box plot
                fig, ax = dark_fig()
                fig.set_size_inches(8, 4)
                bp = ax.boxplot(parsed, patch_artist=True, notch=False,
                                medianprops=dict(color='#6ee7f7', linewidth=2))
                palette = ['#a78bfa', '#f472b6', '#6ee7f7', '#34d399', '#fb923c',
                           '#facc15', '#38bdf8', '#e879f9', '#4ade80', '#f87171']
                for patch, color in zip(bp['boxes'], palette):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.6)
                for whisker in bp['whiskers']:
                    whisker.set_color('#94a3b8')
                for cap in bp['caps']:
                    cap.set_color('#94a3b8')
                for flier in bp['fliers']:
                    flier.set(marker='o', color='#ef4444', alpha=0.6)
                ax.set_xticks(range(1, len(parsed) + 1))
                ax.set_xticklabels(group_names[:len(parsed)], color='#e8eaf0', fontsize=9)
                ax.set_title('Group Distributions (Box Plot)')
                ax.set_ylabel('Value')
                fig_to_st(fig)

        except Exception as e:
            st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHI-SQUARE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Chi-Square Test")
    st.markdown("Choose between **Goodness of Fit** (one variable vs expected) "
                "or **Test of Independence** (contingency table).")

    chi_mode = st.radio("Test type", ["Goodness of Fit", "Test of Independence"], horizontal=True)
    alpha_chi = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="chi_alpha")

    if chi_mode == "Goodness of Fit":
        st.markdown("**Observed frequencies** — one value per category.")
        obs_input = st.text_area("Observed counts", placeholder="30, 20, 25, 25", height=80)
        exp_input = st.text_area("Expected counts (leave blank for equal distribution)",
                                 placeholder="25, 25, 25, 25", height=80)

        if st.button("Run Chi-Square Goodness of Fit", key="chi1"):
            try:
                observed = np.array(parse_data(obs_input))
                if exp_input.strip():
                    expected = np.array(parse_data(exp_input))
                    if len(expected) != len(observed):
                        st.error("Observed and expected must have the same length.")
                        st.stop()
                else:
                    expected = np.full(len(observed), observed.sum() / len(observed))

                chi2, p_val = stats.chisquare(observed, f_exp=expected)
                dof = len(observed) - 1

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f'<div class="result-card"><h4>χ² Statistic</h4><div class="result-value">{chi2:.4f}</div></div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
                with col_c:
                    st.markdown(f'<div class="result-card"><h4>Degrees of Freedom</h4><div class="result-value">{dof}</div></div>', unsafe_allow_html=True)

                verdict = ("✅ Fail to reject H₀ — Observed fits expected distribution."
                           if p_val >= alpha_chi else
                           "❌ Reject H₀ — Observed does NOT fit expected distribution.")
                cls = "verdict-pass" if p_val >= alpha_chi else "verdict-fail"
                st.markdown(f'<div class="{cls}">{verdict}</div>', unsafe_allow_html=True)

                # Bar chart
                cats = [f"Cat {i+1}" for i in range(len(observed))]
                fig, ax = dark_fig()
                x = np.arange(len(cats))
                ax.bar(x - 0.2, observed, 0.38, label='Observed', color='#a78bfa', alpha=0.85)
                ax.bar(x + 0.2, expected, 0.38, label='Expected', color='#f472b6', alpha=0.85)
                ax.set_xticks(x); ax.set_xticklabels(cats, color='#e8eaf0', fontsize=9)
                ax.set_title('Observed vs Expected Frequencies')
                ax.legend(facecolor='#1e2130', edgecolor='#2e3350', labelcolor='#e8eaf0', fontsize=8)
                fig_to_st(fig)

            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.markdown("**Contingency table** — paste or type counts, one row per line, columns separated by commas.")
        st.caption("Example (2×3 table):\n```\n10, 20, 30\n15, 25, 10\n```")

        rows_input = st.text_area("Contingency table", height=140,
                                  placeholder="10, 20, 30\n15, 25, 10")
        row_labels = st.text_input("Row labels (comma separated, optional)", placeholder="Male, Female")
        col_labels = st.text_input("Column labels (comma separated, optional)", placeholder="Low, Medium, High")

        if st.button("Run Chi-Square Independence Test", key="chi2_btn"):
            try:
                lines = [l.strip() for l in rows_input.strip().split('\n') if l.strip()]
                table = np.array([[float(v) for v in parse_data(l)] for l in lines])

                chi2, p_val, dof, expected = stats.chi2_contingency(table)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f'<div class="result-card"><h4>χ² Statistic</h4><div class="result-value">{chi2:.4f}</div></div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<div class="result-card"><h4>p-value</h4><div class="result-value">{p_val:.4f}</div></div>', unsafe_allow_html=True)
                with col_c:
                    st.markdown(f'<div class="result-card"><h4>Degrees of Freedom</h4><div class="result-value">{dof}</div></div>', unsafe_allow_html=True)

                verdict = ("✅ Fail to reject H₀ — Variables appear independent."
                           if p_val >= alpha_chi else
                           "❌ Reject H₀ — Variables are significantly associated.")
                cls = "verdict-pass" if p_val >= alpha_chi else "verdict-fail"
                st.markdown(f'<div class="{cls}">{verdict}</div>', unsafe_allow_html=True)

                r_lbls = [l.strip() for l in row_labels.split(',')] if row_labels.strip() else [f"Row {i+1}" for i in range(table.shape[0])]
                c_lbls = [l.strip() for l in col_labels.split(',')] if col_labels.strip() else [f"Col {j+1}" for j in range(table.shape[1])]

                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown("**Observed**")
                    st.dataframe(pd.DataFrame(table, index=r_lbls, columns=c_lbls), use_container_width=True)
                with col_right:
                    st.markdown("**Expected**")
                    st.dataframe(pd.DataFrame(expected.round(2), index=r_lbls, columns=c_lbls), use_container_width=True)

                # Heatmap
                fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
                fig.patch.set_facecolor('#0f1117')
                for ax, mat, title, cmap in zip(axes, [table, expected],
                                                 ['Observed', 'Expected'],
                                                 ['Purples', 'RdPu']):
                    ax.set_facecolor('#1e2130')
                    im = ax.imshow(mat, cmap=cmap, aspect='auto')
                    ax.set_xticks(range(len(c_lbls))); ax.set_xticklabels(c_lbls, color='#e8eaf0', fontsize=9)
                    ax.set_yticks(range(len(r_lbls))); ax.set_yticklabels(r_lbls, color='#e8eaf0', fontsize=9)
                    for i in range(mat.shape[0]):
                        for j in range(mat.shape[1]):
                            ax.text(j, i, f'{mat[i, j]:.1f}', ha='center', va='center',
                                    color='white', fontsize=9, fontweight='bold')
                    ax.set_title(title, color='#e8eaf0', fontsize=10)
                    fig.colorbar(im, ax=ax).ax.yaxis.set_tick_params(color='#94a3b8')
                plt.tight_layout()
                fig_to_st(fig)

            except Exception as e:
                st.error(f"Error parsing table: {e}")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown('<p style="color:#475569;font-size:0.8rem;text-align:center;">Built with Streamlit · scipy.stats · numpy · matplotlib</p>', unsafe_allow_html=True)
