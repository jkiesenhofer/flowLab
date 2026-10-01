import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

# Configure Matplotlib fonts
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "cm"
})

def animate_rising_bubble_non_coaxial_sliding():
    # Spatial domain setup
    x = np.linspace(-3.5, 3.5, 200)
    y = np.linspace(-4.0, 4.0, 200)
    X, Y = np.meshgrid(x, y)
    
    R = 1.0  # Bubble radius
    U_rise = 0.8  # Steady upward rise velocity of the air bubble
    g_eff = 1.2   # Effective gravity parameter pulling particle downward
    
    theta_adv = np.radians(120)  # Advancing contact angle
    theta_rec = np.radians(50)   # Receding contact angle
    
    # Extended time domain
    num_frames = 300
    dt = 0.05

    # Bubble starts near the bottom domain (y = -3.5)
    y_bubble_start = -3.5
    
    # Non-coaxial initial setup (particle released off-axis at x0 = -0.85 R)
    particle_pos = np.array([0.85, -0.5], dtype=float)
    
    particle_trajectory = [particle_pos.copy()]
    is_attached = False
    polar_angle = 0.0  # Polar angle on bubble interface

    def stokes_bubble_velocity(px, py, y_b):
        """Hadamard-Rybczynski stream function velocity for an ascending gas bubble."""
        rel_y = py - y_b
        r = np.sqrt(px**2 + rel_y**2)
        eps = 1e-5

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

        # 1. Non-Coaxial Interface Attachment Condition
        if not is_attached and r_current <= 1.03 * R:
            is_attached = True
            polar_angle = np.arctan2(rel_y, rel_x)

        # 2. Physics Trajectory Integration
        if is_attached:
            # Gravity-driven tangential sliding along interface
            d_theta_dt = -(g_eff / R) * np.cos(polar_angle)
            polar_angle += d_theta_dt * dt
            
            # Position anchored to bubble surface r = R
            particle_pos[0] = R * np.cos(polar_angle)
            particle_pos[1] = y_b + R * np.sin(polar_angle)
        else:
            # Off-axis advection carried by curved Stokes fluid streamlines
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
        levels = np.linspace(-3.0, 3.0, 35)
        ax.contour(X, Y, psi, levels=levels, cmap="Blues_r", alpha=0.5, linewidths=1.2)

        # 2. Rising Air Bubble
        circle = plt.Circle((0, y_b), R, color="lightcyan", ec="deepskyblue", lw=2, alpha=0.7, zorder=3, label=r"Rising Air Bubble ($R=1$)")
        ax.add_patch(circle)

        # 3. Dynamic Asymmetric Contact Line Boundaries
        x_c = 0.5 * R
        dy_rel = np.sqrt(R**2 - x_c**2)
        y_top, y_bot = y_b + dy_rel, y_b - dy_rel

        # Fluid Interface Boundary Line
        x_vec = np.linspace(-3.5, 3.5, 300)
        y_int = np.where(x_vec < -R, 0, np.where(x_vec > R, 0, y_top * np.exp(-((x_vec - x_c)/0.8)**2) + y_bot * np.exp(-((x_vec + x_c)/0.8)**2)))
        ax.plot(x_vec, y_int, color="teal", lw=2.5, linestyle="--", zorder=4, label=r"Fluid Interface Boundary")

        # 4. Tangent Vectors
        alpha_top = np.arctan2(y_top - y_b, x_c)
        dir_top = alpha_top + (np.pi - theta_adv)
        ax.arrow(x_c, y_top, 0.6 * np.cos(dir_top), 0.6 * np.sin(dir_top), head_width=0.08, color="crimson", lw=2.2, zorder=6, label=r"Top: Advancing ($\theta_A = 120^\circ$)")

        alpha_bot = np.arctan2(y_bot - y_b, -x_c)
        dir_bot = alpha_bot - (np.pi - theta_rec)
        ax.arrow(-x_c, y_bot, -0.6 * np.cos(dir_bot), -0.6 * np.sin(dir_bot), head_width=0.08, color="darkgreen", lw=2.2, zorder=6, label=r"Bottom: Receding ($\theta_R = 50^\circ$)")

        ax.plot(x_c, y_top, "ro", ms=8, zorder=7)
        ax.plot(-x_c, y_bot, "go", ms=8, zorder=7)

        # 5. Non-Coaxial Particle Trajectory & Gravity Vector
        ax.plot(traj_arr[:, 0], traj_arr[:, 1], color="orange", lw=1.8, linestyle="-", zorder=8, label=r"Non-Coaxial Sliding Path")
        
        p_label = r"Sliding under Gravity" if is_attached else r"Non-Coaxial Particle ($x_0 = -0.85 R$)"
        p_color = "red" if is_attached else "darkorange"
        
        ax.plot(particle_pos[0], particle_pos[1], "o", color=p_color, ms=10, mec="black", zorder=9, label=p_label)

        if is_attached:
            d_theta_dt = -(g_eff / R) * np.cos(polar_angle)
            v_slide_x = -np.sin(polar_angle) * 0.4 * np.sign(d_theta_dt)
            v_slide_y =  np.cos(polar_angle) * 0.4 * np.sign(d_theta_dt)
            ax.arrow(particle_pos[0], particle_pos[1], v_slide_x, v_slide_y,
                     head_width=0.08, color="purple", lw=2.5, zorder=10, label=r"Tangential Gravity $u_\theta(g)$")

            ax.arrow(particle_pos[0], particle_pos[1], 0.0, -0.4,
                     head_width=0.08, color="brown", lw=2.0, linestyle=":", zorder=10, label=r"Gravity Force $\mathbf{F}_g$")

        # Plot formatting
        ax.set_aspect("equal")
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-4.0, 4.0)
        ax.set_xlabel(r"$x / R$", fontsize=12)
        ax.set_ylabel(r"$y / R$", fontsize=12)
        ax.set_title("Non-Coaxial Particle Advection & Gravity Sliding on Air Bubble", fontsize=13)
        ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.5)

    anim = FuncAnimation(fig, update, frames=num_frames, interval=40)

    # Save animation as GIF
    print("Saving non-coaxial animation as GIF...")
    writer_gif = PillowWriter(fps=25)
    anim.save("stokes_non_coaxial_gravity_sliding.gif", writer=writer_gif)
    print("Saved 'stokes_non_coaxial_gravity_sliding.gif' successfully!")

    try:
        print("Saving video as MP4...")
        writer_mp4 = FFMpegWriter(fps=25, metadata=dict(artist='Matplotlib'), bitrate=1800)
        anim.save("stokes_non_coaxial_gravity_sliding.mp4", writer=writer_mp4)
        print("Saved 'stokes_non_coaxial_gravity_sliding.mp4' successfully!")
    except FileNotFoundError:
        print("FFmpeg not found. Skipping MP4 save (GIF generated).")

if __name__ == "__main__":
    animate_rising_bubble_non_coaxial_sliding()
