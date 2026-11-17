#!/usr/bin/env python3
"""
particle_trajectory.py
======================

Trajectory of a particle approaching a rising bubble, seen in the frame of
the bubble. Coordinates are scaled by the bubble radius r0.

Model
-----
Bubble    sphere of radius r0 rising at constant speed U_b. In the bubble
          frame the liquid comes from above with velocity -U_b e_y.

Liquid    analytic flow around a sphere
            potential : clean, mobile bubble surface (high Re_b)
            stokes    : contaminated, immobile surface (creeping flow)

Particle  Maxey-Riley equation without the Basset history term
            (rho_p + C_m rho_f) dv/dt = (1 + C_m) rho_f Du/Dt
                                      + (rho_p - rho_f) g
                                      + 3/4 rho_f C_D/d_p |u - v| (u - v)
          with Schiller-Naumann drag and added-mass coefficient C_m = 0.5.

Contact   the particle centre cannot come closer than r0 + r_p. On contact
          the inward normal velocity is removed and the particle slides
          along the bubble surface until the flow carries it away again.
          Optionally it attaches after an induction time t_ind.

The flow is axisymmetric about the y axis, so a particle that starts in the
x-y plane stays in it: the 2-D simulation in that plane is exact.

Usage
-----
    python particle_trajectory.py                       # -> GIF + snapshot PNG
    python particle_trajectory.py --x0 0.8 --dp 60e-6
    python particle_trajectory.py --flow stokes --streamlines
    python particle_trajectory.py --csv                 # + trajectory CSV
    python particle_trajectory.py --no-png              # GIF only
    python particle_trajectory.py -h                    # all options

Outputs: particle_trajectory.gif (animation of the whole run) and
particle_trajectory.png (snapshots), written next to where you run it.

Requires numpy and matplotlib (matplotlib ships with pillow for the GIF).
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
@dataclass
class Params:
    # bubble
    r0: float = 0.5e-3          # bubble radius [m]
    U_b: float = 0.135          # bubble rise velocity [m/s]
    flow: str = "potential"     # "potential" (mobile) | "stokes" (immobile)
    # particle
    d_p: float = 120e-6         # particle diameter [m]
    rho_p: float = 2650.0       # particle density [kg/m^3] (quartz)
    # liquid (water, 20 degC)
    rho_f: float = 998.0        # [kg/m^3]
    mu_f: float = 1.0e-3        # [Pa s]
    C_m: float = 0.5            # added-mass coefficient (sphere)
    g: float = 9.81             # [m/s^2]
    # initial particle position, in units of r0
    x0: float = 0.45
    y0: float = 2.4
    # time integration
    t_end: float = 0.040        # [s]
    dt: float = 1.0e-6          # [s]
    snapshots: tuple = (0.002, 0.005, 0.010)
    # attachment: induction time [s]; None -> particle only slides
    t_ind: float | None = None

    @property
    def r_p(self) -> float:
        return 0.5 * self.d_p


# --------------------------------------------------------------------------
# Liquid flow around the bubble (bubble frame, free stream = -U_b e_y)
# --------------------------------------------------------------------------
def fluid_velocity(x, y, p: Params):
    """Liquid velocity (ux, uy) at (x, y) [m]. Works on scalars and arrays."""
    R, U = p.r0, p.U_b
    r = np.sqrt(x * x + y * y)
    Udotx = -U * y                      # U_inf . x  with U_inf = (0, -U)

    if p.flow == "potential":
        # phi = U_inf . x (1 + R^3 / 2r^3)
        a = 1.0 + 0.5 * R**3 / r**3
        b = -1.5 * R**3 * Udotx / r**5
        ux = b * x
        uy = -U * a + b * y
    elif p.flow == "stokes":
        # Stokeslet + source dipole, no-slip on r = R
        a = 1.0 - 0.75 * R / r - 0.25 * R**3 / r**3
        b = -0.75 * R * Udotx / r**3 + 0.75 * R**3 * Udotx / r**5
        ux = b * x
        uy = -U * a + b * y
    else:
        raise ValueError(f"unknown flow model '{p.flow}'")
    return ux, uy


def fluid_acceleration(x, y, ux, uy, p: Params):
    """Material derivative Du/Dt = (u . grad) u of the steady flow."""
    h = 1e-5 * p.r0
    uxp, uyp = fluid_velocity(x + h, y, p)
    uxm, uym = fluid_velocity(x - h, y, p)
    dux_dx, duy_dx = (uxp - uxm) / (2 * h), (uyp - uym) / (2 * h)
    uxp, uyp = fluid_velocity(x, y + h, p)
    uxm, uym = fluid_velocity(x, y - h, p)
    dux_dy, duy_dy = (uxp - uxm) / (2 * h), (uyp - uym) / (2 * h)
    return ux * dux_dx + uy * dux_dy, ux * duy_dx + uy * duy_dy


# --------------------------------------------------------------------------
# Particle dynamics
# --------------------------------------------------------------------------
def drag_coefficient(Re: float) -> float:
    """Schiller-Naumann."""
    Re = max(Re, 1e-12)
    return 24.0 / Re * (1.0 + 0.15 * Re**0.687) if Re < 1000.0 else 0.44


def particle_acceleration(state: np.ndarray, p: Params) -> np.ndarray:
    """d/dt of state = [x, y, vx, vy]."""
    x, y, vx, vy = state
    ux, uy = fluid_velocity(x, y, p)
    wx, wy = ux - vx, uy - vy                       # slip velocity
    w = np.hypot(wx, wy)
    Re = p.rho_f * w * p.d_p / p.mu_f
    k = 0.75 * p.rho_f * drag_coefficient(Re) / p.d_p * w   # drag / volume / slip
    ax_f, ay_f = fluid_acceleration(x, y, ux, uy, p)

    m_eff = p.rho_p + p.C_m * p.rho_f
    ax = (k * wx + (1 + p.C_m) * p.rho_f * ax_f) / m_eff
    ay = (k * wy + (1 + p.C_m) * p.rho_f * ay_f
          - (p.rho_p - p.rho_f) * p.g) / m_eff
    return np.array([vx, vy, ax, ay])


def rk4_step(state: np.ndarray, dt: float, p: Params) -> np.ndarray:
    k1 = particle_acceleration(state, p)
    k2 = particle_acceleration(state + 0.5 * dt * k1, p)
    k3 = particle_acceleration(state + 0.5 * dt * k2, p)
    k4 = particle_acceleration(state + dt * k3, p)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def settling_velocity(p: Params) -> float:
    """Terminal settling velocity in still liquid (positive = downwards)."""
    drho = p.rho_p - p.rho_f
    vt = abs(drho) * p.g * p.d_p**2 / (18 * p.mu_f)          # Stokes guess
    for _ in range(200):
        Re = p.rho_f * vt * p.d_p / p.mu_f
        vt_new = np.sqrt(4 * p.g * p.d_p * abs(drho)
                         / (3 * drag_coefficient(Re) * p.rho_f))
        vt = 0.5 * (vt + vt_new)
    return float(np.sign(drho) * vt)


def polar_angle(x: float, y: float) -> float:
    """Angle from the bubble's top (front stagnation point) in degrees."""
    return float(np.degrees(np.arctan2(abs(x), y)))


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------
def simulate(p: Params) -> dict:
    R_c = p.r0 + p.r_p                   # centre distance at contact
    tol_contact = 1e-6 * p.r0
    tol_detach = 1e-2 * p.r0

    n = int(round(p.t_end / p.dt))
    T = np.linspace(0.0, n * p.dt, n + 1)
    S = np.empty((n + 1, 4))
    contact = np.zeros(n + 1, dtype=bool)

    x, y = p.x0 * p.r0, p.y0 * p.r0
    ux, uy = fluid_velocity(x, y, p)
    state = np.array([x, y, ux, uy - settling_velocity(p)])
    S[0] = state

    events = {"collision": None, "detachment": None, "attachment": None}
    in_contact, attached, t_contact = False, False, 0.0

    for i in range(n):
        if attached:                                 # rides with the bubble
            state = np.array([state[0], state[1], 0.0, 0.0])
        else:
            state = rk4_step(state, p.dt, p)
            r = np.hypot(state[0], state[1])
            if r < R_c:                              # enforce non-penetration
                nx, ny = state[0] / r, state[1] / r
                state[0], state[1] = nx * R_c, ny * R_c
                vn = state[2] * nx + state[3] * ny
                if vn < 0.0:                         # remove inward velocity
                    state[2] -= vn * nx
                    state[3] -= vn * ny
                r = R_c
            gap = r - R_c

            if gap < tol_contact:
                if not in_contact and events["collision"] is None:
                    events["collision"] = (T[i + 1], polar_angle(*state[:2]))
                in_contact = True
            elif in_contact and gap > tol_detach:
                in_contact = False
                if events["detachment"] is None:
                    events["detachment"] = (T[i + 1], polar_angle(*state[:2]))

            if in_contact:
                t_contact += p.dt
                if p.t_ind is not None and t_contact >= p.t_ind:
                    attached = True
                    events["attachment"] = (T[i + 1], polar_angle(*state[:2]))

        S[i + 1] = state
        contact[i + 1] = in_contact or attached

    return {"t": T, "x": S[:, 0], "y": S[:, 1], "vx": S[:, 2], "vy": S[:, 3],
            "contact": contact, "events": events, "t_contact": t_contact}


# --------------------------------------------------------------------------
# Plotting
# --------------------------------------------------------------------------
BUBBLE_FC, BUBBLE_EC = "#e8f4fc", "#3a9ad9"
PART_FC, PART_EC = "#3aa0e0", "#1b4f72"
TRAJ_C = "#f5b041"


def style_axes(ax, first: bool, lim: float = 3.0):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_facecolor("#fbfbfb")
    ax.set_xticks(np.arange(-lim, lim + 1))
    ax.set_yticks(np.arange(-lim, lim + 1))
    ax.grid(True, color="#e6e6e6", lw=0.6, ls=":")
    for s in ax.spines.values():
        s.set_color("#c8c8c8")
    ax.tick_params(colors="#666666", labelsize=9)
    ax.set_xlabel(r"$x/r_0$", color="#444444")
    if first:
        ax.set_ylabel(r"$y/r_0$", color="#444444")


def draw_streamlines(ax, p: Params, lim: float = 3.0):
    g = np.linspace(-lim, lim, 241)
    X, Y = np.meshgrid(g, g)
    with np.errstate(divide="ignore", invalid="ignore"):
        ux, uy = fluid_velocity(X * p.r0, Y * p.r0, p)
    inside = X**2 + Y**2 < 1.0
    ux, uy = np.where(inside, np.nan, ux), np.where(inside, np.nan, uy)
    ax.streamplot(X, Y, ux, uy, color="#d5dde3", linewidth=0.6,
                  density=1.2, arrowsize=0.6, zorder=1)


def draw_frame(ax, sim, k, p: Params, title: str, streamlines: bool):
    r0 = p.r0
    if streamlines:
        draw_streamlines(ax, p)
    ax.add_patch(Circle((0, 0), 1.0, fc=BUBBLE_FC, ec=BUBBLE_EC, lw=2, zorder=2))
    ax.plot(sim["x"][:k + 1] / r0, sim["y"][:k + 1] / r0,
            color=TRAJ_C, lw=1.6, zorder=3)
    rp_vis = max(p.r_p / r0, 0.07)               # keep tiny particles visible
    ax.add_patch(Circle((sim["x"][k] / r0, sim["y"][k] / r0), rp_vis,
                        fc=PART_FC, ec=PART_EC, lw=1.4, zorder=4))
    ax.set_title(title, fontweight="bold", fontsize=13, pad=12)


def snapshot_index(sim, t: float) -> int:
    return int(np.clip(np.searchsorted(sim["t"], t - 1e-12), 0, len(sim["t"]) - 1))


def plot_snapshots(sim, p: Params, fname: str, streamlines=False):
    m = len(p.snapshots)
    fig, axes = plt.subplots(1, m, figsize=(5.0 * m, 5.0), sharey=True)
    axes = np.atleast_1d(axes)
    for j, (ax, ts) in enumerate(zip(axes, p.snapshots)):
        style_axes(ax, first=(j == 0))
        draw_frame(ax, sim, snapshot_index(sim, ts), p, f"T = {ts:.3f}s", streamlines)
    fig.tight_layout()
    fig.savefig(fname, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {fname}")


def animate(sim, p: Params, fname: str, streamlines=False, frames=150, fps=30,
            hold=1.5):
    """Single-panel GIF of the whole run; the last frame is held for `hold` s."""
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    idx = np.linspace(0, len(sim["t"]) - 1, frames).astype(int)
    idx = np.concatenate([idx, np.full(int(hold * fps), idx[-1])])

    def update(f):
        ax.clear()
        style_axes(ax, first=True)
        k = idx[f]
        draw_frame(ax, sim, k, p, f"T = {sim['t'][k]:.4f}s", streamlines)
        fig.tight_layout()

    anim = FuncAnimation(fig, update, frames=len(idx))
    anim.save(fname, writer=PillowWriter(fps=fps), dpi=110)
    plt.close(fig)
    print(f"saved {fname}")


def write_csv(sim, p: Params, fname: str):
    with open(fname, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t_s", "x_m", "y_m", "x_r0", "y_r0", "vx_m_s", "vy_m_s", "contact"])
        for i in range(len(sim["t"])):
            w.writerow([f"{sim['t'][i]:.7e}", f"{sim['x'][i]:.7e}", f"{sim['y'][i]:.7e}",
                        f"{sim['x'][i] / p.r0:.6f}", f"{sim['y'][i] / p.r0:.6f}",
                        f"{sim['vx'][i]:.7e}", f"{sim['vy'][i]:.7e}", int(sim["contact"][i])])
    print(f"saved {fname}")


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
def print_summary(sim, p: Params):
    tau_p = p.rho_p * p.d_p**2 / (18 * p.mu_f)
    Re_b = p.rho_f * p.U_b * 2 * p.r0 / p.mu_f
    print(f"Bubble   : d_b = {2e3 * p.r0:.2f} mm, U_b = {p.U_b:.3f} m/s, "
          f"Re_b = {Re_b:.0f}, flow = {p.flow}")
    print(f"Particle : d_p = {1e6 * p.d_p:.0f} um, rho_p = {p.rho_p:.0f} kg/m3, "
          f"v_settle = {1e3 * settling_velocity(p):.2f} mm/s, "
          f"St = tau_p U_b / r0 = {tau_p * p.U_b / p.r0:.3f}")
    ev = sim["events"]
    if ev["collision"] is None:
        print("Result   : no collision (particle passes the bubble)")
        return
    t, th = ev["collision"]
    print(f"Collision: t = {t * 1e3:.3f} ms at theta = {th:.1f} deg from the top")
    if ev["attachment"]:
        t, th = ev["attachment"]
        print(f"Attached : t = {t * 1e3:.3f} ms at theta = {th:.1f} deg")
    elif ev["detachment"]:
        t, th = ev["detachment"]
        print(f"Detached : t = {t * 1e3:.3f} ms at theta = {th:.1f} deg "
              f"(sliding time {sim['t_contact'] * 1e3:.3f} ms)")
    else:
        th = polar_angle(sim["x"][-1], sim["y"][-1])
        print(f"Sliding  : still on the surface at t_end, theta = {th:.1f} deg "
              f"(sliding time {sim['t_contact'] * 1e3:.3f} ms)")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main():
    d = Params()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r0", type=float, default=d.r0, help="bubble radius [m]")
    ap.add_argument("--ub", type=float, default=d.U_b, help="bubble rise velocity [m/s]")
    ap.add_argument("--flow", choices=["potential", "stokes"], default=d.flow)
    ap.add_argument("--dp", type=float, default=d.d_p, help="particle diameter [m]")
    ap.add_argument("--rhop", type=float, default=d.rho_p, help="particle density [kg/m3]")
    ap.add_argument("--rhof", type=float, default=d.rho_f, help="liquid density [kg/m3]")
    ap.add_argument("--mu", type=float, default=d.mu_f, help="liquid viscosity [Pa s]")
    ap.add_argument("--x0", type=float, default=d.x0, help="start x / r0")
    ap.add_argument("--y0", type=float, default=d.y0, help="start y / r0")
    ap.add_argument("--t-end", type=float, default=d.t_end, help="end time [s]")
    ap.add_argument("--dt", type=float, default=d.dt, help="time step [s]")
    ap.add_argument("--snapshots", type=float, nargs="+", default=list(d.snapshots),
                    help="snapshot times [s]")
    ap.add_argument("--t-ind", type=float, default=None,
                    help="induction time [s]: particle attaches after this contact time")
    ap.add_argument("--streamlines", action="store_true", help="draw liquid streamlines")
    ap.add_argument("--no-png", action="store_true", help="skip the snapshot PNG")
    ap.add_argument("--fps", type=int, default=30, help="GIF frames per second")
    ap.add_argument("--frames", type=int, default=150, help="number of GIF frames")
    ap.add_argument("--csv", action="store_true", help="also write the trajectory as CSV")
    ap.add_argument("--out", default="particle_trajectory", help="output file prefix")
    a = ap.parse_args()

    snaps = tuple(sorted(a.snapshots))
    p = Params(r0=a.r0, U_b=a.ub, flow=a.flow, d_p=a.dp, rho_p=a.rhop, rho_f=a.rhof,
               mu_f=a.mu, x0=a.x0, y0=a.y0, t_end=max(a.t_end, snaps[-1]), dt=a.dt,
               snapshots=snaps, t_ind=a.t_ind)

    sim = simulate(p)
    print_summary(sim, p)
    animate(sim, p, f"{a.out}.gif", streamlines=a.streamlines,
            frames=a.frames, fps=a.fps)
    if not a.no_png:
        plot_snapshots(sim, p, f"{a.out}.png", streamlines=a.streamlines)
    if a.csv:
        write_csv(sim, p, f"{a.out}.csv")


if __name__ == "__main__":
    main()
