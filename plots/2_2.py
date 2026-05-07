import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 26
})

# ========================================================================
# Helper Functions
# ========================================================================

def first_derivative_matrix(x):
    """Generates the 1st derivative operator matrix using central differences."""
    n = len(x)
    D = np.zeros((n, n))
    dx = x[1] - x[0]
    for i in range(1, n-1):
        D[i, i-1] = -1.0 / (2.0 * dx)
        D[i, i+1] =  1.0 / (2.0 * dx)
    D[0, 0] = -3.0 / (2.0 * dx); D[0, 1] = 4.0 / (2.0 * dx); D[0, 2] = -1.0 / (2.0 * dx)
    D[-1, -1] = 3.0 / (2.0 * dx); D[-1, -2] = -4.0 / (2.0 * dx); D[-1, -3] = 1.0 / (2.0 * dx)
    return D

def added_mass_coefficient(H, Rb):
    """Calculates added mass coefficient and its spatial derivative for the bubble."""
    zeta = max((H + Rb) / Rb, 1.0 + 1e-12)
    Cm = 0.5 + 0.19222 * zeta**(-3.019) + 0.06214 * zeta**(-8.331) + \
         0.0348 * zeta**(-24.65) + 0.0139 * zeta**(-120.7)
    dCm_dH = (-3.019 * 0.19222 * zeta**(-4.019) - 8.331 * 0.06214 * zeta**(-9.331) - \
              24.65 * 0.0348 * zeta**(-25.65) - 120.7 * 0.0139 * zeta**(-121.7)) / Rb
    return Cm, dCm_dH

def calculate_history_force(accel_hist, time_hist, current_time, Rb, mu, rho):
    """Calculates the Basset history integral."""
    valid = (time_hist > 0) & (current_time > time_hist)
    tau = current_time - time_hist[valid]
    accel = accel_hist[valid]
    F_hist = 0.0
    if len(tau) > 1:
        kernel = 6.0 * Rb**2 * np.sqrt(np.pi * rho * mu) / np.sqrt(tau)
        F_hist = np.trapz(kernel * accel, x=tau)
    return F_hist

def smoothstep(val, start, end):
    """Smooth transition between states."""
    if val >= start: return 0.0
    if val <= end: return 1.0
    t = (start - val) / (start - end)
    return t * t * (3.0 - 2.0 * t)

def solve_implicit_step_spheres(h_current, h_prev, D, r, dt, mu_c, v_rel, Rb, Rs, sigma, P_edge, Reff_geom):
    """Solves the 1D Reynolds Equation implicitly for two approaching spheres."""
    N = len(r) - 1
    Np1 = N + 1
    A = np.zeros((2*Np1, 2*Np1))
    B = np.zeros(2*Np1)
    
    A[:Np1, :Np1] = (3.0 / (2.0 * dt)) * np.eye(Np1)
    lambda_mob = 4.0 
    diag_1_r = np.diag(1.0 / r); diag_r = np.diag(r); diag_h3 = np.diag(h_current**3)
    mat_mult = np.linalg.multi_dot([diag_1_r, D, diag_r, diag_h3, -D])
    A[:Np1, Np1:] = (lambda_mob / (12.0 * mu_c)) * mat_mult
    B[:Np1] = 2.0 * h_current / dt - h_prev / (2.0 * dt)
    
    Laplacian = np.linalg.multi_dot([diag_1_r, D, diag_r, D])
    A[Np1:, :Np1] = sigma * Laplacian
    A[Np1:, Np1:] = np.eye(Np1)
    
    h_ideal = (r**2) / (2.0 * Reff_geom)
    B[Np1:] = P_edge * np.ones(Np1) + sigma * Laplacian.dot(h_ideal)
    
    A[0, :] = 0.0; A[0, :Np1] = D[0, :]; B[0] = 0.0
    B[N] = (-v_rel + (2.0/dt)*h_current[-1] - (1.0/(2.0*dt))*h_prev[-1]) * (2.0*dt) / 3.0
    A[N, :] = 0.0; A[N, N] = 1.0; 
    A[Np1, :] = 0.0; A[Np1, Np1:] = D[0, :]; B[Np1] = 0.0
    A[-1, :] = 0.0; A[-1, -1] = 1.0; B[-1] = P_edge
    
    sol = np.linalg.solve(A, B)
    return sol[:Np1], sol[Np1:]

# ========================================================================
# Physics Force Calculations
# ========================================================================
def calculate_bubble_forces(h_profile, P, r, v_b, V_b, Rb, Rs, z_b, z_s, rho_c, rho_b, mu_c, g, current_time, accel_history, time_history, sigma, P_static, Reff_geom, St, osc_amp, phase_shift):
    P_hydro = P - P_static
    F_buoyancy = (rho_c - rho_b) * g * V_b
    
    Gamma = 0.5 
    F_lubrication = Gamma * (2.0 * np.pi * np.trapz(r * P_hydro, x=r))
    
    Re = max(rho_c * abs(v_b) * (2*Rb) / mu_c, 1e-12)
    Eo = g * (rho_c - rho_b) * ((2*Rb)**2) / sigma
    Cd_base = max(min((24/Re)*(1+0.15*Re**0.687), 72/Re), (8/3)*(Eo/(Eo+4)))
    F_drag_base = 0.5 * Cd_base * rho_c * (np.pi * Rb**2) * (v_b**2) * np.sign(v_b)
    
    gap = max(z_s - z_b - (Rb + Rs), 1e-12)
    
    f_oscillation = (St * abs(v_b)) / (2.0 * Rb) 
    wobble_active = smoothstep(gap, start=4.0*Rb, end=1.0*Rb) if gap > 1.0*Rb else 0.0
    drag_modifier = 1.0 - (osc_amp * np.cos(2.0 * np.pi * f_oscillation * current_time + phase_shift))
    F_drag_b = F_drag_base * (drag_modifier * wobble_active + 1.0 * (1 - wobble_active))

    Cm, dCm_dH = added_mass_coefficient(gap, Rb)
    kappa = 0.0 
    F_added_mass_spatial = kappa * (rho_c * V_b * dCm_dH * (v_b**2))
    F_history = calculate_history_force(accel_history, time_history, current_time, Rb, mu_c, rho_c)
    M_eff_b = Cm * rho_c * V_b + rho_b * V_b
    
    return F_buoyancy, F_lubrication, F_drag_b, F_history, F_added_mass_spatial, M_eff_b

def calculate_sphere_forces(v_s, Rs, rho_s, rho_c, mu_c, g):
    V_s = (4/3) * np.pi * Rs**3
    F_net_weight = (rho_s - rho_c) * g * V_s
    
    Re_s = max(rho_c * abs(v_s) * (2*Rs) / mu_c, 1e-12)
    Cd_s = (24/Re_s) * (1 + 0.15 * Re_s**0.687) 
    F_drag_s = 0.5 * Cd_s * rho_c * (np.pi * Rs**2) * (v_s**2) * np.sign(v_s)
    
    M_eff_s = (rho_s * V_s) + 0.5 * (rho_c * V_s)
    
    return F_net_weight, F_drag_s, M_eff_s

# ========================================================================
# Plotting Functions
# ========================================================================
def plot_results(T, r, zb_s, zs_s, vb_s, vs_s, Fb, Flub, Fdrag_b, Fdrag_s, h_store, Rb, Rs, dt):
    plt.style.use('bmh')
    
    fig, (ax_pos, ax_vel, ax_force, ax_film) = plt.subplots(4, 1, figsize=(10, 18), gridspec_kw={'height_ratios': [1.5, 1.5, 2, 2]})
    
    # 1. POSITION PLOT
    ax_pos.plot(T, zb_s * 1000, 'b-', lw=2, label='Bubble Z-Position (Rising)')
    ax_pos.plot(T, zs_s * 1000, 'r--', lw=2, label='Particle Z-Position (Falling)')
    ax_pos.set_ylabel('Position (mm)')
    ax_pos.set_title('Trajectory of Approaching Bodies')
    ax_pos.legend()
    ax_pos.grid(True)
    
    # 2. VELOCITY PLOT
    ax_vel.plot(T, vb_s, 'b-', lw=2, label='Bubble Velocity (Positive = Up)')
    ax_vel.plot(T, vs_s, 'r--', lw=2, label='Particle Velocity (Negative = Down)')
    ax_vel.set_ylabel('Velocity (m/s)')
    ax_vel.legend()
    ax_vel.grid(True)
    
    # 3. FORCE PLOT
    ax_force.plot(T, Fb, 'b:', label='Bubble Buoyancy (+)')
    ax_force.plot(T, -Flub, color='firebrick', label='Lubrication on Bubble (-)')
    ax_force.plot(T, -Fdrag_b, color='rebeccapurple', label='Bubble Drag (-)')
    ax_force.plot(T, -Fdrag_s, color='darkorange', label='Particle Drag (Opposes fall)')
    ax_force.set_ylim(-0.001, 0.001)
    ax_force.set_ylabel('Force (N)')
    ax_force.legend(ncol=2)
    ax_force.grid(True)
    
    # 4. FILM PROFILE PLOT
    impact_idx = np.argmin(h_store[:, 0])
    start_idx = max(0, impact_idx - int(0.010 / dt))
    end_idx = min(len(T)-1, impact_idx + int(0.002 / dt))
    
    if start_idx >= end_idx:
        snapshot_indices = [len(T)-1]
    else:
        snapshot_indices = np.linspace(start_idx, end_idx, 6, dtype=int)
        
    colors = plt.cm.viridis(np.linspace(0, 1, len(snapshot_indices)))
    
    for i, idx in enumerate(snapshot_indices):
        ax_film.plot(r * 1000, h_store[idx, :] * 1000, color=colors[i], lw=2, label=f't = {T[idx]:.4f} s')
    
    ax_film.axhline(0, color='black', lw=2, label='Equivalent Contact Plane')
    ax_film.set_ylabel('Gap Height, h (mm)')
    ax_film.set_xlabel('Radial Distance, r (mm)')
    ax_film.set_title('Film Profile Evolution (Near Collision)')
    ax_film.legend(loc='upper right')
    ax_film.grid(True)
    
    plt.tight_layout()
    plt.show()

def plot_3d_impact(T, r, h_store, Rb, Rs):
    """Generates a 3D surface plot showing the FULL particle and EXTENDED bubble."""
    impact_idx = np.argmin(h_store[:, 0])
    h_impact = h_store[impact_idx, :]
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # ==========================================
    # 1. CREATE FULL SOLID SPHERE (Particle)
    # ==========================================
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    X_s = Rs * np.outer(np.cos(u), np.sin(v))
    Y_s = Rs * np.outer(np.sin(u), np.sin(v))
    Z_s = Rs - Rs * np.outer(np.ones(np.size(u)), np.cos(v)) # Shifts sphere so bottom touches Z=0
    
    ax.plot_surface(X_s*1000, Y_s*1000, Z_s*1000, color='silver', alpha=0.7, 
                    rstride=2, cstride=2, linewidth=0.2, edgecolor='gray')

    # ==========================================
    # 2. CREATE EXTENDED BUBBLE SURFACE
    # ==========================================
    R_plot_max = 0.95 * Rb # Plot out to 95% of the bubble's full radius
    
    x = np.linspace(-R_plot_max, R_plot_max, 150)
    y = np.linspace(-R_plot_max, R_plot_max, 150)
    X_b, Y_b = np.meshgrid(x, y)
    R_grid = np.sqrt(X_b**2 + Y_b**2)
    
    Z_b = np.full_like(R_grid, np.nan) # Empty surface
    
    # A) Inside the interaction zone (apply the physics deformation)
    r_edge = r[-1]
    inside = R_grid <= r_edge
    Z_p_1d = Rs - np.sqrt(np.maximum(Rs**2 - r**2, 0)) # Exact particle bottom profile
    Z_b_1d = Z_p_1d - h_impact                         # Subtract simulated gap height
    Z_b[inside] = np.interp(R_grid[inside], r, Z_b_1d)
    
    # B) Outside the interaction zone (attach undeformed spherical dome)
    outside = (R_grid > r_edge) & (R_grid <= R_plot_max)
    z_edge = Z_b_1d[-1]
    
    # Find the theoretical center of the bubble to make the edges match seamlessly
    C_z = z_edge - np.sqrt(max(Rb**2 - r_edge**2, 0)) 
    
    # Calculate the remaining undeformed sphere
    val = Rb**2 - R_grid[outside]**2
    val[val < 0] = 0 # Prevent imaginary numbers at extreme edges
    Z_b[outside] = C_z + np.sqrt(val)
    
    surf = ax.plot_surface(X_b*1000, Y_b*1000, Z_b*1000, cmap='viridis', alpha=0.9, 
                           rstride=2, cstride=2, linewidth=0, antialiased=True)
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Relative Z Height (mm)')
    ax.set_title(f'3D Reconstruction: Solid Particle Impacting Bubble\n(t = {T[impact_idx]:.4f} s)')
    ax.set_xlabel('X (mm) - Radial Axis')
    ax.set_ylabel('Y (mm) - Radial Axis')
    ax.set_zlabel('Z (mm) - Vertical Height')
    
    # Adjust viewing angle for best look at the interaction gap
    ax.view_init(elev=0, azim=45)
    
    # Force 1:1:1 True Geometric Aspect Ratio so spheres aren't stretched
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()
    
    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)
    
    plot_radius = 0.5 * max([x_range, y_range, z_range])
    
    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    
    plt.tight_layout()
    plt.show()

# ========================================================================
# Main Execution
# ========================================================================
def main():
    # --- GEOMETRY & PROPERTIES ---
    Rb = 0.00175             # Bubble radius (1.75 mm)
    Rs = 0.00035             # Solid sphere radius (0.35 mm)
    rho_s = 2500.0           # Solid sphere density (e.g. Glass)
    sigma, mu_c, rho_c, rho_b, g = 0.072, 1.0e-3, 998.0, 1.2, 9.81
    
    V_b = (4/3)*np.pi*Rb**3
    Reff_geom = (Rb * Rs) / (Rb + Rs)  
    
    # GRID ADJUSTED TO FOCUS ON THE PARTICLE (rmax = 0.9 * Rs to ensure valid sphere math)
    N, rmax, dt = 50, 0.9 * Rs, 1.0e-5
    tf = 0.07 
    maxSteps = int(tf/dt)+1
    
    r = np.linspace(0, rmax, N+1); r[0] = (r[1]-r[0])/2.0
    D = first_derivative_matrix(r)
    
    H0 = 0.0149 
    activate_dist, blend_start, blend_end = 0.5*Rb, 0.5*Rb, 0.001*Rb
    h_mesh = 4.5e-5  
    
    St, osc_amp, phase_shift = 0.28, 0.25, 5.5

    print(f"Starting simulation. Max time: {tf}s, dt: {dt}s ...")
    
    z_b = 0.0
    z_s = H0 + Rb + Rs
    v_b = 0.0
    v_s = 0.0
    
    h_current = H0 + (r**2)/(2.0*Reff_geom)
    h_prev = np.copy(h_current)
    
    T_s, zb_s, zs_s, vb_s, vs_s, Fb_s, Fl_s, Fd_b_s, Fd_s_s = [np.zeros(maxSteps) for _ in range(9)]
    h_store = np.zeros((maxSteps, N+1)) 
    acc_h, time_h = np.zeros(100), np.zeros(100)
    
    t, i = 0.0, 0
    
    while t < tf and i < maxSteps:
        gap = z_s - z_b - (Rb + Rs)
        if gap < -0.8 * Rb: 
            print(f"Collision/Overlap reached at t = {t:.4f}s. Stopping.")
            break 
        
        v_rel = v_b - v_s 
        
        blend = smoothstep(gap, start=blend_start, end=blend_end)
        P_edge = 2.0*sigma/Rb + blend*(2.0*sigma/Reff_geom)
        
        if gap > activate_dist:
            h_new = max(gap, h_mesh) + (r**2)/(2.0*Reff_geom)
            P_new = np.full_like(r, P_edge)
        else:
            h_safe = np.maximum(h_current, h_mesh) 
            h_new, P_new = solve_implicit_step_spheres(h_safe, h_prev, D, r, dt, mu_c, v_rel, Rb, Rs, sigma, P_edge, Reff_geom)
            
        F_b, F_l_raw, F_d_b, F_h, F_am_s, M_eff_b = calculate_bubble_forces(
            h_new, P_new, r, v_b, V_b, Rb, Rs, z_b, z_s, rho_c, rho_b, mu_c, g, t, acc_h, time_h, sigma, P_edge, Reff_geom, St, osc_amp, phase_shift)
        
        F_l = F_l_raw * blend
        F_net_weight_s, F_drag_s, M_eff_s = calculate_sphere_forces(v_s, Rs, rho_s, rho_c, mu_c, g)
        
        F_sum_b = F_b - F_d_b - F_l + F_am_s - F_h
        a_b = F_sum_b / M_eff_b
        v_b_next = v_b + a_b * dt
        z_b += v_b_next * dt
        
        F_sum_s = -F_net_weight_s - F_drag_s + F_l 
        a_s = F_sum_s / M_eff_s
        v_s_next = v_s + a_s * dt
        z_s += v_s_next * dt

        T_s[i], zb_s[i], zs_s[i] = t+dt, z_b, z_s
        vb_s[i], vs_s[i] = v_b, v_s
        Fb_s[i], Fl_s[i], Fd_b_s[i], Fd_s_s[i] = F_b, F_l, F_d_b, F_drag_s
        h_store[i, :] = h_new
        
        acc_h = np.roll(acc_h, 1); time_h = np.roll(time_h, 1)
        acc_h[0], time_h[0] = a_b, t
        h_prev, h_current = h_current, h_new
        v_b = v_b_next
        v_s = v_s_next
        t += dt
        i += 1

    print("Simulation Complete. Generating plots...")
    
    T_s, zb_s, zs_s = T_s[:i], zb_s[:i], zs_s[:i]
    vb_s, vs_s = vb_s[:i], vs_s[:i]
    Fb_s, Fl_s, Fd_b_s, Fd_s_s = Fb_s[:i], Fl_s[:i], Fd_b_s[:i], Fd_s_s[:i]
    h_store = h_store[:i, :]

    # Call both plotting functions (Make sure to pass Rb to the 3D plot)
    plot_results(T_s, r, zb_s, zs_s, vb_s, vs_s, Fb_s, Fl_s, Fd_b_s, Fd_s_s, h_store, Rb, Rs, dt)
    plot_3d_impact(T_s, r, h_store, Rb, Rs)

if __name__ == "__main__": 
    main()
