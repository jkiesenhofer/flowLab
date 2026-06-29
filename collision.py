import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Simulation & Physical Parameters ---
dt = 0.001          # Time step (s)
t_max = 2.0         # Max simulation time (s)
time_steps = np.arange(0, t_max, dt)
N_steps = len(time_steps)

# Physical Constants
g = 9.81            # Gravity (m/s^2)
rho_w = 1000.0      # Density of water (kg/m^3)
mu_w = 1e-3         # Dynamic viscosity (Pa*s)
gamma = 0.072       # Surface tension of water (N/m)

# Initial Single Bubble Parameters
d_b = 1.0e-3        # 1 mm nominal diameter
r_0 = d_b / 2.0
bubble_pos = np.array([0.0, 0.0])  

# Hydrophobic Low-Inertia Particle
r_p = 0.05e-3       
rho_p = 1100.0      
m_p = rho_p * (4.0/3.0) * np.pi * (r_p**3)

# Start above the bubble, perfectly aligned to initiate center dewetting
particle_pos = np.array([0.0, 1.2e-3])  
particle_vel = np.array([0.0, -0.12])    

# State Machine Flags
is_attached = False
has_split = False
neck_width = r_0 * 2.0
split_frame = 0
contact_time = 0.0

# Daughter Bubbles properties
b1_pos, b2_pos = np.zeros(2), np.zeros(2)
b_daughter_radius = r_0 / np.sqrt(2)

# --- Plot Setup ---
fig, ax = plt.subplots(figsize=(7, 7), facecolor='#ffffff')
ax.set_facecolor('#fdfdfd')
view_size = 1.6e-3  
ax.set_xlim(-view_size, view_size)
ax.set_ylim(-view_size, view_size)
ax.grid(True, color='#e5e5e5', alpha=0.7, linestyle='--')

# Initialize Graphical Objects Handles
theta = np.linspace(0, 2*np.pi, 200)
h_bubble_main = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.5, zorder=2)[0]
h_bubble1 = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.0, zorder=2, visible=False)[0]
h_bubble2 = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.0, zorder=2, visible=False)[0]

h_particle = ax.scatter([], [], s=60, color='#10b981', edgecolors='#064e3b', zorder=5, label='Hydrophobic Particle')
h_trajectory, = ax.plot([], [], color='#f59e0b', linestyle='-', linewidth=1.5, alpha=0.6)

ax.tick_params(colors='#333333', labelsize=9)
ax.set_title("Hydrophobic Dewetting & Capillary Bridge Breakup", color='#111111', fontsize=11, fontweight='bold')
ax.legend(loc='upper right')

path_x, path_y = [particle_pos[0]], [particle_pos[1]]

def update(frame):
    global particle_pos, particle_vel, is_attached, has_split, neck_width, b1_pos, b2_pos, split_frame, contact_time
    
    t = frame * dt

    # --- STAGE 1: APPROACH AND DEWETTING PINCH ---
    if not has_split:
        dx = particle_pos[0] - bubble_pos[0]
        dy = particle_pos[1] - bubble_pos[1]
        dist = np.sqrt(dx**2 + dy**2)

        if not is_attached:
            # Low-inertia streamlined approach
            if dist > r_0:
                u_fluid_x = -(-0.12) * (3/2) * (r_0**3) * (dx * dy) / (dist**5)
                u_fluid_y = (-0.12) * (1 - 0.5 * (r_0/dist)**3 + 1.5 * (r_0**3) * (dy**2) / (dist**5))
            else:
                u_fluid_x, u_fluid_y = 0.0, 0.0

            particle_vel[0] = u_fluid_x
            particle_vel[1] = u_fluid_y
            particle_pos += particle_vel * dt

            # Direct contact makes the particle jump to the interface
            if dist <= (r_0 + r_p):
                is_attached = True
                contact_time = t
        else:
            # Hydrophobic Dewetting Pull: 
            # The interface rapidly retracts, pulling the particle into the core center
            t_contact = t - contact_time
            
            # Pull particle downward into the waist due to dewetting suction
            particle_pos[1] = r_0 - (r_0 * (t_contact * 2.5))
            
            # The capillary neck narrows exponentially due to the rupture of the thin water film
            neck_width = max(0.0, (2.0 * r_0) * np.exp(-4.5 * t_contact))

            # Critical instability threshold: Capillary bridge snaps!
            if neck_width <= 0.04 * r_0 or particle_pos[1] <= -r_0 * 0.4:
                has_split = True
                split_frame = frame
                # Snapping splits the bubble left-and-right as the film breaks vertically
                b1_pos = np.array([-r_0 * 0.6, 0.0])
                b2_pos = np.array([ r_0 * 0.6, 0.0])
                h_bubble_main.set_visible(False)
                h_bubble1.set_visible(True)
                h_bubble2.set_visible(True)

        path_x.append(particle_pos[0])
        path_y.append(particle_pos[1])

        # Symmetrically deform the bubble to show hydrophobic indentation
        xb, yb = [], []
        for t_val in theta:
            x_circ = r_0 * np.cos(t_val)
            y_circ = r_0 * np.sin(t_val)
            
            if is_attached:
                t_contact = t - contact_time
                # Localized hourglass warping around the apex where dewetting forces act
                if y_circ > particle_pos[1]:
                    indent = (r_0 - particle_pos[1]) * np.exp(-abs(x_circ)/(0.4 * r_0))
                    y_circ -= indent * 0.85
                
                # Squeeze the waist laterally as fluid transfers away from the contact line
                pinch_factor = neck_width / (2.0 * r_0)
                if abs(y_circ) < r_0 * 0.6:
                    weight = np.cos(y_circ / (r_0 * 0.6) * np.pi / 2.0)
                    x_circ *= (1.0 - weight * (1.0 - pinch_factor))
                
            xb.append(x_circ)
            yb.append(y_circ)
            
        h_bubble_main.set_xy(np.column_stack((xb, yb)))

    # --- STAGE 2: POST-BREAKUP RECOIL ---
    else:
        t_post = (frame - split_frame) * dt
        
        # Symmetrical outward recoil driven by surface tension minimization
        b1_pos[0] -= 0.25 * np.exp(-12.0 * t_post) * dt + 0.01 * dt
        b2_pos[0] += 0.25 * np.exp(-12.0 * t_post) * dt + 0.01 * dt
        
        # Both daughter bubbles float upward together
        b1_pos[1] += 0.04 * dt
        b2_pos[1] += 0.04 * dt

        # The highly hydrophobic particle remains stabilized inside the snapped film center
        particle_pos[1] -= 0.05 * dt
        path_x.append(particle_pos[0])
        path_y.append(particle_pos[1])

        # Dynamic cross-section relaxation from capsule profile back to circles
        E_relax = max(0.65, 1.0 - 0.35 * np.exp(-8.0 * t_post))
        
        xb1 = b1_pos[0] + (b_daughter_radius / np.sqrt(E_relax)) * np.cos(theta)
        yb1 = b1_pos[1] + (b_daughter_radius * np.sqrt(E_relax)) * np.sin(theta)
        h_bubble1.set_xy(np.column_stack((xb1, yb1)))
        
        xb2 = b2_pos[0] + (b_daughter_radius * np.sqrt(E_relax)) * np.cos(theta)
        yb2 = b2_pos[1] + (b_daughter_radius / np.sqrt(E_relax)) * np.sin(theta)
        h_bubble2.set_xy(np.column_stack((xb2, yb2)))
        
    h_particle.set_offsets([particle_pos[0], particle_pos[1]])
    h_trajectory.set_data(path_x, path_y)
    
    return h_bubble_main, h_bubble1, h_bubble2, h_particle, h_trajectory

anim = animation.FuncAnimation(fig, update, frames=N_steps, interval=12, blit=False, repeat=False)
plt.show()
