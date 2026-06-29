import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Simulation & Physical Parameters ---
dt = 0.001          # Time step (s)
t_max = 2.2         # Max simulation time (s)
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
r_p = 0.045e-3       
rho_p = 1150.0      
m_p = rho_p * (4.0/3.0) * np.pi * (r_p**3)

# Start above and shifted right to hit the upper-right shoulder asymmetrically
particle_pos = np.array([0.22e-3, 1.2e-3])  
particle_vel = np.array([0.0, -0.12])    

# State Machine Flags
is_attached = False
has_split = False
pinch_depth = 0.0
split_frame = 0
contact_time = 0.0

# Unequal Daughter Bubbles (Asymmetric volume split: 70% vs 30%)
b1_pos, b2_pos = np.zeros(2), np.zeros(2)
r_daughter_large = r_0 * (0.7)**(1/2) 
r_daughter_small = r_0 * (0.3)**(1/2) 

# --- Plot Setup ---
fig, ax = plt.subplots(figsize=(7, 7), facecolor='#ffffff')
ax.set_facecolor('#fdfdfd')
view_size = 1.6e-3  
ax.set_xlim(-view_size, view_size)
ax.set_ylim(-view_size, view_size)
ax.grid(True, color='#e5e5e5', alpha=0.7, linestyle='--')

# Initialize Graphical Objects Handles
theta = np.linspace(0, 2*np.pi, 250)
h_bubble_main = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.5, zorder=2)[0]
h_bubble1 = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.0, zorder=2, visible=False)[0]
h_bubble2 = ax.fill([], [], color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2.0, zorder=2, visible=False)[0]

h_particle = ax.scatter([], [], s=55, color='#10b981', edgecolors='#064e3b', zorder=5, label='Hydrophobic Particle')
h_trajectory, = ax.plot([], [], color='#f59e0b', linestyle='-', linewidth=1.5, alpha=0.6)

ax.tick_params(colors='#333333', labelsize=9)
ax.set_title("Asymmetric Hydrophobic Dewetting & Off-Center Pinch-Off", color='#111111', fontsize=11, fontweight='bold')
ax.legend(loc='upper right')

path_x, path_y = [particle_pos[0]], [particle_pos[1]]

def update(frame):
    global particle_pos, particle_vel, is_attached, has_split, pinch_depth, b1_pos, b2_pos, split_frame, contact_time
    
    t = frame * dt

    # --- STAGE 1: ASYMMETRIC APPROACH AND DEWETTING ---
    if not has_split:
        dx = particle_pos[0] - bubble_pos[0]
        dy = particle_pos[1] - bubble_pos[1]
        dist = np.sqrt(dx**2 + dy**2)

        if not is_attached:
            if dist > r_0:
                u_fluid_x = -(-0.12) * (3/2) * (r_0**3) * (dx * dy) / (dist**5)
                u_fluid_y = (-0.12) * (1 - 0.5 * (r_0/dist)**3 + 1.5 * (r_0**3) * (dy**2) / (dist**5))
            else:
                u_fluid_x, u_fluid_y = 0.0, 0.0

            particle_vel[0] = u_fluid_x
            particle_vel[1] = u_fluid_y
            particle_pos += particle_vel * dt

            if dist <= (r_0 + r_p):
                is_attached = True
                contact_time = t
        else:
            t_contact = t - contact_time
            pinch_depth = min(r_0 * 0.95, r_0 * (t_contact * 3.5))
            
            particle_pos[0] = r_0 * np.cos(np.pi/4) - pinch_depth * 0.6
            particle_pos[1] = r_0 * np.sin(np.pi/4) - pinch_depth * 0.7

            if pinch_depth >= r_0 * 0.85:
                has_split = True
                split_frame = frame
                b1_pos = np.array([-r_0 * 0.3,  r_0 * 0.1]) 
                b2_pos = np.array([ r_0 * 0.8,  r_0 * 0.5]) 
                h_bubble_main.set_visible(False)
                h_bubble1.set_visible(True)
                h_bubble2.set_visible(True)

        path_x.append(particle_pos[0])
        path_y.append(particle_pos[1])

        xb, yb = [], []
        for t_val in theta:
            x_circ = r_0 * np.cos(t_val)
            y_circ = r_0 * np.sin(t_val)
            
            if is_attached:
                angular_distance = np.abs(t_val - np.pi/4)
                if angular_distance > np.pi: 
                    angular_distance = 2*np.pi - angular_distance
                    
                if angular_distance < np.pi/3:
                    weight = np.cos(angular_distance / (np.pi/3) * np.pi / 2.0)
                    x_circ -= weight * pinch_depth * 0.55
                    y_circ -= weight * pinch_depth * 0.65
                
                if t_val > np.pi and t_val < 1.5*np.pi:
                    y_circ -= (pinch_depth * 0.2)
                    
            xb.append(x_circ)
            yb.append(y_circ)
            
        h_bubble_main.set_xy(np.column_stack((xb, yb)))

    # --- STAGE 2: UNEQUAL DAUGHTER RECOIL ---
    else:
        t_post = (frame - split_frame) * dt
        
        b1_pos[0] -= 0.12 * np.exp(-10.0 * t_post) * dt + 0.005 * dt 
        b2_pos[0] += 0.45 * np.exp(-14.0 * t_post) * dt + 0.02 * dt  
        
        b1_pos[1] += 0.05 * dt
        b2_pos[1] += 0.07 * dt 

        particle_pos[0] = b2_pos[0] - r_daughter_small * 0.5
        particle_pos[1] = b2_pos[1] + r_daughter_small * 0.5
        path_x.append(particle_pos[0])
        path_y.append(particle_pos[1])

        E1 = max(0.75, 1.0 - 0.25 * np.exp(-7.0 * t_post))
        E2 = max(0.50, 1.0 - 0.50 * np.exp(-12.0 * t_post)) 
        
        xb1 = b1_pos[0] + (r_daughter_large / np.sqrt(E1)) * np.cos(theta)
        yb1 = b1_pos[1] + (r_daughter_large * np.sqrt(E1)) * np.sin(theta)
        h_bubble1.set_xy(np.column_stack((xb1, yb1)))
        
        xb2 = b2_pos[0] + (r_daughter_small / np.sqrt(E2)) * np.cos(theta)
        yb2 = b2_pos[1] + (r_daughter_small * np.sqrt(E2)) * np.sin(theta)
        h_bubble2.set_xy(np.column_stack((xb2, yb2)))
        
    h_particle.set_offsets([particle_pos[0], particle_pos[1]])
    h_trajectory.set_data(path_x, path_y)
    
    return h_bubble_main, h_bubble1, h_bubble2, h_particle, h_trajectory

# --- Animation Generation Framework ---
anim = animation.FuncAnimation(fig, update, frames=N_steps, interval=12, blit=False, repeat=False)

# =====================================================================
# SAVING PIPELINE CODE: Compiling into an MP4 file
# =====================================================================
print("Compiling and saving the video file... Please wait.")
# Use FFMpegWriter with matching capital letters
writer = animation.FFMpegWriter(fps=60, metadata=dict(artist='Me'), bitrate=2000)
anim.save("asymmetric_bubble_split.mp4", writer=writer)
print("Saved successfully as 'asymmetric_bubble_split.mp4'!")

plt.show()
