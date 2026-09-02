# =============================================================================
# RETIREMENT BUDGET OPTIMIZATION — Streamlit GUI
# Beautiful interactive table with y values, RM values and Balance
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import time

# -----------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Retirement Budget Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------
KEPERLUAN = ['N_1','N_2','N_3','N_4','N_5','N_6','N_7','N_8']
KEHENDAK  = ['W_1','W_2','W_3']
SIMPANAN  = ['S_1']
ALL_COLS  = KEPERLUAN + KEHENDAK + SIMPANAN

ITEM_DISPLAY = {
    'N_1':'N1','N_2':'N2','N_3':'N3','N_4':'N4',
    'N_5':'N5','N_6':'N6','N_7':'N7','N_8':'N8',
    'W_1':'H1','W_2':'H2','W_3':'H3','S_1':'S1'
}

GROUP_MAP = {}
for c in KEPERLUAN: GROUP_MAP[c] = 'Keperluan'
for c in KEHENDAK:  GROUP_MAP[c] = 'Kehendak'
for c in SIMPANAN:  GROUP_MAP[c] = 'Simpanan'

P_TYPES = {
    'Staircase':  {'Q1':0.27,'Q2':0.25,'Q3':0.25,'Q4':0.23},
    'Horizontal': {'Q1':0.25,'Q2':0.25,'Q3':0.25,'Q4':0.25},
    'ZigZag':     {'Q1':0.20,'Q2':0.30,'Q3':0.20,'Q4':0.30},
}

ALPHA_SCENARIOS = {
    'Scenario 1 (0.5/0.3/0.2)': {'Keperluan':0.5,'Kehendak':0.3,'Simpanan':0.2},
    'Scenario 2 (0.55/0.25/0.2)':{'Keperluan':0.55,'Kehendak':0.25,'Simpanan':0.2},
    'Scenario 3 (0.6/0.2/0.2)':  {'Keperluan':0.6,'Kehendak':0.2,'Simpanan':0.2},
}

# -----------------------------------------------------------------------
# Custom CSS
# -----------------------------------------------------------------------
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Make sure sidebar toggle button is always visible */
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    color: white !important;
    background: rgba(102,126,234,0.4) !important;
    border-radius: 8px !important;
}

/* Main background */
.main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
.block-container { padding: 1.5rem 2rem; }

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    text-align: center;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-sub {
    color: rgba(255,255,255,0.6);
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

/* Sidebar styling */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] .stMarkdown { color: white; }

/* Input labels */
label { color: rgba(255,255,255,0.85) !important; font-weight: 500 !important; }

/* Button */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    background: linear-gradient(135deg, #764ba2, #667eea) !important;
}

/* Table container */
.table-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    margin-top: 1.5rem;
}

/* Table styles */
.results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    font-family: 'Inter', sans-serif;
}
.results-table thead th {
    padding: 14px 10px;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}
.th-quarter {
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.9);
    text-align: center;
}
.th-min {
    background: rgba(66, 133, 244, 0.25);
    color: #90caf9;
    text-align: center;
}
.th-max {
    background: rgba(234, 115, 51, 0.25);
    color: #ffab76;
    text-align: center;
}
.th-item {
    background: rgba(255,255,255,0.04);
    color: rgba(255,255,255,0.7);
    text-align: left;
    padding-left: 20px !important;
    min-width: 70px;
}

/* Table body rows */
.results-table tbody tr {
    transition: all 0.2s ease;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.results-table tbody tr:hover {
    background: rgba(102,126,234,0.15) !important;
    transform: scale(1.005);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    cursor: pointer;
}

/* Row types */
.row-item-name td { background: rgba(255,255,255,0.04); }
.row-y td { background: rgba(255,255,255,0.02); }
.row-rm td { background: rgba(0,0,0,0.15); }
.row-balance td { background: rgba(255,215,0,0.08); }
.row-group-kep td { border-left: 3px solid #4285f4; }
.row-group-keh td { border-left: 3px solid #34a853; }
.row-group-sim td { border-left: 3px solid #ea4335; }
.row-group-bal td { border-left: 3px solid #fbbc04; }

/* Cell styles */
.cell-item {
    padding: 10px 10px 10px 20px;
    font-weight: 700;
    font-size: 0.9rem;
    color: white;
}
.cell-label {
    padding: 5px 10px 5px 20px;
    color: rgba(255,255,255,0.45);
    font-size: 0.72rem;
    font-style: italic;
}
.cell-y-min {
    padding: 5px 10px;
    text-align: center;
    color: #90caf9;
    font-weight: 500;
    font-size: 0.8rem;
}
.cell-y-max {
    padding: 5px 10px;
    text-align: center;
    color: #ffab76;
    font-weight: 500;
    font-size: 0.8rem;
}
.cell-rm-min {
    padding: 5px 10px;
    text-align: center;
    color: #80deea;
    font-size: 0.78rem;
    font-family: 'Courier New', monospace;
}
.cell-rm-max {
    padding: 5px 10px;
    text-align: center;
    color: #ffcc80;
    font-size: 0.78rem;
    font-family: 'Courier New', monospace;
}
.cell-bal-min {
    padding: 10px;
    text-align: center;
    color: #a5d6a7;
    font-weight: 600;
    font-family: 'Courier New', monospace;
}
.cell-bal-max {
    padding: 10px;
    text-align: center;
    color: #ffe082;
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

/* Quarter dividers */
.q-divider { border-left: 1px solid rgba(255,255,255,0.08) !important; }

/* Stats cards */
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.stat-card:hover {
    background: rgba(102,126,234,0.2);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
.stat-value { font-size: 1.4rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 4px; }

/* Loading */
.loading-box {
    text-align: center;
    padding: 3rem;
    color: rgba(255,255,255,0.7);
}

/* Legend */
.legend { display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; color: rgba(255,255,255,0.6); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }

/* Selectbox & number input dark theme */
.stSelectbox > div > div, .stNumberInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Parse y-values-data.xlsx
# -----------------------------------------------------------------------
@st.cache_data
def parse_y_values_file(file_bytes):
    import io
    df = pd.read_excel(io.BytesIO(file_bytes), header=None)

    # Items order: N1-N8, H1-H3, S1 per quarter
    ITEMS_ORDER = ['N_1','N_2','N_3','N_4','N_5','N_6','N_7','N_8',
                   'W_1','W_2','W_3','S_1']
    Q_LABELS    = ['Q1','Q2','Q3','Q4']
    N_ITEMS     = len(ITEMS_ORDER)

    # Row indices (0-based)
    ROW_MEAN = 4   # Purata/Mean
    ROW_P5   = 7   # Minimum 5%
    ROW_P95  = 8   # Maksimum 95%

    y_stats = {}
    for qi, q_name in enumerate(Q_LABELS):
        y_stats[q_name] = {}
        col_start = 1 + qi * N_ITEMS
        for ii, col in enumerate(ITEMS_ORDER):
            c = col_start + ii
            y_stats[q_name][col] = {
                'mean': float(df.iloc[ROW_MEAN, c]),
                'p5':   float(df.iloc[ROW_P5,   c]),
                'p95':  float(df.iloc[ROW_P95,  c]),
            }

    return y_stats

# -----------------------------------------------------------------------
# Computation using y-values file
# -----------------------------------------------------------------------
def compute_table_from_y(y_stats, I_income, p_name, alpha_name, mode='mean'):
    """
    mode: 'mean' = use Purata/Mean for both Min and Max (testing)
          'percentile' = use p5 for Min, p95 for Max
    """
    quarters = P_TYPES[p_name]
    alpha    = ALPHA_SCENARIOS[alpha_name]

    results = {}
    for q_name, p in quarters.items():
        q_income = p * I_income
        E_kep    = alpha['Keperluan'] * q_income
        E_keh    = alpha['Kehendak']  * q_income
        E_sim    = alpha['Simpanan']  * q_income
        E_map    = {'Keperluan': E_kep, 'Kehendak': E_keh, 'Simpanan': E_sim}

        results[q_name] = {}
        sum_y_kep = 0; sum_y_keh = 0; sum_y_sim = 0

        for col in ALL_COLS:
            grp = GROUP_MAP[col]
            E_k = E_map[grp]
            stats = y_stats[q_name][col]

            if mode == 'mean':
                y_min = stats['mean']
                y_max = stats['mean']
            else:
                y_min = stats['p5']
                y_max = stats['p95']

            rm_min = round(y_min * E_k, 2)
            rm_max = round(y_max * E_k, 2)

            results[q_name][col] = {
                'y_min':  round(y_min, 4),
                'y_max':  round(y_max, 4),
                'rm_min': rm_min,
                'rm_max': rm_max,
                'E_k':    round(E_k, 2),
            }

            # Accumulate for balance calculation
            y_mean = stats['mean']
            if grp == 'Keperluan': sum_y_kep += y_mean
            elif grp == 'Kehendak': sum_y_keh += y_mean
            else: sum_y_sim += y_mean

        # Balance = Σ(E_k - e_k) where e_k ≈ Σy_mean × E_k
        b1 = round(E_kep * (1 - sum_y_kep), 2)
        b2 = round(E_keh * (1 - sum_y_keh), 2)
        b3 = round(E_sim * (1 - sum_y_sim), 2)
        bal = round(b1 + b2 + b3, 2)

        results[q_name]['BALANCE'] = {
            'b1': b1, 'b2': b2, 'b3': b3,
            'rm_min': bal,
            'rm_max': bal,
        }

    return results

# -----------------------------------------------------------------------
# HTML Table builder
# -----------------------------------------------------------------------
def build_table_html(table_data, quarters):
    q_labels = ['Q1','Q2','Q3','Q4']
    group_colors = {'Keperluan':'row-group-kep','Kehendak':'row-group-keh',
                    'Simpanan':'row-group-sim'}

    html = '''
    <div class="table-container">
    <table class="results-table">
    <thead>
        <tr>
            <th class="th-item" rowspan="2">Item</th>
    '''
    for q in q_labels:
        html += f'<th class="th-quarter q-divider" colspan="2">{q}</th>'
    html += '</tr><tr>'
    for _ in q_labels:
        html += '<th class="th-min q-divider">Min</th><th class="th-max">Max</th>'
    html += '</tr></thead><tbody>'

    for col in ALL_COLS:
        item_disp = ITEM_DISPLAY[col]
        grp       = GROUP_MAP[col]
        grp_cls   = group_colors[grp]

        # Item name row
        html += f'<tr class="row-item-name {grp_cls}">'
        html += f'<td class="cell-item">{item_disp}</td>'
        for q in q_labels:
            d = table_data.get(q, {}).get(col, {})
            html += f'<td class="cell-y-min q-divider">{d.get("y_min","—"):.4f}</td>'
            html += f'<td class="cell-y-max">{d.get("y_max","—"):.4f}</td>'
        html += '</tr>'

        # RM row
        html += f'<tr class="row-rm {grp_cls}">'
        html += '<td class="cell-label">RM</td>'
        for q in q_labels:
            d = table_data.get(q, {}).get(col, {})
            rm_min = d.get('rm_min', 0)
            rm_max = d.get('rm_max', 0)
            html += f'<td class="cell-rm-min q-divider">RM {rm_min:,.2f}</td>'
            html += f'<td class="cell-rm-max">RM {rm_max:,.2f}</td>'
        html += '</tr>'

    # Balance row
    html += '<tr class="row-balance row-group-bal">'
    html += '<td class="cell-item" style="color:#ffe082;">BALANCE</td>'
    for q in q_labels:
        d = table_data.get(q, {}).get('BALANCE', {})
        rm_min = d.get('rm_min', 0)
        rm_max = d.get('rm_max', 0)
        html += f'<td class="cell-bal-min q-divider">RM {rm_min:,.2f}</td>'
        html += f'<td class="cell-bal-max">RM {rm_max:,.2f}</td>'
    html += '</tr>'

    html += '</tbody></table></div>'
    return html

# -----------------------------------------------------------------------
# Main App
# -----------------------------------------------------------------------

# Hero Header
st.markdown("""
<div class="hero-header">
    <p class="hero-title">💰 Retirement Budget Optimizer</p>
    <p class="hero-sub">Optimize your retirement savings with advanced budget allocation modeling</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Parameters")
    st.markdown("---")

    uploaded = st.file_uploader(
        "📂 Upload y-Values Statistics File",
        type=['xlsx'],
        help="Upload the y Distribution Statistics Excel file (y-values-data.xlsx)"
    )

    st.markdown("---")

    I_income = st.number_input(
        "💵 Annual Income (RM)",
        min_value=1000,
        max_value=9_999_999,
        value=100000,
        step=1000,
        help="Enter your annual income in RM"
    )

    p_name = st.selectbox(
        "📊 P Pattern",
        options=list(P_TYPES.keys()),
        help="Select quarterly income distribution pattern"
    )
    p_vals = P_TYPES[p_name]
    st.caption(f"Q1={p_vals['Q1']} | Q2={p_vals['Q2']} | Q3={p_vals['Q3']} | Q4={p_vals['Q4']}")

    alpha_name = st.selectbox(
        "🎯 Alpha Scenario",
        options=list(ALPHA_SCENARIOS.keys()),
        help="Select budget allocation ratio"
    )
    a_vals = ALPHA_SCENARIOS[alpha_name]
    st.caption(f"Kep={a_vals['Keperluan']} | Keh={a_vals['Kehendak']} | Sim={a_vals['Simpanan']}")

    st.markdown("---")

    st.markdown("""
    <div style='background:rgba(102,126,234,0.15);border:1px solid rgba(102,126,234,0.3);
    border-radius:8px;padding:10px;font-size:0.75rem;color:rgba(255,255,255,0.6)'>
    <b style='color:rgba(255,255,255,0.8)'>📌 Testing Mode</b><br>
    Currently using <b>Purata/Mean</b> y-values to generate the table.<br><br>
    Y = mean y value from statistics file<br>
    RM = Y × E_k (income-scaled)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    calc_btn = st.button("⚡ Calculate", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:rgba(255,255,255,0.4);font-size:0.75rem;'>
    <b>Legend</b><br>
    🔵 Min = Based on Mean y value<br>
    🟠 Max = Based on Mean y value<br>
    Y = Weightage value (dimensionless)<br>
    RM = Monetary value (income-scaled)
    </div>
    """, unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────────────────
if not uploaded:
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;color:rgba(255,255,255,0.4)'>
        <div style='font-size:4rem;margin-bottom:1rem'>📊</div>
        <div style='font-size:1.2rem;font-weight:600;color:rgba(255,255,255,0.6)'>Upload y-Values Statistics File to get started</div>
        <div style='font-size:0.9rem;margin-top:0.5rem'>Upload the <b>y-values-data.xlsx</b> file generated from the main model</div>
        <div style='margin-top:1.5rem;padding:1rem;background:rgba(102,126,234,0.1);border-radius:10px;
        border:1px solid rgba(102,126,234,0.3);font-size:0.82rem;color:rgba(255,255,255,0.5);max-width:500px;margin-left:auto;margin-right:auto;'>
        📌 The file should contain KDE statistics including Purata/Mean, Minimum 5%, Maksimum 95% for all 12 expense items across 4 quarters.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if calc_btn:
    # Parse y-values file
    file_bytes = uploaded.read()
    with st.spinner("📂 Reading y-values statistics file..."):
        try:
            y_stats = parse_y_values_file(file_bytes)
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()

    # Loading animation
    progress_bar = st.progress(0)
    status_text  = st.empty()

    steps = [
        (20,  "📊 Computing quarterly income allocations (E_k)..."),
        (45,  "🔢 Applying Purata/Mean y-values from statistics file..."),
        (70,  "💹 Computing RM values: y_mean × E_k..."),
        (90,  "⚖️  Calculating quarterly balance estimates..."),
        (100, "✅ Table ready!"),
    ]

    for pct, msg in steps:
        status_text.markdown(
            f"<div style='color:rgba(255,255,255,0.7);text-align:center;'>{msg}</div>",
            unsafe_allow_html=True)
        progress_bar.progress(pct)
        time.sleep(0.35)

    progress_bar.empty()
    status_text.empty()

    # Compute table using mean y values
    table_data = compute_table_from_y(y_stats, I_income, p_name, alpha_name, mode='mean')

    # ── Summary Cards ─────────────────────────────────────────────────
    q1_income  = P_TYPES[p_name]['Q1'] * I_income
    q4_income  = P_TYPES[p_name]['Q4'] * I_income
    q1_balance = table_data.get('Q1',{}).get('BALANCE',{}).get('rm_min', 0)
    q4_balance = table_data.get('Q4',{}).get('BALANCE',{}).get('rm_min', 0)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, f"RM {I_income:,}",      "Annual Income"),
        (c2, f"RM {q1_income:,.0f}",  "Q1 Quarterly Income"),
        (c3, f"RM {q1_balance:,.2f}", "Q1 Est. Balance"),
        (c4, f"RM {q4_balance:,.2f}", "Q4 Est. Balance"),
    ]
    for col_widget, val, lbl in cards:
        with col_widget:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{val}</div>
                <div class="stat-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Table ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;'>
        <div style='color:white;font-size:1.1rem;font-weight:600;'>
            📋 Budget Allocation Table
        </div>
        <div style='color:rgba(255,255,255,0.4);font-size:0.8rem;'>
            {p_name} | {alpha_name} | Testing: Purata/Mean y-values
        </div>
    </div>
    """, unsafe_allow_html=True)

    table_html = build_table_html(table_data, P_TYPES[p_name])
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Footer info ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:rgba(255,255,255,0.3);font-size:0.75rem;text-align:center;'>
        📌 <b>Testing Mode</b> — Y values based on Purata/Mean from statistics file &nbsp;|&nbsp;
        RM = Y × E_k &nbsp;|&nbsp; E_k = d_k × p_j × Income &nbsp;|&nbsp;
        Balance = E_k − Σ(y_mean × E_k)
    </div>
    """, unsafe_allow_html=True)

elif not calc_btn:
    if uploaded:
        st.markdown("""
        <div style='text-align:center;padding:3rem;color:rgba(255,255,255,0.5)'>
            <div style='font-size:3rem'>⚡</div>
            <div style='font-size:1rem;margin-top:0.5rem'>Click <b>Calculate</b> to generate the table</div>
        </div>
        """, unsafe_allow_html=True)
