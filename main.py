import streamlit as st

st.set_page_config(page_title="Emergency Services India", layout="centered")

st.markdown("""
    <style>
    body {
        background: #f4f8fc;
    }
    .big-header {
        margin-top: 1.5rem;
        margin-bottom: 0.1rem;
        font-size: 2.4rem;
        font-weight: 700;
        text-align: center;
        color: #232c43;
    }
    .subtitle {
        text-align: center;
        color: #8195a7;
        font-size: 1.07rem;
        margin-bottom: 2.2rem;
    }
    .hotline-row {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    .hotline-card {
        background: white;
        border-radius: 1.1rem;
        padding: 1.1rem;
        box-shadow: 0px 2px 16px 0 #e0e6f2;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1.2rem;
        min-width: 120px;
    }
    .hotline-num {
        color: #ed3b42;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .hotline-label {
        color: #21233b; 
        font-size: 1.1rem;
        margin-bottom: 0.12rem;
        font-weight: 500;
    }
    .hotline-action {
        color: #528bc9;
        font-size: 0.85rem;
        margin-top: 0.35rem;
    }

    .loc-card {
        background: white;
        border-radius: 1rem;
        box-shadow: 0px 2px 10px #e2eaf5;
        padding: 2rem 2rem 0.7rem 2rem;
        max-width: 525px;
        margin: 1.8rem auto 1.3rem auto;
    }

    .search-btn {
        background: #17a2f8;
        color: white;
        width: 100%;
        font-size: 1.1rem;
        padding: 0.7rem;
        border: none;
        outline: none;
        border-radius: 0.8rem;
        font-weight: 600;
        transition: all 0.2s;
        margin-top: 0.4rem;
        margin-bottom: 0.6rem;
    }
    .search-btn:hover {
        background: #046fbb;
        cursor: pointer;
    }

    /* Service selection grid */
    .service-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.1rem;
        margin-top: 2.1rem; margin-bottom: 1.1rem;
        justify-items: center;
    }
    .service-box {
        background: white;
        border-radius: 1rem;
        border: 2px solid #e9eefa;
        display: flex;
        align-items: center;
        flex-direction: column;
        padding: 1.2rem 0.5rem 0.8rem 0.5rem;
        cursor: pointer;
        min-width: 115px;
        min-height: 93px;
        box-shadow: 0px 1.5px 10px 0 #eceff6;
        transition: border-color 0.17s, box-shadow 0.18s;
    }
    .service-box.selected {
        border: 2.7px solid #30a1e6;
        background: #eafdff;
        box-shadow: 0px 2.5px 14px 0 #cfe7f8;
    }
    .svc-ico {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
        color: #18a4ea;
    }
    .svc-label {
        font-size: 1rem;
        font-weight: 500;
        color: #233656;
    }
    .select-links {
        text-align: right;
        margin-right: 1.6rem;
        margin-bottom: 0.7rem;
        color: #12a2e2;
        font-size: 0.89rem;
    }
    .select-links span {
        cursor: pointer;
        margin-left: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---- HOTLINE CARDS ----
st.markdown('<div class="big-header">Emergency Hotlines</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Tap to call immediately</div>', unsafe_allow_html=True)
st.markdown("""
    <div class="hotline-row">
        <div class="hotline-card"><div class="hotline-num">100</div>
        <div class="hotline-label">Police</div><div class="hotline-action">📞 Tap to call</div></div>
        <div class="hotline-card"><div class="hotline-num">101</div>
        <div class="hotline-label">Fire</div><div class="hotline-action">📞 Tap to call</div></div>
        <div class="hotline-card"><div class="hotline-num">108</div>
        <div class="hotline-label">Ambulance</div><div class="hotline-action">📞 Tap to call</div></div>
        <div class="hotline-card"><div class="hotline-num">112</div>
        <div class="hotline-label">Emergency</div><div class="hotline-action">📞 Tap to call</div></div>
    </div>
""", unsafe_allow_html=True)

# ---- LOCATION INPUT ----
with st.container():
    st.markdown('<div class="loc-card">', unsafe_allow_html=True)
    loc = st.text_input("Location", value="", placeholder="Enter city, area, or landmark...")
    use_current = st.button("Use Current")
    radius = st.selectbox("Search Radius", ["1 km","2 km","5 km","10 km","20 km","50 km"], index=2)
    st.markdown('<button class="search-btn">🔍 Search Services</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- SERVICE SELECTION ----
service_list = [
    ("Hospital", "🏥"), ("Clinic", "➕"), ("Pharmacy", "💊"), ("Doctors", "🩺"),
    ("Police", "🛡️"), ("Fire Station", "🔥"), ("Embassy", "🏛️"), ("ATM", "💳"),
    ("Tourist Office", "ℹ️")
]

# Store selection with session_state (simulate toggles)
if "svc_selected" not in st.session_state:
    st.session_state.svc_selected = {"Hospital", "Pharmacy", "Police"}

def toggle_service(idx):
    svc = service_list[idx][0]
    if svc in st.session_state.svc_selected:
        st.session_state.svc_selected.remove(svc)
    else:
        st.session_state.svc_selected.add(svc)

def select_all():
    st.session_state.svc_selected = set([svc for svc, _ in service_list])
def clear_all():
    st.session_state.svc_selected = set()

st.markdown('<div class="section-header" style="font-size:1.25rem;margin-top:1.8rem;" >Select Services'
            '<span class="select-links">'
            '<span onclick="window.parent.postMessage({eventType:\'selectAll\'}, \'*\')">Select All</span>|'
            '<span onclick="window.parent.postMessage({eventType:\'clearAll\'}, \'*\')">Clear All</span>'
            '</span>'
            '</div>', unsafe_allow_html=True)

# Service grid
cols = st.columns(4)
curr = 0
for row in range((len(service_list) + 3)//4):
    for col in cols:
        idx = row*4+cols.index(col)
        if idx >= len(service_list):
            continue
        svc, ico = service_list[idx]
        is_selected = svc in st.session_state.svc_selected
        sel_cls = "service-box selected" if is_selected else "service-box"
        with col:
            st.markdown(f"""
                <div class="{sel_cls}" 
                     onclick="window.parent.postMessage({{eventType:'svc{idx}'}}, '*')">
                  <div class="svc-ico">{ico}</div>
                  <div class="svc-label">{svc}</div>
                </div>
            """, unsafe_allow_html=True)
    curr += 1

st.markdown(
    '<div style="text-align:center;color:#7c8ea6;font-size:1rem;padding-top:1.9rem;">'
    'Enter a location and select services to start searching for emergency resources near you.</div>',
    unsafe_allow_html=True
)
