# =============================================================================
# RETIREMENT BUDGET OPTIMIZATION — Streamlit GUI
# Beautiful interactive table with y values, RM values and Balance
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import time
import io

# -----------------------------------------------------------------------
# Page config — sidebar always expanded by default
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
    'N_1': 'Makanan & Minuman Bukan Beralkohol',
    'N_2': 'Perumahan Elektrik, Gas & Bahan Api',
    'N_3': 'Pengangkutan',
    'N_4': 'Kesihatan',
    'N_5': 'Pendidikan',
    'N_6': 'Pakaian & Kasut',
    'N_7': 'Perabot, & Penyelenggaraan Isi Rumah',
    'N_8': 'Komunikasi',
    'W_1': 'Rekreasi & Budaya',
    'W_2': 'Restoran & Hotel',
    'W_3': 'Alkohol & Perkhidmatan Lain',
    'S_1': 'Simpanan Kewangan',
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

/* Hide only Streamlit footer and main menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Hide toolbar action buttons only - NOT the sidebar toggle */
[data-testid="stToolbarActions"] {visibility: hidden;}
.stDeployButton {display: none !important;}

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
# Embedded y-values data (Purata/Mean, 5th%, 95th% from statistics file)
# Source: y-values-data.xlsx | I=RM100,000 | Staircase | Scenario 1
# -----------------------------------------------------------------------
Y_DATA = {
    'Q1': {
        'N_1': {'mean':0.1566,'p5':0.1562,'p95':0.1569},
        'N_2': {'mean':0.0194,'p5':0.0191,'p95':0.0198},
        'N_3': {'mean':0.0293,'p5':0.0290,'p95':0.0297},
        'N_4': {'mean':0.3040,'p5':0.3037,'p95':0.3043},
        'N_5': {'mean':0.0492,'p5':0.0488,'p95':0.0495},
        'N_6': {'mean':0.0214,'p5':0.0211,'p95':0.0218},
        'N_7': {'mean':0.1011,'p5':0.1008,'p95':0.1014},
        'N_8': {'mean':0.0904,'p5':0.0901,'p95':0.0908},
        'W_1': {'mean':0.0370,'p5':0.0365,'p95':0.0376},
        'W_2': {'mean':0.0380,'p5':0.0374,'p95':0.0385},
        'W_3': {'mean':0.3892,'p5':0.3886,'p95':0.3897},
        'S_1': {'mean':0.2923,'p5':0.2914,'p95':0.2931},
    },
    'Q2': {
        'N_1': {'mean':0.1690,'p5':0.1687,'p95':0.1694},
        'N_2': {'mean':0.0210,'p5':0.0206,'p95':0.0213},
        'N_3': {'mean':0.0316,'p5':0.0312,'p95':0.0320},
        'N_4': {'mean':0.3283,'p5':0.3280,'p95':0.3287},
        'N_5': {'mean':0.0530,'p5':0.0527,'p95':0.0534},
        'N_6': {'mean':0.0231,'p5':0.0228,'p95':0.0235},
        'N_7': {'mean':0.1092,'p5':0.1088,'p95':0.1096},
        'N_8': {'mean':0.0977,'p5':0.0973,'p95':0.0981},
        'W_1': {'mean':0.0401,'p5':0.0395,'p95':0.0407},
        'W_2': {'mean':0.0409,'p5':0.0403,'p95':0.0415},
        'W_3': {'mean':0.4203,'p5':0.4197,'p95':0.4209},
        'S_1': {'mean':0.3156,'p5':0.3147,'p95':0.3165},
    },
    'Q3': {
        'N_1': {'mean':0.1691,'p5':0.1687,'p95':0.1694},
        'N_2': {'mean':0.0210,'p5':0.0207,'p95':0.0214},
        'N_3': {'mean':0.0314,'p5':0.0311,'p95':0.0318},
        'N_4': {'mean':0.3284,'p5':0.3280,'p95':0.3288},
        'N_5': {'mean':0.0531,'p5':0.0528,'p95':0.0535},
        'N_6': {'mean':0.0232,'p5':0.0228,'p95':0.0236},
        'N_7': {'mean':0.1093,'p5':0.1089,'p95':0.1096},
        'N_8': {'mean':0.0978,'p5':0.0974,'p95':0.0981},
        'W_1': {'mean':0.0401,'p5':0.0395,'p95':0.0407},
        'W_2': {'mean':0.0411,'p5':0.0405,'p95':0.0417},
        'W_3': {'mean':0.4203,'p5':0.4198,'p95':0.4209},
        'S_1': {'mean':0.3154,'p5':0.3145,'p95':0.3163},
    },
    'Q4': {
        'N_1': {'mean':0.1837,'p5':0.1833,'p95':0.1840},
        'N_2': {'mean':0.0227,'p5':0.0224,'p95':0.0231},
        'N_3': {'mean':0.0344,'p5':0.0341,'p95':0.0348},
        'N_4': {'mean':0.3569,'p5':0.3565,'p95':0.3573},
        'N_5': {'mean':0.0578,'p5':0.0574,'p95':0.0582},
        'N_6': {'mean':0.0250,'p5':0.0247,'p95':0.0254},
        'N_7': {'mean':0.1186,'p5':0.1183,'p95':0.1190},
        'N_8': {'mean':0.1062,'p5':0.1058,'p95':0.1066},
        'W_1': {'mean':0.0438,'p5':0.0431,'p95':0.0444},
        'W_2': {'mean':0.0444,'p5':0.0438,'p95':0.0451},
        'W_3': {'mean':0.4570,'p5':0.4563,'p95':0.4576},
        'S_1': {'mean':0.3426,'p5':0.3416,'p95':0.3436},
    },
}

# -----------------------------------------------------------------------
# Computation using embedded y-values
# -----------------------------------------------------------------------
def compute_table_from_y(I_income, p_name, alpha_name, mode='mean'):
    quarters = P_TYPES[p_name]
    alpha    = ALPHA_SCENARIOS[alpha_name]
    results  = {}

    for q_name, p in quarters.items():
        q_income = p * I_income
        E_kep    = alpha['Keperluan'] * q_income
        E_keh    = alpha['Kehendak']  * q_income
        E_sim    = alpha['Simpanan']  * q_income
        E_map    = {'Keperluan': E_kep, 'Kehendak': E_keh, 'Simpanan': E_sim}

        results[q_name] = {}
        sum_y = {
            'min': {'Keperluan': 0, 'Kehendak': 0, 'Simpanan': 0},
            'max': {'Keperluan': 0, 'Kehendak': 0, 'Simpanan': 0},
        }

        for col in ALL_COLS:
            grp   = GROUP_MAP[col]
            E_k   = E_map[grp]
            stats = Y_DATA[q_name][col]

            y_min  = stats['p5']
            y_max  = stats['p95']
            rm_min = round(y_min * E_k, 2)
            rm_max = round(y_max * E_k, 2)

            results[q_name][col] = {
                'y_min':  round(y_min, 4),
                'y_max':  round(y_max, 4),
                'rm_min': rm_min,
                'rm_max': rm_max,
                'E_k':    round(E_k, 2),
            }
            sum_y['min'][grp] += y_min   # min spending → max balance
            sum_y['max'][grp] += y_max   # max spending → min balance

        # Min balance = when spending is at MAX (y = p95) → less savings
        b1_min = round(E_kep * (1 - sum_y['max']['Keperluan']), 2)
        b2_min = round(E_keh * (1 - sum_y['max']['Kehendak']),  2)
        b3_min = round(E_sim * (1 - sum_y['max']['Simpanan']),  2)
        bal_min = round(b1_min + b2_min + b3_min, 2)

        # Max balance = when spending is at MIN (y = p5) → more savings
        b1_max = round(E_kep * (1 - sum_y['min']['Keperluan']), 2)
        b2_max = round(E_keh * (1 - sum_y['min']['Kehendak']),  2)
        b3_max = round(E_sim * (1 - sum_y['min']['Simpanan']),  2)
        bal_max = round(b1_max + b2_max + b3_max, 2)

        results[q_name]['BALANCE'] = {
            'rm_min': bal_min,
            'rm_max': bal_max,
        }

    return results

# -----------------------------------------------------------------------
# HTML Table builder
# -----------------------------------------------------------------------
def build_table_html(table_data, quarters):
    q_labels = ['Q1','Q2','Q3','Q4']
    group_colors = {
        'Keperluan': 'row-group-kep',
        'Kehendak':  'row-group-keh',
        'Simpanan':  'row-group-sim'
    }
    group_header_label = {
        'Keperluan': '🏠 &nbsp; Keperluan',
        'Kehendak':  '💎 &nbsp; Kehendak',
        'Simpanan':  '💰 &nbsp; Simpanan',
    }

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

    prev_group = None
    for col in ALL_COLS:
        item_disp = ITEM_DISPLAY[col]
        grp       = GROUP_MAP[col]
        grp_cls   = group_colors[grp]

        # Group separator header row
        if grp != prev_group:
            grp_bg    = {'Keperluan':'rgba(66,133,244,0.20)','Kehendak':'rgba(52,168,83,0.20)','Simpanan':'rgba(234,67,53,0.20)'}[grp]
            grp_color = {'Keperluan':'#90caf9','Kehendak':'#a5d6a7','Simpanan':'#ef9a9a'}[grp]
            grp_label = group_header_label[grp]
            n_cols = 1 + len(q_labels) * 2
            html += f'''<tr>
                <td colspan="{n_cols}" style="
                    background:{grp_bg};
                    color:{grp_color};
                    font-weight:700;
                    font-size:0.82rem;
                    letter-spacing:1.5px;
                    text-transform:uppercase;
                    padding:8px 20px;
                    border-top:1px solid rgba(255,255,255,0.06);
                    border-bottom:1px solid rgba(255,255,255,0.06);
                ">{grp_label}</td>
            </tr>'''
            prev_group = grp

        # Y value row
        html += f'<tr class="row-item-name {grp_cls}">'
        html += f'<td class="cell-item">{item_disp}</td>'
        for q in q_labels:
            d = table_data.get(q, {}).get(col, {})
            html += f'<td class="cell-y-min q-divider">{d.get("y_min",0):.4f}</td>'
            html += f'<td class="cell-y-max">{d.get("y_max",0):.4f}</td>'
        html += '</tr>'

        # RM row
        html += f'<tr class="row-rm {grp_cls}">'
        html += '<td class="cell-label">RM</td>'
        for q in q_labels:
            d = table_data.get(q, {}).get(col, {})
            html += f'<td class="cell-rm-min q-divider">RM {d.get("rm_min",0):,.2f}</td>'
            html += f'<td class="cell-rm-max">RM {d.get("rm_max",0):,.2f}</td>'
        html += '</tr>'

    # Balance section header
    n_cols = 1 + len(q_labels) * 2
    html += f'''<tr>
        <td colspan="{n_cols}" style="
            background:rgba(255,215,0,0.12);
            color:#ffe082;
            font-weight:700;
            font-size:0.82rem;
            letter-spacing:1.5px;
            text-transform:uppercase;
            padding:8px 20px;
            border-top:1px solid rgba(255,255,255,0.06);
            border-bottom:1px solid rgba(255,255,255,0.06);
        ">📊 &nbsp; Quarterly Balance</td>
    </tr>'''

    # Balance Min row (spending at max → lower balance)
    html += '<tr class="row-balance row-group-bal">'
    html += '<td class="cell-item" style="color:#ef9a9a;font-size:0.82rem;">Minimum</td>'
    for q in q_labels:
        d  = table_data.get(q, {}).get('BALANCE', {})
        rm = d.get('rm_min', 0)
        html += f'<td class="cell-bal-min q-divider" colspan="2" style="text-align:center;color:#ef9a9a;">RM {rm:,.2f}</td>'
    html += '</tr>'

    # Balance Max row (spending at min → higher balance)
    html += '<tr class="row-balance row-group-bal">'
    html += '<td class="cell-item" style="color:#a5d6a7;font-size:0.82rem;">Maximum</td>'
    for q in q_labels:
        d  = table_data.get(q, {}).get('BALANCE', {})
        rm = d.get('rm_max', 0)
        html += f'<td class="cell-bal-max q-divider" colspan="2" style="text-align:center;color:#a5d6a7;">RM {rm:,.2f}</td>'
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
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border-radius:8px;padding:8px 12px;
    margin-top:-8px;margin-bottom:8px;font-size:0.78rem;color:rgba(255,255,255,0.5);
    display:flex;justify-content:space-between;'>
        <span>Q1 <b style='color:#90caf9'>{p_vals['Q1']}</b></span>
        <span>Q2 <b style='color:#ef9a9a'>{p_vals['Q2']}</b></span>
        <span>Q3 <b style='color:#a5d6a7'>{p_vals['Q3']}</b></span>
        <span>Q4 <b style='color:#ce93d8'>{p_vals['Q4']}</b></span>
    </div>
    """, unsafe_allow_html=True)

    alpha_name = st.selectbox(
        "🎯 Alpha Scenario",
        options=list(ALPHA_SCENARIOS.keys()),
        help="Select budget allocation ratio"
    )
    a_vals = ALPHA_SCENARIOS[alpha_name]
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border-radius:8px;padding:8px 12px;
    margin-top:-8px;margin-bottom:8px;font-size:0.78rem;color:rgba(255,255,255,0.5);
    display:flex;justify-content:space-between;'>
        <span>🏠 <b style='color:#90caf9'>{a_vals['Keperluan']}</b></span>
        <span>💎 <b style='color:#a5d6a7'>{a_vals['Kehendak']}</b></span>
        <span>💰 <b style='color:#ce93d8'>{a_vals['Simpanan']}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    calc_btn = st.button("⚡ Calculate", use_container_width=True)

# ── Main Content ──────────────────────────────────────────────────────────
if calc_btn:
    # Loading animation
    progress_bar = st.progress(0)
    status_text  = st.empty()

    steps = [
        (20,  "📊 Computing quarterly income allocations (E_k)..."),
        (45,  "🔢 Applying Purata/Mean y-values from statistics..."),
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

    # Compute table using embedded mean y values
    table_data = compute_table_from_y(I_income, p_name, alpha_name)

    # ── Summary Cards ─────────────────────────────────────────────────
    total_bal_min = sum(
        table_data.get(q,{}).get('BALANCE',{}).get('rm_min', 0)
        for q in ['Q1','Q2','Q3','Q4']
    )
    total_bal_max = sum(
        table_data.get(q,{}).get('BALANCE',{}).get('rm_max', 0)
        for q in ['Q1','Q2','Q3','Q4']
    )

    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, f"RM {I_income:,}",          "Annual Income",          "💵"),
        (c2, f"RM {total_bal_min:,.2f}",   "Total Minimum Balance",  "📉"),
        (c3, f"RM {total_bal_max:,.2f}",   "Total Maximum Balance",  "📈"),
    ]
    for col_widget, val, lbl, icon in cards:
        with col_widget:
            st.markdown(f"""
            <div class="stat-card">
                <div style='font-size:1.5rem;margin-bottom:4px'>{icon}</div>
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
            {p_name} &nbsp;|&nbsp; {alpha_name}
        </div>
    </div>
    """, unsafe_allow_html=True)

    table_html = build_table_html(table_data, P_TYPES[p_name])
    st.markdown(table_html, unsafe_allow_html=True)

    plt_close = None  # placeholder

else:
    st.markdown("""
    <div style='text-align:center;padding:3rem;color:rgba(255,255,255,0.5)'>
        <div style='font-size:3rem'>⚡</div>
        <div style='font-size:1rem;margin-top:0.5rem'>Set your parameters and click <b>Calculate</b></div>
    </div>
    """, unsafe_allow_html=True)
