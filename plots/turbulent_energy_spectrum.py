"""
Turbulent Energy Spectrum from Velocity Field Video
====================================================
Reads a video of a bubbly/particle flow (e.g. bubbleVectors2.mp4),
extracts velocity fields via optical flow (Farneback), computes the
2-D turbulent kinetic energy spectrum E(k), and plots it with two
reference slopes: −5/3 (Kolmogorov inertial range) and −3 (enstrophy
cascade / large-scale dissipation).

Dependencies
------------
    pip install opencv-python numpy matplotlib scipy

Usage
-----
    python turbulent_energy_spectrum.py --video bubbleVectors2.mp4
    python turbulent_energy_spectrum.py --video bubbleVectors2.mp4 --frames 60 --output spectrum.png
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.ndimage import uniform_filter1d


# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Turbulent energy spectrum from flow video")
    p.add_argument("--video",   required=True, help="Path to the flow video file")
    p.add_argument("--frames",  type=int, default=None,
                   help="Maximum number of frame pairs to average (default: all)")
    p.add_argument("--output",  default="turbulent_spectrum.png",
                   help="Output image filename (default: turbulent_spectrum.png)")
    p.add_argument("--smooth",  type=int, default=5,
                   help="Uniform filter width for spectrum smoothing (default: 5)")
    p.add_argument("--scale",   type=float, default=1.0,
                   help="Physical length scale per pixel (arbitrary units, default: 1.0)")
    return p.parse_args()


# ── OPTICAL FLOW ──────────────────────────────────────────────────────────────

def extract_velocity_fields(video_path: str, max_pairs: int | None):
    """
    Use Farneback dense optical flow to extract (u, v) velocity fields
    from consecutive frame pairs. Returns the time-averaged 2-D TKE field.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        sys.exit(f"[ERROR] Cannot open video: {video_path}")

    ok, frame = cap.read()
    if not ok:
        sys.exit("[ERROR] Cannot read first frame.")

    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    H, W = prev_gray.shape

    # Accumulators for time-averaged spectrum
    E_sum = np.zeros((H, W), dtype=np.float64)
    count = 0

    farneback_params = dict(
        pyr_scale=0.5, levels=5, winsize=21,
        iterations=3, poly_n=7, poly_sigma=1.5, flags=0
    )

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, **farneback_params)

        u, v = flow[..., 0], flow[..., 1]
        E_sum += 0.5 * (u**2 + v**2)          # local TKE contribution

        prev_gray = gray
        count += 1
        if max_pairs and count >= max_pairs:
            break
        if count % 20 == 0:
            print(f"  processed {count} frame pairs …")

    cap.release()
    if count == 0:
        sys.exit("[ERROR] No frame pairs could be processed.")
    print(f"[INFO] Averaged over {count} frame pairs.")
    return E_sum / count, (H, W)


# ── ENERGY SPECTRUM ───────────────────────────────────────────────────────────

def compute_spectrum(tke_field: np.ndarray, pixel_scale: float):
    """
    Compute the 1-D radially-averaged turbulent kinetic energy spectrum E(k).

    Returns
    -------
    k   : wavenumber array (1 / length units)
    Ek  : E(k) — energy per unit wavenumber
    """
    H, W = tke_field.shape

    # Apply a 2-D Hann window to reduce spectral leakage
    win_r = np.hanning(H)[:, None]
    win_c = np.hanning(W)[None, :]
    window = win_r * win_c
    window /= window.mean()                    # preserve mean energy

    # 2-D FFT of the windowed TKE field
    F = np.fft.fft2(tke_field * window)
    F = np.fft.fftshift(F)

    power = (np.abs(F) ** 2) / (H * W)        # power spectral density

    # Radial wavenumber grid
    kx = np.fft.fftshift(np.fft.fftfreq(W, d=pixel_scale))
    ky = np.fft.fftshift(np.fft.fftfreq(H, d=pixel_scale))
    KX, KY = np.meshgrid(kx, ky)
    K = np.sqrt(KX**2 + KY**2)

    # Bin into annular shells (radial average)
    k_max   = min(kx.max(), ky.max())
    k_min   = max(kx[kx > 0].min(), ky[ky > 0].min())
    n_bins  = min(H, W) // 2
    k_edges = np.linspace(k_min, k_max, n_bins + 1)
    k_bins  = 0.5 * (k_edges[:-1] + k_edges[1:])

    Ek = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (K >= k_edges[i]) & (K < k_edges[i + 1])
        if mask.any():
            # Multiply by 2πk to convert 2-D PSD → 1-D E(k)
            Ek[i] = power[mask].mean() * 2 * np.pi * k_bins[i]

    return k_bins, Ek


# ── PLOTTING ──────────────────────────────────────────────────────────────────

def plot_spectrum(k, Ek, smooth_width: int, output: str):
    """
    Plot E(k) on log–log axes with −5/3 and −3 reference slopes.
    """
    # Remove zeros / NaNs
    valid = (Ek > 0) & np.isfinite(Ek)
    k, Ek = k[valid], Ek[valid]

    if len(k) < 10:
        sys.exit("[ERROR] Too few valid spectral points to plot. "
                 "Try a longer video or fewer frames.")

    # Smooth spectrum
    Ek_smooth = uniform_filter1d(Ek, size=smooth_width)

    # ── Reference slopes ────────────────────────────────────────────────────
    # Place slope guides in the middle third of the wavenumber range
    k_lo, k_hi = k[len(k)//4], k[3*len(k)//4]
    k_ref = np.array([k_lo, k_hi])

    # Anchor each slope at the smoothed spectrum's midpoint
    k_mid   = np.sqrt(k_lo * k_hi)
    idx_mid = np.argmin(np.abs(k - k_mid))
    E_mid   = Ek_smooth[idx_mid]

    slope_53 = E_mid * (k_ref / k_mid) ** (-5/3)
    slope_3  = E_mid * (k_ref / k_mid) ** (-3)

    # ── Figure style ────────────────────────────────────────────────────────
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # Raw spectrum (faint)
    ax.loglog(k, Ek, color="#4a6fa5", alpha=0.35, lw=0.9, label="E(k) raw")

    # Smoothed spectrum
    ax.loglog(k, Ek_smooth, color="#7ec8e3", lw=2.2, label="E(k) smoothed")

    # Slope guides
    ax.loglog(k_ref, slope_53, color="#f4a261", lw=2, ls="--",
              label=r"$k^{-5/3}$ (Kolmogorov inertial)")
    ax.loglog(k_ref, slope_3,  color="#e76f51", lw=2, ls=":",
              label=r"$k^{-3}$ (enstrophy cascade / large-scale)")

    # Slope annotation arrows
    for k_ann, slope, txt, dy in [
        (k_ref[1] * 0.7, slope_53[1], r"$-5/3$", 2.5),
        (k_ref[1] * 0.7, slope_3[1],  r"$-3$",   0.3),
    ]:
        ax.annotate(txt, xy=(k_ann, slope),
                    xytext=(k_ann * 1.5, slope * dy),
                    color="white", fontsize=11, ha="left",
                    arrowprops=dict(arrowstyle="->", color="white", lw=1))

    ax.set_xlabel("Wavenumber  $k$  [px$^{-1}$]", color="white", fontsize=12)
    ax.set_ylabel("Energy  $E(k)$  [a.u.]",        color="white", fontsize=12)
    ax.set_title("Turbulent Kinetic Energy Spectrum\n"
                 "(dense optical flow · bubbleVectors2.mp4)",
                 color="white", fontsize=13, pad=12)

    ax.tick_params(colors="white", which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")

    ax.xaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs="all", numticks=10))
    ax.grid(which="major", color="#2a2a2a", lw=0.8)
    ax.grid(which="minor", color="#1a1a1a", lw=0.4)

    legend = ax.legend(framealpha=0.25, edgecolor="#555", fontsize=10,
                       labelcolor="white")
    legend.get_frame().set_facecolor("#111")

    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"[INFO] Saved spectrum plot → {output}")
    plt.show()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if not Path(args.video).exists():
        sys.exit(f"[ERROR] Video file not found: {args.video}")

    print(f"[INFO] Loading video: {args.video}")
    tke_field, (H, W) = extract_velocity_fields(args.video, args.frames)
    print(f"[INFO] Frame size: {W}×{H} px")

    print("[INFO] Computing energy spectrum …")
    k, Ek = compute_spectrum(tke_field, pixel_scale=args.scale)

    print("[INFO] Plotting …")
    plot_spectrum(k, Ek, smooth_width=args.smooth, output=args.output)


if __name__ == "__main__":
    main()
