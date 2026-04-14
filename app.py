import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(page_title="Advanced Flotation: Materials & Economics", layout="wide")

# Title
st.write(r"$\huge \text{Kinetic Model \& Plant Economics}$")
st.markdown(r"""
$\text{This model integrates }\mathbf{Surface\ Physics}\text{ with }\mathbf{Plant\ Scaling.}$  
$\text{Adjust throughput and cell size to see how kinetics translate into costs.}$
""")

# -------------------------
# Sidebar: Material & Physics
# -------------------------
st.sidebar.markdown(r"$\text{Material \& Physics}$")

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

# -------------------------
# Sidebar: Plant Scaling & Costs
# -------------------------
st.sidebar.markdown(r"$\text{Plant Scaling}$")

flow_rate = st.sidebar.number_input(
    r"$\text{Volumetric Flow Rate } Q \text{ (m}^3\text{/h)}$",
    10.0, 2000.0, 500.0
)

cell_volume = st.sidebar.number_input(
    r"$\text{Cell Volume } V \text{ (m}^3\text{)}$",
    1.0, 300.0, 150.0
)

energy_cost = st.sidebar.slider(
    r"$\text{Energy Cost (\$/kWh)}$",
    0.05, 0.30, 0.12
)

# -------------------------
# Physics Engine
# -------------------------
def calculate_advanced_kinetics(jg_cm_s, db_mm, ti_ms, dp_um, rho_p, gamma_mn_m, theta_deg):
    # Unit conversions
    jg_m = jg_cm_s / 100
    db_m = max(db_mm / 1000, 1e-9)
    dp_m = max(dp_um / 1_000_000, 1e-9)
    ti_s = ti_ms / 1000
    gamma_si = gamma_mn_m / 1000

    theta_rad = np.radians(theta_deg)

    rho_f = 1000
    g = 9.81

    # Bubble surface area flux
    S_b = (6 * jg_m) / db_m

    # Collision probability
    P_c = 3 * (dp_m / db_m)

    # Relative velocity
    v_rel = max(jg_m + 0.1, 1e-6)

    # Contact time
    t_s = (db_m / v_rel) * np.log(max(3 * db_m / dp_m, 1.0001))

    # Attachment probability
    P_a = np.exp(-ti_s / max(t_s, 1e-6)) * (theta_deg / 90)
    P_a = np.clip(P_a, 0, 1)

    # Detachment vs attachment forces
    f_detach = (np.pi / 6) * (dp_m**3) * (rho_p - rho_f) * g
    f_attach = np.pi * dp_m * gamma_si * (np.sin(theta_rad)**2)

    Bo_mod = f_detach / max(f_attach, 1e-12)

    # Stability probability
    P_s = np.clip(1 - np.sqrt(Bo_mod) if Bo_mod < 1 else 0.01, 0.01, 1.0)

    # Kinetic constant (1/min)
    k_min = (S_b * P_c * P_a * P_s * 60) / 4

    return k_min


k_min = calculate_advanced_kinetics(1.5, 1.2, 25, 75, rho_p, 50, theta)

# -------------------------
# Economic Calculations
# -------------------------
tau = (cell_volume / flow_rate) * 60
recovery_plant = (k_min * tau) / (1 + k_min * tau)

capex = 250000 * (cell_volume / 50)**0.6
power_req = cell_volume * 1.5
annual_opex = power_req * 24 * 365 * energy_cost

# -------------------------
# Display Metrics
# -------------------------
st.divider()
st.markdown(r"$\Large \text{Plant Performance \& Economics}$")

m1, m2, m3, m4 = st.columns(4)

m1.latex(r"\text{Est. Recovery: } \mathbf{" + f"{recovery_plant*100:.1f}" + r"\%}")
m2.latex(r"\text{Res. Time: } \mathbf{" + f"{tau:.2f}" + r"\ \text{min}}")
m3.latex(r"\text{Est. CAPEX: } \mathbf{\$" + f"{capex/1000:.0f}" + r"k}")
m4.latex(r"\text{Annual Power: } \mathbf{\$" + f"{annual_opex/1000:.0f}" + r"k}")

# -------------------------
# Visualizations
# -------------------------
st.divider()

c1, c2 = st.columns(2)

with c1:
    volumes = np.linspace(10, 500, 50)
    taus = (volumes / flow_rate) * 60
    recs = (k_min * taus) / (1 + k_min * taus) * 100

    fig_v, ax_v = plt.subplots()
    ax_v.plot(volumes, recs)
    ax_v.axvline(cell_volume, linestyle="--")
    ax_v.set_title(r"$\text{Recovery vs. Cell Volume}$")
    ax_v.set_xlabel(r"$\text{Cell Volume (m}^3\text{)}$")
    ax_v.set_ylabel(r"$\text{Recovery (\%)}$")
    st.pyplot(fig_v)

with c2:
    capex_curve = 250000 * (volumes / 50)**0.6 / 1000

    fig_cost, ax_cost = plt.subplots()
    ax_cost.plot(volumes, capex_curve)
    ax_cost.set_title(r"$\text{Capital Investment Sizing}$")
    ax_cost.set_xlabel(r"$\text{Cell Volume (m}^3\text{)}$")
    ax_cost.set_ylabel(r"$\text{Estimated CAPEX (\$k)}$")
    st.pyplot(fig_cost)

# -------------------------
# Formulas Section
# -------------------------
with st.expander("Show Economic Formulas"):
    st.latex(r"\tau = \frac{V_{cell}}{Q_{flow}} \cdot 60")
    st.latex(r"R = \frac{k \cdot \tau}{1 + k \cdot \tau}")
    st.latex(r"C_{cap} = C_{base} \left( \frac{V}{V_{base}} \right)^{0.6}")
