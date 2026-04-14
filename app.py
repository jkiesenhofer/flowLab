import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(page_title="Advanced Flotation: Materials & Surface Physics", layout="wide")

st.title(r"Kinetic Model: Material & Surface Properties")
st.markdown("""
This version integrates **Material Science** into the Schulze-Nguyen framework. 
The stability of the bubble-particle aggregate now depends on the **Mineral Density** and the **Contact Angle ($\theta$)**, which represents the surface hydrophobicity.
""")

# -------------------------
# Sidebar: Material Selection
# -------------------------
st.sidebar.header("Material Selection")

# Dictionary of minerals with density (kg/m3) and typical contact angle (degrees)
minerals = {
    "Chalcopyrite (CuFeS2)": {"rho": 4200, "theta": 75},
    "Galena (PbS)": {"rho": 7500, "theta": 80},
    "Sphalerite (ZnS)": {"rho": 4000, "theta": 65},
    "Quartz (SiO2) - Hydrophilic": {"rho": 2650, "theta": 10},
    "Coal (Bituminous)": {"rho": 1300, "theta": 60},
    "Custom Mineral": {"rho": 4500, "theta": 70}
}

selected_mineral = st.sidebar.selectbox("Select Mineral Type", list(minerals.keys()))

# Allow manual override for custom mineral
if selected_mineral == "Custom Mineral":
    rho_p = st.sidebar.number_input("Custom Density (kg/m³)", 1000, 10000, 4500)
    theta = st.sidebar.slider("Custom Contact Angle (°)", 0, 110, 70)
else:
    rho_p = minerals[selected_mineral]["rho"]
    theta = st.sidebar.slider("Adjust Contact Angle (°)", 0, 110, minerals[selected_mineral]["theta"])

# -------------------------
# Sidebar: Physics Parameters
# -------------------------
st.sidebar.header("Hydrodynamics")
J_g = st.sidebar.slider(r"Gas Velocity $J_g$ (cm/s)", 0.1, 5.0, 1.5, 0.1)
D_b = st.sidebar.slider(r"Bubble Diameter $D_b$ (mm)", 0.5, 5.0, 1.2, 0.1)

st.sidebar.header("Surface Physics")
t_i = st.sidebar.slider(r"Induction Time $t_i$ (ms)", 1, 100, 25, 1)
gamma = st.sidebar.slider("Surface Tension (mN/m)", 20, 72, 50) 
d_p = st.sidebar.slider(r"Particle Size $d_p$ ($\mu m$)", 10, 500, 75, 5)

# -------------------------
# Logic: Material-Specific Physics Engine
# -------------------------
def calculate_advanced_kinetics(J_g, D_b, t_i, d_p, rho_p, gamma, theta):
    # SI Unit Conversions
    jg_m = J_g / 100               
    db_m = D_b / 1000              
    dp_m = d_p / 1_000_000          
    ti_s = t_i / 1000              
    rho_f = 1000                   
    g = 9.81                       
    gamma_si = gamma / 1000        
    theta_rad = np.radians(theta)

    # 1. Bubble Surface Area Flux (Sb)
    S_b = (6 * jg_m) / db_m

    # 2. Probability of Collision (Pc)
    P_c = 3 * (dp_m / db_m)

    # 3. Probability of Adhesion (Pa) - Nguyen Sliding Time
    v_rel = jg_m + 0.1 
    t_s = (db_m / v_rel) * np.log(3 * db_m / dp_m)
    # Pa also scales with hydrophobicity (simplified)
    P_a = np.exp(-ti_s / t_s) * (theta/90) 
    P_a = np.clip(P_a, 0.0, 1.0)
    
    # 4. Probability of Stability (Ps) - Schulze Bond Number with Contact Angle
    # Attachment Force incorporates sin^2(theta) for the meniscus tenacity
    f_detach = (np.pi / 6) * (dp_m**3) * (rho_p - rho_f) * g
    f_attach = np.pi * dp_m * gamma_si * (np.sin(theta_rad)**2)
    
    Bo_mod = f_detach / f_attach if f_attach > 0 else 100
    
    if Bo_mod < 1:
        P_s = 1 - (Bo_mod)**0.5 # Schulze stability approximation
    else:
        P_s = 0.01 
    P_s = np.clip(P_s, 0.01, 1.0)

    # 5. Global Rate Constant k (min^-1)
    k_min = (S_b * P_c * P_a * P_s * 60) / 4
    
    return k_min, S_b, P_c, P_a, P_s

k_min, S_b, P_c, P_a, P_s = calculate_advanced_kinetics(J_g, D_b, t_i, d_p, rho_p, gamma, theta)

# -------------------------
# Display
# -------------------------
st.subheader(f"Current Mineral: {selected_mineral}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kinetic k", f"{k_min:.3f} min⁻¹")
m2.metric("Hydrophobicity (θ)", f"{theta}°")
m3.metric("Stability $P_s$", f"{P_s*100:.1f}%")
m4.metric("Density", f"{rho_p} kg/m³")

st.divider()

c1, c2 = st.columns(2)

with c1:
    # Recovery Plot
    t = np.linspace(0, 20, 200)
    rec = 1 - np.exp(-k_min * t)
    fig_rec, ax_rec = plt.subplots()
    ax_rec.plot(t, rec * 100, color="darkcyan", lw=3)
    ax_rec.set_title(f"Recovery Curve: {selected_mineral}")
    ax_rec.set_xlabel("Time (min)")
    ax_rec.set_ylabel("Recovery (%)")
    ax_rec.grid(alpha=0.3)
    st.pyplot(fig_rec)

with c2:
    # Comparison: Current vs Quartz (Gangue)
    dp_range = np.linspace(10, 400, 100)
    k_mineral = []
    k_quartz = []
    for dp in dp_range:
        k_m, _, _, _, _ = calculate_advanced_kinetics(J_g, D_b, t_i, dp, rho_p, gamma, theta)
        k_q, _, _, _, _ = calculate_advanced_kinetics(J_g, D_b, t_i, dp, 2650, gamma, 10)
        k_mineral.append(k_m)
        k_quartz.append(k_q)
    
    fig_comp, ax_comp = plt.subplots()
    ax_comp.plot(dp_range, k_mineral, color="orange", lw=3, label=selected_mineral)
    ax_comp.plot(dp_range, k_quartz, color="gray", lw=2, linestyle="--", label="Quartz (Gangue)")
    ax_comp.set_title("Selectivity: Mineral vs. Quartz")
    ax_comp.set_xlabel("Particle Size (µm)")
    ax_comp.set_ylabel("Rate k (min⁻¹)")
    ax_comp.legend()
    st.pyplot(fig_comp)

# -------------------------
# Theoretical Notes
# -------------------------
st.divider()
st.header("Theoretical Formulas: Solid Properties")

with st.expander("Show Stability & Surface Math"):
    st.markdown(r"""
    ### 1. The Influence of Contact Angle ($\theta$)
    The Contact Angle represents the hydrophobicity of the solid. In the Schulze model, the attachment force (capillary force) is proportional to the tension and the contact angle:
    $$F_{attach} = \pi \cdot d_p \cdot \gamma \cdot \sin^2(\theta)$$
    
    ### 2. The Modified Bond Number ($Bo$)
    Stability decreases as the density difference ($\Delta \rho$) increases or the contact angle decreases:
    $$Bo = \frac{g \cdot d_p^2 \cdot (\rho_p - \rho_f)}{\gamma \cdot \sin^2(\theta)}$$
    
    ### 3. Selectivity
    A mineral is "floatable" if its $k$ is significantly higher than the gangue (Quartz). Notice how low contact angles ($\theta < 20^\circ$) essentially zero out the $P_a$ and $P_s$ parameters.
    """)
