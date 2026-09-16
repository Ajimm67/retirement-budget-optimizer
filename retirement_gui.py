# =============================================================================
# RETIREMENT BUDGET OPTIMIZATION — Streamlit GUI
# Clean centered layout, no sidebar
# =============================================================================
import streamlit as st
import numpy as np
import time

st.set_page_config(
    page_title="Retirement Budget Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------
KEPERLUAN = ['N_1','N_2','N_3','N_4','N_5','N_6','N_7','N_8']
KEHENDAK  = ['W_1','W_2','W_3']
SIMPANAN  = ['S_1']
ALL_COLS  = KEPERLUAN + KEHENDAK + SIMPANAN

GROUP_MAP = {}
for c in KEPERLUAN: GROUP_MAP[c] = 'Keperluan'
for c in KEHENDAK:  GROUP_MAP[c] = 'Kehendak'
for c in SIMPANAN:  GROUP_MAP[c] = 'Simpanan'

ITEM_DISPLAY = {
    'N_1':'Keperluan 1','N_2':'Keperluan 2','N_3':'Keperluan 3','N_4':'Keperluan 4',
    'N_5':'Keperluan 5','N_6':'Keperluan 6','N_7':'Keperluan 7','N_8':'Keperluan 8',
    'W_1':'Kehendak 1','W_2':'Kehendak 2','W_3':'Kehendak 3','S_1':'Simpanan 1',
}

P_TYPES = {'Staircase': {'Q1':0.27,'Q2':0.25,'Q3':0.25,'Q4':0.23}}
ALPHA_SCENARIOS = {'Scenario 2 (0.55/0.25/0.2)': {'Keperluan':0.55,'Kehendak':0.25,'Simpanan':0.2}}
P_NAME     = 'Staircase'
ALPHA_NAME = 'Scenario 2 (0.55/0.25/0.2)'

# -----------------------------------------------------------------------
# Embedded y-values data
# Source: y-values-data_updated_.xlsx | Staircase | Scenario 2
# -----------------------------------------------------------------------
Y_DATA = {
    'Q1': {
        'N_1': {'mean':0.1593,'p5':0.1483,'p95':0.1698},
        'N_2': {'mean':0.0302,'p5':0.0282,'p95':0.0324},
        'N_3': {'mean':0.0338,'p5':0.0315,'p95':0.036},
        'N_4': {'mean':0.3305,'p5':0.309,'p95':0.353},
        'N_5': {'mean':0.0756,'p5':0.0705,'p95':0.081},
        'N_6': {'mean':0.032,'p5':0.0299,'p95':0.0342},
        'N_7': {'mean':0.1487,'p5':0.1382,'p95':0.1589},
        'N_8': {'mean':0.0951,'p5':0.0886,'p95':0.1018},
        'W_1': {'mean':0.1067,'p5':0.099,'p95':0.1139},
        'W_2': {'mean':0.0958,'p5':0.089,'p95':0.1026},
        'W_3': {'mean':0.5904,'p5':0.5532,'p95':0.6296},
        'S_1': {'mean':0.401,'p5':0.3746,'p95':0.428},
    },
    'Q2': {
        'N_1': {'mean':0.1745,'p5':0.1627,'p95':0.1864},
        'N_2': {'mean':0.0328,'p5':0.0305,'p95':0.0351},
        'N_3': {'mean':0.0368,'p5':0.0342,'p95':0.0391},
        'N_4': {'mean':0.3569,'p5':0.3328,'p95':0.3794},
        'N_5': {'mean':0.0813,'p5':0.0756,'p95':0.0869},
        'N_6': {'mean':0.0346,'p5':0.0323,'p95':0.0371},
        'N_7': {'mean':0.1601,'p5':0.149,'p95':0.1712},
        'N_8': {'mean':0.1024,'p5':0.0956,'p95':0.1094},
        'W_1': {'mean':0.1141,'p5':0.1067,'p95':0.1219},
        'W_2': {'mean':0.1032,'p5':0.0965,'p95':0.1101},
        'W_3': {'mean':0.6384,'p5':0.5943,'p95':0.6829},
        'S_1': {'mean':0.4327,'p5':0.4018,'p95':0.4629},
    },
    'Q3': {
        'N_1': {'mean':0.1714,'p5':0.1599,'p95':0.1835},
        'N_2': {'mean':0.0323,'p5':0.0301,'p95':0.0345},
        'N_3': {'mean':0.0366,'p5':0.0342,'p95':0.0392},
        'N_4': {'mean':0.3565,'p5':0.3337,'p95':0.3807},
        'N_5': {'mean':0.0816,'p5':0.0759,'p95':0.0871},
        'N_6': {'mean':0.0342,'p5':0.032,'p95':0.0365},
        'N_7': {'mean':0.1601,'p5':0.1492,'p95':0.171},
        'N_8': {'mean':0.1026,'p5':0.0954,'p95':0.1098},
        'W_1': {'mean':0.1147,'p5':0.1068,'p95':0.1222},
        'W_2': {'mean':0.1035,'p5':0.0967,'p95':0.1104},
        'W_3': {'mean':0.6387,'p5':0.5931,'p95':0.6807},
        'S_1': {'mean':0.4318,'p5':0.4026,'p95':0.4604},
    },
    'Q4': {
        'N_1': {'mean':0.187,'p5':0.174,'p95':0.1995},
        'N_2': {'mean':0.0352,'p5':0.0327,'p95':0.0376},
        'N_3': {'mean':0.0396,'p5':0.037,'p95':0.0423},
        'N_4': {'mean':0.3891,'p5':0.3633,'p95':0.415},
        'N_5': {'mean':0.0884,'p5':0.0824,'p95':0.0944},
        'N_6': {'mean':0.0377,'p5':0.0351,'p95':0.0402},
        'N_7': {'mean':0.1746,'p5':0.1626,'p95':0.1869},
        'N_8': {'mean':0.1117,'p5':0.1039,'p95':0.1196},
        'W_1': {'mean':0.1249,'p5':0.1163,'p95':0.1335},
        'W_2': {'mean':0.1122,'p5':0.1043,'p95':0.1202},
        'W_3': {'mean':0.6933,'p5':0.6463,'p95':0.7427},
        'S_1': {'mean':0.4699,'p5':0.4391,'p95':0.5018},
    },
}

# -----------------------------------------------------------------------
# CSS
# -----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
[data-testid="stToolbarActions"] {visibility: hidden;}
.stDeployButton {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}

.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

/* Animated gradient background */
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.main {
    background: linear-gradient(-45deg, #0f0c29, #1a0533, #0d1b4b, #0f3460, #1a1a2e);
    background-size: 400% 400%;
    animation: gradientShift 12s ease infinite;
    min-height: 100vh;
}

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6b6b, #00d2ff);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeInDown 0.8s ease, gradientShift 4s linear infinite;
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    color: rgba(255,255,255,0.5);
    font-size: 1rem;
    margin-top: 0.6rem;
    animation: fadeInDown 0.8s ease 0.2s both;
}

/* Income input card */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
.input-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    max-width: 480px;
    margin: 0 auto 2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    animation: fadeInUp 0.8s ease 0.3s both;
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.input-card:hover {
    box-shadow: 0 25px 80px rgba(102,126,234,0.3);
    border-color: rgba(102,126,234,0.4);
}
.input-label {
    color: rgba(255,255,255,0.7);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    text-align: center;
}

/* Number input override */
input[type="number"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    padding: 0.8rem !important;
}
input[type="number"]:focus {
    border-color: rgba(102,126,234,0.8) !important;
    box-shadow: 0 0 20px rgba(102,126,234,0.3) !important;
}

/* Calculate button */
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(102,126,234,0.5); }
    50%       { box-shadow: 0 0 40px rgba(102,126,234,0.9); }
}
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.9rem 2rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    animation: pulse 2.5s ease-in-out infinite !important;
    transition: transform 0.2s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    background: linear-gradient(135deg, #764ba2, #667eea) !important;
    animation: none !important;
    box-shadow: 0 12px 35px rgba(102,126,234,0.7) !important;
}

/* Stat cards */
@keyframes countUp { from { opacity: 0; } to { opacity: 1; } }
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: fadeInUp 0.5s ease both;
}
.stat-card:hover {
    background: rgba(102,126,234,0.2);
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    border-color: rgba(102,126,234,0.4);
}
.stat-icon  { font-size: 1.6rem; margin-bottom: 4px; }
.stat-value { font-size: 1.25rem; font-weight: 700; color: white; margin: 4px 0; }
.stat-label { font-size: 0.72rem; color: rgba(255,255,255,0.45); letter-spacing: 0.5px; text-transform: uppercase; }

/* Table */
.table-wrapper {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    animation: fadeInUp 0.6s ease 0.2s both;
}
.results-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; font-family: 'Inter', sans-serif; }
.results-table thead th { padding: 14px 10px; font-weight: 600; font-size: 0.78rem; letter-spacing: 0.5px; text-transform: uppercase; border-bottom: 2px solid rgba(255,255,255,0.1); }
.th-item    { background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.7); text-align: left; padding-left: 20px !important; min-width: 130px; }
.th-quarter { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.9); text-align: center; }
.th-min     { background: rgba(66,133,244,0.22); color: #90caf9; text-align: center; }
.th-max     { background: rgba(234,115,51,0.22); color: #ffab76; text-align: center; }
.results-table tbody tr { transition: all 0.2s ease; border-bottom: 1px solid rgba(255,255,255,0.04); }
.results-table tbody tr:hover { background: rgba(102,126,234,0.12) !important; transform: scaleX(1.002); cursor: pointer; }
.q-divider { border-left: 1px solid rgba(255,255,255,0.07) !important; }
.row-group-kep td { border-left: 3px solid #4285f4; }
.row-group-keh td { border-left: 3px solid #34a853; }
.row-group-sim td { border-left: 3px solid #ea4335; }
.row-group-bal td { border-left: 3px solid #fbbc04; }
.cell-item    { padding: 10px 10px 10px 18px; font-weight: 700; font-size: 0.88rem; color: white; }
.cell-label   { padding: 4px 10px 4px 18px; color: rgba(255,255,255,0.38); font-size: 0.7rem; font-style: italic; }
.cell-y-min   { padding: 5px 10px; text-align: center; color: #90caf9; font-weight: 500; font-size: 0.8rem; }
.cell-y-max   { padding: 5px 10px; text-align: center; color: #ffab76; font-weight: 500; font-size: 0.8rem; }
.cell-rm-min  { padding: 4px 10px; text-align: center; color: #80deea; font-size: 0.76rem; font-family: 'Courier New', monospace; }
.cell-rm-max  { padding: 4px 10px; text-align: center; color: #ffcc80; font-size: 0.76rem; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Computation
# -----------------------------------------------------------------------
def compute_table(I_income):
    quarters = P_TYPES[P_NAME]
    alpha    = ALPHA_SCENARIOS[ALPHA_NAME]
    results  = {}

    for q_name, p in quarters.items():
        q_income = p * I_income
        E_kep = alpha['Keperluan'] * q_income
        E_keh = alpha['Kehendak']  * q_income
        E_sim = alpha['Simpanan']  * q_income
        E_map = {'Keperluan': E_kep, 'Kehendak': E_keh, 'Simpanan': E_sim}

        results[q_name] = {}
        sum_y = {
            'min': {'Keperluan':0,'Kehendak':0,'Simpanan':0},
            'max': {'Keperluan':0,'Kehendak':0,'Simpanan':0},
        }

        for col in ALL_COLS:
            grp    = GROUP_MAP[col]
            E_k    = E_map[grp]
            stats  = Y_DATA[q_name][col]
            y_min  = stats['p5']
            y_max  = stats['p95']
            results[q_name][col] = {
                'y_min':  round(y_min, 4),
                'y_max':  round(y_max, 4),
                'rm_min': round(y_min * E_k, 2),
                'rm_max': round(y_max * E_k, 2),
            }
            sum_y['min'][grp] += y_min
            sum_y['max'][grp] += y_max

        # Balance: min = max spending (p95), max = min spending (p5)
        bal_min = round(E_kep*(1-sum_y['max']['Keperluan']) + E_keh*(1-sum_y['max']['Kehendak']) + E_sim*(1-sum_y['max']['Simpanan']), 2)
        bal_max = round(E_kep*(1-sum_y['min']['Keperluan']) + E_keh*(1-sum_y['min']['Kehendak']) + E_sim*(1-sum_y['min']['Simpanan']), 2)
        results[q_name]['BALANCE'] = {'rm_min': bal_min, 'rm_max': bal_max}

    return results

# -----------------------------------------------------------------------
# HTML Table
# -----------------------------------------------------------------------
def build_table(data):
    q_labels  = ['Q1','Q2','Q3','Q4']
    grp_cls   = {'Keperluan':'row-group-kep','Kehendak':'row-group-keh','Simpanan':'row-group-sim'}
    grp_icon  = {'Keperluan':'🏠','Kehendak':'💎','Simpanan':'💰'}
    grp_color = {'Keperluan':'rgba(66,133,244,0.20)','Kehendak':'rgba(52,168,83,0.20)','Simpanan':'rgba(234,67,53,0.20)'}
    grp_txt   = {'Keperluan':'#90caf9','Kehendak':'#a5d6a7','Simpanan':'#ef9a9a'}

    html = '<div class="table-wrapper"><table class="results-table"><thead><tr>'
    html += '<th class="th-item" rowspan="2">Item</th>'
    for q in q_labels:
        html += f'<th class="th-quarter q-divider" colspan="2">{q}</th>'
    html += '</tr><tr>'
    for _ in q_labels:
        html += '<th class="th-min q-divider">Min</th><th class="th-max">Max</th>'
    html += '</tr></thead><tbody>'

    prev_grp = None
    for col in ALL_COLS:
        grp = GROUP_MAP[col]
        if grp != prev_grp:
            nc = 1 + len(q_labels)*2
            html += f'<tr><td colspan="{nc}" style="background:{grp_color[grp]};color:{grp_txt[grp]};font-weight:700;font-size:0.78rem;letter-spacing:1.5px;text-transform:uppercase;padding:7px 18px;border-top:1px solid rgba(255,255,255,0.06);">{grp_icon[grp]} &nbsp; {grp}</td></tr>'
            prev_grp = grp

        g = grp_cls[grp]
        d_label = ITEM_DISPLAY[col]
        html += f'<tr class="row-item-name {g}"><td class="cell-item">{d_label}</td>'
        for q in q_labels:
            d = data.get(q,{}).get(col,{})
            html += f'<td class="cell-y-min q-divider">{d.get("y_min",0):.4f}</td>'
            html += f'<td class="cell-y-max">{d.get("y_max",0):.4f}</td>'
        html += '</tr>'

        html += f'<tr class="row-rm {g}"><td class="cell-label">RM</td>'
        for q in q_labels:
            d = data.get(q,{}).get(col,{})
            html += f'<td class="cell-rm-min q-divider">RM {d.get("rm_min",0):,.2f}</td>'
            html += f'<td class="cell-rm-max">RM {d.get("rm_max",0):,.2f}</td>'
        html += '</tr>'

    # Balance
    nc = 1 + len(q_labels)*2
    html += f'<tr><td colspan="{nc}" style="background:rgba(255,215,0,0.10);color:#ffe082;font-weight:700;font-size:0.78rem;letter-spacing:1.5px;text-transform:uppercase;padding:7px 18px;border-top:1px solid rgba(255,255,255,0.06);">📊 &nbsp; Quarterly Balance</td></tr>'

    html += '<tr class="row-group-bal"><td class="cell-item" style="color:#ef9a9a;font-size:0.82rem;">Minimum</td>'
    for q in q_labels:
        rm = data.get(q,{}).get('BALANCE',{}).get('rm_min',0)
        html += f'<td class="cell-rm-min q-divider" colspan="2" style="text-align:center;color:#ef9a9a;">RM {rm:,.2f}</td>'
    html += '</tr>'

    html += '<tr class="row-group-bal"><td class="cell-item" style="color:#a5d6a7;font-size:0.82rem;">Maximum</td>'
    for q in q_labels:
        rm = data.get(q,{}).get('BALANCE',{}).get('rm_max',0)
        html += f'<td class="cell-rm-max q-divider" colspan="2" style="text-align:center;color:#a5d6a7;">RM {rm:,.2f}</td>'
    html += '</tr>'

    html += '</tbody></table></div>'
    return html

# -----------------------------------------------------------------------
# App Layout
# -----------------------------------------------------------------------

# Hero
st.markdown("""
<div class="hero">
    <p class="hero-title">💰 Retirement Budget Optimizer</p>
    <p class="hero-sub">Enter your annual income to generate your personalized retirement budget allocation</p>
</div>
""", unsafe_allow_html=True)

# Centered income input
_, mid, _ = st.columns([1, 1.4, 1])
with mid:
    st.markdown('<p class="input-label">💵 Annual Income (RM)</p>', unsafe_allow_html=True)
    I_income = st.number_input(
        "", min_value=1000, max_value=9_999_999,
        value=100000, step=1000,
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    calc_btn = st.button("⚡ Calculate Budget Allocation", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Results
if calc_btn:
    progress_bar = st.progress(0)
    status       = st.empty()
    steps = [
        (25,  "📊 Computing quarterly allocations..."),
        (55,  "💹 Calculating y values and RM amounts..."),
        (85,  "⚖️  Estimating quarterly balances..."),
        (100, "✅ Done!"),
    ]
    for pct, msg in steps:
        status.markdown(f"<div style='text-align:center;color:rgba(255,255,255,0.6);font-size:0.9rem;'>{msg}</div>", unsafe_allow_html=True)
        progress_bar.progress(pct)
        time.sleep(0.3)
    progress_bar.empty()
    status.empty()

    data = compute_table(I_income)

    # Metric cards
    total_min = sum(data.get(q,{}).get('BALANCE',{}).get('rm_min',0) for q in ['Q1','Q2','Q3','Q4'])
    total_max = sum(data.get(q,{}).get('BALANCE',{}).get('rm_max',0) for q in ['Q1','Q2','Q3','Q4'])

    c1, c2, c3 = st.columns(3)
    for col_w, icon, val, lbl in [
        (c1, "💵", f"RM {I_income:,}",         "Annual Income"),
        (c2, "📉", f"RM {total_min:,.2f}",      "Total Minimum Balance"),
        (c3, "📈", f"RM {total_max:,.2f}",      "Total Maximum Balance"),
    ]:
        with col_w:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value">{val}</div>
                <div class="stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.8rem;'>
        <div style='color:white;font-size:1.05rem;font-weight:600;'>📋 Budget Allocation Table</div>
        <div style='color:rgba(255,255,255,0.35);font-size:0.78rem;'>Staircase &nbsp;|&nbsp; Scenario 2 (0.55 / 0.25 / 0.20)</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(build_table(data), unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:2rem;color:rgba(255,255,255,0.3);font-size:0.9rem;'>
        Enter your income above and click <b style='color:rgba(255,255,255,0.5)'>Calculate</b> to see your budget allocation
    </div>""", unsafe_allow_html=True)
