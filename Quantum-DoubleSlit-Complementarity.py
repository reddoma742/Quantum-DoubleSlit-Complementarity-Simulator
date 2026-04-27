# -*- coding: utf-8 -*-
"""
Berramdane Model V9.3 – Quantum Double‑Slit Complementarity Simulator
Author : Al Moalim Berramdane
License: CC BY 4.0
Interactive simulation for Jupyter Notebook / Google Colab.
"""

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Checkbox, IntSlider
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# === Only used physical constants ===
h = 6.626e-34      # Planck constant (J·s)
m = 9.109e-31      # Electron mass (kg)
L_total = 2.2      # Distance from slits to screen (m)

def de_broglie_wavelength(v):
    return h / (m * v)

def double_slit_intensity_single_velocity(x, v_par, L, a_width, d_slit):
    lam = de_broglie_wavelength(v_par)
    beta = (np.pi * d_slit * x) / (lam * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (lam * L)
    envelope = np.sinc(alpha / np.pi)**2
    return interference * envelope

def double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=100):
    velocities = np.random.normal(v_mean, delta_v, n_samples)
    total = np.zeros_like(x)
    for v in velocities:
        total += double_slit_intensity_single_velocity(x, v, L, a_width, d_slit)
    return total / n_samples

def particle_like_pattern(x, v_par, L, a_width, d_slit):
    """
    Corrected two‑peak distribution representing which‑path information.
    Each peak corresponds to particles passing through one slit.
    """
    lam = de_broglie_wavelength(v_par)
    sigma = a_width * L / lam
    I_left = np.exp(-(x + d_slit/2)**2 / (2 * sigma**2))
    I_right = np.exp(-(x - d_slit/2)**2 / (2 * sigma**2))
    return 0.5 * (I_left + I_right)

def compute_visibility(x, I):
    peaks, _ = find_peaks(I, distance=len(x)//30)
    if len(peaks) < 2:
        return 0.0
    I_max = np.max(I[peaks])
    center_idx = np.argmin(np.abs(x))
    search = np.where(np.abs(x - x[center_idx]) < 5e-3)[0]
    I_min = np.min(I[search]) if len(search) > 0 else np.min(I)
    return (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

@interact(
    v_mean=FloatSlider(value=5.8e5, min=2e5, max=1.2e6, step=0.1e5, description='Mean velocity (m/s)'),
    delta_v=FloatSlider(value=0.0, min=0.0, max=2e5, step=0.1e4, description='Velocity spread Δv (m/s)'),
    a_width=FloatSlider(value=0.72e-6, min=0.2e-6, max=1.5e-6, step=0.01e-6, description='Slit width (m)'),
    d_slit=FloatSlider(value=2.45e-6, min=1.0e-6, max=5.0e-6, step=0.05e-6, description='Slit separation (m)'),
    observer_active=Checkbox(value=False, description='Which‑path detector ON'),
    meas_strength=FloatSlider(value=0.0, min=0.0, max=1.0, step=0.01, description='Measurement strength'),
    temperature=FloatSlider(value=0.0, min=0, max=1000, step=10, description='Detector noise (K equiv)'),
    show_buildup=Checkbox(value=False, description='Show temporal buildup'),
    n_particles=IntSlider(value=300, min=50, max=1000, step=50, description='Particles (buildup)')
)
def interactive_lab(v_mean, delta_v, a_width, d_slit, observer_active, meas_strength,
                    temperature, show_buildup, n_particles):

    if a_width >= d_slit:
        print("⚠️ Adjusting slit width < separation")
        a_width = d_slit * 0.99

    x = np.linspace(-0.005, 0.005, 1500)

    if delta_v > 0:
        I_interf = double_slit_intensity_with_spread(x, v_mean, delta_v, L_total, a_width, d_slit, n_samples=100)
    else:
        I_interf = double_slit_intensity_single_velocity(x, v_mean, L_total, a_width, d_slit)

    I_particle = particle_like_pattern(x, v_mean, L_total, a_width, d_slit)

    if observer_active:
        I = (1 - meas_strength) * I_interf + meas_strength * I_particle
    else:
        I = I_interf

    if show_buildup:
        cumulative = np.zeros_like(x)
        for _ in range(n_particles):
            if delta_v > 0:
                I_one = double_slit_intensity_with_spread(x, v_mean, delta_v, L_total, a_width, d_slit, n_samples=20)
            else:
                I_one = double_slit_intensity_single_velocity(x, v_mean, L_total, a_width, d_slit)
            if observer_active:
                I_one = (1 - meas_strength) * I_one + meas_strength * particle_like_pattern(x, v_mean, L_total, a_width, d_slit)
            cumulative += I_one
        I = cumulative / n_particles

    if temperature > 0:
        noise = (temperature / 1000.0) * 0.15 * np.max(I)
        I += np.random.normal(0, noise, len(I))
        I = np.maximum(I, 0)

    if np.max(I) > 0:
        I /= np.max(I)

    I_interf_norm = I_interf / np.max(I_interf) if np.max(I_interf) > 0 else I_interf
    I_particle_norm = I_particle / np.max(I_particle) if np.max(I_particle) > 0 else I_particle

    visibility = compute_visibility(x, I)
    lam = de_broglie_wavelength(v_mean)
    spacing_mm = lam * L_total / d_slit * 1000

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    # Main pattern
    ax1.plot(x * 1000, I, 'b-', lw=1.5)
    ax1.fill_between(x * 1000, I, alpha=0.3)
    title = f'Double‑slit | Visibility = {visibility:.1%}'
    if observer_active:
        title += f' | Path strength = {meas_strength:.2f}'
        if meas_strength > 0.9:
            title += ' (Particle‑like)'
        elif meas_strength > 0.1:
            title += ' (Partial coherence)'
        else:
            title += ' (Interference)'
    if delta_v > 0:
        title += f' | Δv = {delta_v/1e3:.0f} km/s'
    if temperature > 0:
        title += f' | Noise = {temperature:.0f} K'
    ax1.set_title(title)
    ax1.set_xlabel('Position (mm)')
    ax1.set_ylabel('Intensity')
    ax1.set_xlim(-5, 5)
    ax1.grid(alpha=0.3)

    # Detector screen
    screen = np.tile(I, (150, 1))
    im = ax2.imshow(screen, cmap='hot', aspect='auto', extent=[-5, 5, 0, 1])
    ax2.set_title('Detector screen')
    ax2.set_xlabel('Position (mm)')
    ax2.set_yticks([])
    plt.colorbar(im, ax=ax2, label='Intensity', shrink=0.8)

    # Complementarity comparison
    ax3.plot(x * 1000, I_interf_norm, 'b--', lw=1, alpha=0.7, label='Pure interference')
    ax3.plot(x * 1000, I_particle_norm, 'r--', lw=1, alpha=0.7, label='Pure which‑path')
    ax3.plot(x * 1000, I, 'k-', lw=2, label='Current state')
    ax3.set_xlim(-5, 5)
    ax3.set_ylim(0, 1.05)
    ax3.set_title('Complementarity principle')
    ax3.set_xlabel('Position (mm)')
    ax3.set_ylabel('Normalised intensity')
    ax3.legend(fontsize=8, loc='upper right')
    ax3.grid(alpha=0.3)

    # Information panel
    info = (f"Fringe spacing: {spacing_mm:.2f} mm\n"
            f"λ = {lam*1e9:.2f} nm\n"
            f"v = {v_mean/1e3:.0f} km/s\n"
            f"Slit width = {a_width*1e6:.2f} µm\n"
            f"Separation = {d_slit*1e6:.2f} µm\n"
            f"Complementarity: V = {visibility:.2f}")
    ax4.text(0.05, 0.95, info, transform=ax4.transAxes, fontsize=10, va='top')
    ax4.axis('off')

    plt.tight_layout()
    plt.show()
    print(f"✅ Visibility: {visibility:.1%} | Theoretical spacing: {spacing_mm:.2f} mm")

if __name__ == "__main__":
    print("This code is intended for Jupyter Notebook / Google Colab.\n"
          "Please run it in an interactive environment to see the widgets.")


Fix V9.3 with correct exponent syntax.
   
