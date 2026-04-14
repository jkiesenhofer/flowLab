import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Industrial Flotation: Kinetics & Economics",
    layout="wide"
)

# -------------------------
# Title & Description
# -------------------------
st.latex(r"\huge \text{Kinetic Model \& Plant Economics}")

st.markdown(r"""
$$
\text{This model integrates } \mathbf{Surface\ Physics}
\text{ with } \mathbf{Plant\ Scaling.}
$$
""")

# -------------------------
# Sidebar: Material & Physics
# -------------------------
st.sidebar.markdown(r"### $\text{Material Properties}$")

minerals = {
    "Chalcopyrite (CuFeS2)": {"rho": 4200, "theta": 75},
    "Galena (PbS)": {"rho": 7500, "theta": 80},
    "Sphalerite (ZnS)": {"rho": 4000, "theta": 65},
    "Quartz (SiO2)": {"rho": 2650, "theta": 10},
    "Coal (Bituminous)": {"rho": 1300, "theta": 60},
    "Custom Mineral": {"rho": 4500, "theta": 70}
}

selected_mineral = st.sidebar.selectbox("Select Mineral Type", list(minerals.keys()))

if selected_mineral == "Custom Mineral":
    rho_p = st.sidebar.number_input("Custom Density (kg/m³)", 1000.0, 10000.0, 4500.0)
    theta = st.sidebar.slider("Contact Angle (°)", 0, 110, 70)
else:
    rho_p = minerals[selected_mineral]["rho"]
    theta = st.sidebar.slider("Contact Angle (°)", 0, 110, minerals[selected_mineral]["theta"])

# Particle Size
dp_um = st.sidebar.slider("Particle Diameter ($d_p$) [µm]", 10, 250, 75)

# -------------------------
# Sidebar: Operational Parameters
# -------------------------
st.sidebar.markdown(r"### $\text{Operational Variables}$")

jg_cm_s = st.sidebar.slider("Air Velocity ($J_g$) [cm/s]", 0.5, 3.0, 1.5)
db_mm = st.sidebar.slider("Bubble Diameter ($d_b$) [mm]", 0.5, 3.0, 1.2)

# -------------------------
# Sidebar: Plant Scaling & Costs
# -------------------------
st.sidebar.markdown(r"### $\text{Plant Scaling}$")

flow_rate = st.sidebar.number_input(r"Volumetric Flow Rate $Q$ (m$^3$/h)", 10.0, 2000.0, 500.0)
cell_volume = st.sidebar.number_input(r"Cell Volume $V$ (m$^3$)", 1.0, 500.0, 150.0)
energy_cost = st.sidebar.slider("Energy Cost ($/kWh)", 0.05, 0.30, 0.12)

# -------------------------
# Physics Engine
# -------------------------
def calculate_advanced_kinetics(jg_cm_s, db_mm, ti_ms, dp_um, rho_p, gamma_mn_m, theta_deg):
    jg_m = jg_cm_s / 100
    db_m = max(db_mm / 1000, 1e-9)
    dp_m = max(dp_um / 1_000_000, 1e-9)
    ti_s = ti_ms / 1000
    gamma_si = gamma_mn_m / 1000
    theta_rad = np.radians(theta_deg)
    rho_f, g = 1000, 9.81

    # Kinetics Logic: S_b (Surface area flux), P_c (Collision), P_a (Attachment), P_s (Stability)
    S_b = (6 * jg_m) / db_m
    P_c = 3 * (dp_m / db_m)
    v_rel = max(jg_m + 0.1, 1e-6)
    t_s = (db_m / v_rel) * np.log(max(3 * db_m / dp_m, 1.0001))
    P_a = np.exp(-ti_s / max(t_s, 1e-6)) * (theta_deg / 90)
    P_a = np.clip(P_a, 0, 1)
    
    f_detach = (np.pi / 6) * (dp_m**3) * (rho_p - rho_f) * g
    f_attach = np.pi * dp_m * gamma_si * (np.sin(theta_rad)**2)
    Bo_mod = f_detach / max(f_attach, 1e-12)
    P_s = np.clip(1 - np.sqrt(Bo_mod) if Bo_mod < 1 else 0.01, 0.01, 1.0)

    k_min = (S_b * P_c * P_a * P_s * 60) / 4
    return k_min

# Calculate Current State
k_current = calculate_advanced_kinetics(jg_cm_s, db_mm, 25, dp_um, rho_p, 50, theta)
tau = (cell_volume / flow_rate) * 60
recovery_plant = (k_current * tau) / (1 + k_current * tau)

# Economics
capex = 250000 * (cell_volume / 50)**0.6
power_req = cell_volume * 1.5
annual_opex = power_req * 24 * 365 * energy_cost

# -------------------------
# Display Metrics
# -------------------------
st.divider()
st.latex(r"\Large \text{Plant Performance \& Economics}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Est. Recovery", f"{recovery_plant*100:.1f}%")
m2.metric("Res. Time", f"{tau:.2f} min")
m3.metric("Est. CAPEX", f"${capex/1000:.0f}k")
m4.metric("Annual Power", f"${annual_opex/1000:.0f}k")

# -------------------------
# Visualizations Row
# -------------------------
st.divider()
st.subheader("Process Sensitivity Analysis")

c1, c2, c3 = st.columns(3)

with c1:
    # Graph 1: Recovery vs Particle Size
    sizes = np.linspace(10, 300, 50)
    recs_size = []
    for s in sizes:
        k_val = calculate_advanced_kinetics(jg_cm_s, db_mm, 25, s, rho_p, 50, theta)
        recs_size.append((k_val * tau) / (1 + k_val * tau) * 100)
    
    fig1, ax1 = plt.subplots()
    ax1.plot(sizes, recs_size, color='teal', linewidth=2)
    ax1.axvline(dp_um, color='red', linestyle='--', label='Current $d_p$')
    ax1.set_title("Recovery vs. Particle size ($d_p$)")
    ax1.set_xlabel("Particle Size (µm)")
    ax1.set_ylabel("Recovery (%)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)

with c2:
    # Graph 2: Recovery vs Air Velocity (Jg)
    jgs = np.linspace(0.1, 4.0, 50)
    recs_jg = []
    for j in jgs:
        k_val = calculate_advanced_kinetics(j, db_mm, 25, dp_um, rho_p, 50, theta)
        recs_jg.append((k_val * tau) / (1 + k_val * tau) * 100)
        
    fig2, ax2 = plt.subplots()
    ax2.plot(jgs, recs_jg, color='darkorange', linewidth=2)
    ax2.axvline(jg_cm_s, color='red', linestyle='--', label='Current $J_g$')
    ax2.set_title("Recovery vs. Air Velocity ($J_g$)")
    ax2.set_xlabel("Superficial Gas Velocity (cm/s)")
    ax2.set_ylabel("Recovery (%)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

with c3:
    # Graph 3: Rate Constant (k) vs Bubble Diameter (db)
    dbs = np.linspace(0.5, 4.0, 50)
    ks_db = []
    for d in dbs:
        k_val = calculate_advanced_kinetics(jg_cm_s, d, 25, dp_um, rho_p, 50, theta)
        ks_db.append(k_val)
        
    fig3, ax3 = plt.subplots()
    ax3.plot(dbs, ks_db, color='mediumpurple', linewidth=2)
    ax3.axvline(db_mm, color='red', linestyle='--', label='Current $d_b$')
    ax3.set_title("Rate Constant ($k$) vs. Bubble Size ($d_b$)")
    ax3.set_xlabel("Bubble Diameter (mm)")
    ax3.set_ylabel("Kinetics $k$ (min⁻¹)")
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    st.pyplot(fig3)
