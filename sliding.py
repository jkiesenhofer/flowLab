import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from matplotlib.patches import Arc

# Configure Matplotlib fonts
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "cm"
})

def animate_rising_bubble_physical():
    # -------------------------------------------------------------------------
    # Physical Dimensions (all spatial coordinates in millimeters)
    # -------------------------------------------------------------------------
    D_bubble = 2.0         # Bubble diameter (mm)
    R = D_bubble / 2.0      # Bubble radius = 1.0 mm
    
    D_particle = 0.8       # Particle diameter (mm)
    r_p = D_particle / 2.0  # Particle radius = 0.4 mm
    
    U_rise = 10.0          # Bubble rise velocity (mm/s)
    g_eff = 15.0           # Effective gravity acceleration scale (mm/s^2)
    
    # Contact Angles
    theta_adv = np.radians(120)  # Advancing contact angle at bubble boundary
    theta_rec = np.radians(50)   # Receding contact angle at bubble boundary
    theta_p_deg = 65.0           # Particle-Interface contact angle (degrees)
    theta_p = np.radians(theta_p_deg)

    # Spatial domain setup (mm)
    x = np.linspace(-3.5 * R, 3.5 * R, 200)
    y = np.linspace(-4.0 * R, 4.0 * R, 200)
    X, Y = np.meshgrid(x, y)
    
    # Time discretization
    num_frames = 300
    dt = 0.01  # seconds
    
    y_bubble_start = -3.5 * R
    
    # Non-coaxial initial setup: particle released off-axis at x0 = 0.85 * R
    particle_pos = np.array([0.85 * R, -0.5 * R], dtype=float)
    particle_trajectory = [particle_pos.copy()]
    
    is_attached = False
    polar_angle = 0.0  # Polar angle relative to bubble center

    def stokes_bubble_velocity(px, py, y_b):
        """Hadamard-Rybczynski stream function velocity for an ascending gas bubble."""
        rel_y = py - y_b
        eps = 1e-4

        def get_psi_bubble(x_val, y_val):
            r_val = np.sqrt(x_val**2 + y_val**2)
            if r_val <= R:
                return -0.5 * U_rise * (x_val**2) * (1.0 - (r_val / R))
            else:
                return -0.5 * U_rise * (x_val**2) * (1.0 - (R / r_val))

        psi_y_plus = get_psi_bubble(px, rel_y + eps)
        psi_y_minus = get_psi_bubble(px, rel_y - eps)
        ux = (psi_y_plus - psi_y_minus) / (2 * eps)

        psi_x_plus = get_psi_bubble(px + eps, rel_y)
        psi_x_minus = get_psi_bubble(px - eps, rel_y)
        uy = -(psi_x_plus - psi_x_minus) / (2 * eps)

        return np.array([ux, uy])

    fig, ax = plt.subplots(figsize=(8, 8))

    def update(frame):
        nonlocal particle_pos, is_attached, polar_angle
        ax.clear()
        
        # Extended rise trajectory: y_b(t) = y_start + U_rise * t
        y_b = y_bubble_start + U_rise * (frame * dt)
        
        # Relative coordinates to rising bubble center
        rel_x = particle_pos[0]
        rel_y = particle_pos[1] - y_b
        r_current = np.sqrt(rel_x**2 + rel_y**2)

        # Attachment condition considering finite particle radius (R + r_p)
        attachment_radius = R + 0.1 * r_p
        if not is_attached and r_current <= attachment_radius:
            is_attached = True
            polar_angle = np.arctan2(rel_y, rel_x)

        # Physics Trajectory Integration
        if is_attached:
            # Gravity-driven tangential sliding along interface
            d_theta_dt = -(g_eff / (R + r_p)) * np.cos(polar_angle)
            polar_angle += d_theta_dt * dt
            
            # Position anchored to bubble surface with particle radius offset
            particle_pos[0] = (R + r_p) * np.cos(polar_angle)
            particle_pos[1] = y_b + (R + r_p) * np.sin(polar_angle)
        else:
            # Off-axis fluid advection
            u_fluid = stokes_bubble_velocity(particle_pos[0], particle_pos[1], y_b)
            particle_pos += u_fluid * dt

        particle_trajectory.append(particle_pos.copy())
        traj_arr = np.array(particle_trajectory)

        # Stream function grid centered on rising bubble
        Y_rel = Y - y_b
        r_grid = np.sqrt(X**2 + Y_rel**2)
        
        psi = np.zeros_like(X)
        mask_out = r_grid > R
        mask_in = r_grid <= R
        
        psi[mask_out] = -0.5 * U_rise * (X[mask_out]**2) * (1.0 - (R / r_grid[mask_out]))
        psi[mask_in] = -0.5 * U_rise * (X[mask_in]**2) * (1.0 - (r_grid[mask_in] / R))

        # 1. Background Stokes Streamlines
        levels = np.linspace(-3.0 * R**2 * U_rise, 3.0 * R**2 * U_rise, 35)
        ax.contour(X, Y, psi, levels=levels, cmap="Blues_r", alpha=0.5, linewidths=1.2)

        # 2. Rising Air Bubble (2 mm diameter)
        circle = plt.Circle((0, y_b), R, color="lightcyan", ec="deepskyblue", lw=2, alpha=0.7, zorder=3,
                            label=f"Rising Air Bubble ($D={D_bubble:.1f}\\,\\mathrm{{mm}}$)")
        ax.add_patch(circle)

        # 3. Dynamic Asymmetric Contact Line Boundaries
        x_c = 0.5 * R
        dy_rel = np.sqrt(max(0, R**2 - x_c**2))
        y_top, y_bot = y_b + dy_rel, y_b - dy_rel

        x_vec = np.linspace(-3.5 * R, 3.5 * R, 300)
        y_int = np.where(
            x_vec < -R, 0,
            np.where(
                x_vec > R, 0,
                y_top * np.exp(-((x_vec - x_c) / (0.8 * R))**2) + y_bot * np.exp(-((x_vec + x_c) / (0.8 * R))**2)
            )
        )
        ax.plot(x_vec, y_int, color="teal", lw=2.5, linestyle="--", zorder=4, label=r"Fluid Interface Boundary")

        # 4. Bubble Contact Line Tangent Vectors (\theta_A and \theta_R)
        alpha_top = np.arctan2(y_top - y_b, x_c)
        dir_top = alpha_top + (np.pi - theta_adv)
        ax.arrow(x_c, y_top, 0.6 * R * np.cos(dir_top), 0.6 * R * np.sin(dir_top),
                 head_width=0.08 * R, color="crimson", lw=2.2, zorder=6, label=r"Top: Advancing ($\theta_A = 120^\circ$)")

        alpha_bot = np.arctan2(y_bot - y_b, -x_c)
        dir_bot = alpha_bot - (np.pi - theta_rec)
        ax.arrow(-x_c, y_bot, -0.6 * R * np.cos(dir_bot), -0.6 * R * np.sin(dir_bot),
                 head_width=0.08 * R, color="darkgreen", lw=2.2, zorder=6, label=r"Bottom: Receding ($\theta_R = 50^\circ$)")

        ax.plot(x_c, y_top, "ro", ms=8, zorder=7)
        ax.plot(-x_c, y_bot, "go", ms=8, zorder=7)

        # 5. Non-Coaxial Particle Trajectory & Particle Patch (0.8 mm diameter)
        ax.plot(traj_arr[:, 0], traj_arr[:, 1], color="orange", lw=1.8, linestyle="-", zorder=8, label=r"Non-Coaxial Sliding Path")

        p_label = f"Particle ($d_p={D_particle:.1f}\\,\\mathrm{{mm}}$) - Attached ($\\theta_p={theta_p_deg:.0f}^\\circ$)" if is_attached else f"Particle ($d_p={D_particle:.1f}\\,\\mathrm{{mm}}$)"
        p_color = "red" if is_attached else "darkorange"

        # Draw physical particle circle
        particle_circle = plt.Circle((particle_pos[0], particle_pos[1]), r_p, color=p_color, ec="black", lw=1.2, zorder=9, label=p_label)
        ax.add_patch(particle_circle)

        # ---------------------------------------------------------------------
        # Dynamic Particle-Interface Contact Angle (\theta_p) Construction
        # ---------------------------------------------------------------------
        if is_attached:
            # Contact point at the bubble interface (three-phase contact line)
            contact_pt = np.array([R * np.cos(polar_angle), y_b + R * np.sin(polar_angle)])
            
            # Local interface tangent angle at the contact point
            tangent_angle = polar_angle + np.pi / 2.0
            
            # Surface tension / Interface tangent vector along liquid-gas boundary
            t_len = 0.5 * R
            ax.plot([contact_pt[0] - t_len * np.cos(tangent_angle), contact_pt[0] + t_len * np.cos(tangent_angle)],
                    [contact_pt[1] - t_len * np.sin(tangent_angle), contact_pt[1] + t_len * np.sin(tangent_angle)],
                    color="magenta", lw=1.5, linestyle="-.", zorder=10, label=r"Interface Tangent ($\gamma_{LG}$)")

            # Solid particle-liquid boundary tangent vector (rotated by \theta_p)
            p_tangent_angle = tangent_angle + theta_p
            ax.arrow(contact_pt[0], contact_pt[1], 0.4 * R * np.cos(p_tangent_angle), 0.4 * R * np.sin(p_tangent_angle),
                     head_width=0.06 * R, color="darkviolet", lw=2.0, zorder=11, label=rf"Particle Contact Vector ($\theta_p={theta_p_deg:.0f}^\circ$)")

            # Arc depicting the particle contact angle \theta_p
            start_deg = np.degrees(tangent_angle)
            end_deg = np.degrees(p_tangent_angle)
            arc_p = Arc((contact_pt[0], contact_pt[1]), 0.6 * R, 0.6 * R, angle=0,
                        theta1=min(start_deg, end_deg), theta2=max(start_deg, end_deg),
                        color="darkviolet", lw=2.0, zorder=12)
            ax.add_patch(arc_p)

            # Contact angle text label near the contact point
            label_offset_x = 0.25 * R * np.cos(tangent_angle + theta_p / 2.0)
            label_offset_y = 0.25 * R * np.sin(tangent_angle + theta_p / 2.0)
            ax.text(contact_pt[0] + label_offset_x, contact_pt[1] + label_offset_y,
                    rf"$\theta_p={theta_p_deg:.0f}^\circ$", color="darkviolet", fontsize=11, fontweight="bold", zorder=13)

            # Forces acting on attached particle
            d_theta_dt = -(g_eff / (R + r_p)) * np.cos(polar_angle)
            v_slide_x = -np.sin(polar_angle) * 0.4 * R * np.sign(d_theta_dt)
            v_slide_y = np.cos(polar_angle) * 0.4 * R * np.sign(d_theta_dt)
            ax.arrow(particle_pos[0], particle_pos[1], v_slide_x, v_slide_y,
                     head_width=0.08 * R, color="purple", lw=2.2, zorder=10, label=r"Tangential Velocity $u_\theta(g)$")

            ax.arrow(particle_pos[0], particle_pos[1], 0.0, -0.4 * R,
                     head_width=0.08 * R, color="brown", lw=2.0, linestyle=":", zorder=10, label=r"Gravity Force $\mathbf{F}_g$")

        # Plot formatting
        ax.set_aspect("equal")
        ax.set_xlim(-3.5 * R, 3.5 * R)
        ax.set_ylim(-4.0 * R, 4.0 * R)
        ax.set_xlabel(r"$x$ [mm]", fontsize=12)
        ax.set_ylabel(r"$y$ [mm]", fontsize=12)
        ax.set_title(f"2 mm Bubble & 0.8 mm Particle Advection & Attachment", fontsize=13)
        ax.legend(loc="lower right", framealpha=0.9, fontsize=8.0)
        ax.grid(True, linestyle=":", alpha=0.5)

    anim = FuncAnimation(fig, update, frames=num_frames, interval=40)

    # Save animation as GIF
    print("Saving physical bubble animation as GIF...")
    writer_gif = PillowWriter(fps=25)
    anim.save("stokes_physical_bubble_sliding.gif", writer=writer_gif)
    print("Saved 'stokes_physical_bubble_sliding.gif' successfully!")

    try:
        print("Saving video as MP4...")
        writer_mp4 = FFMpegWriter(fps=25, metadata=dict(artist='Matplotlib'), bitrate=1800)
        anim.save("stokes_physical_bubble_sliding.mp4", writer=writer_mp4)
        print("Saved 'stokes_physical_bubble_sliding.mp4' successfully!")
    except FileNotFoundError:
        print("FFmpeg not found. Skipping MP4 save (GIF generated).")

if __name__ == "__main__":
    animate_rising_bubble_physical()
