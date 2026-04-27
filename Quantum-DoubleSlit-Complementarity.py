# -*- coding: utf-8 -*-
"""
Berramdane Model V9.4 – Quantum Double‑Slit Complementarity Simulator
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

# === الثوابت الفيزيائية ===
h = 6.626e-34      # ثابت بلانك
m = 9.109e-31      # كتلة الإلكترون
L_total = 2.2      # المسافة بين الشقوق والشاشة

# ========== إضافة حساب الزوايا (كما طلب ديبسيك) ==========
def compute_angles(v_mean, a_width, d_slit, L):
    """
    تحسب زاوية أول هدب تداخل وزاوية أول عقدة حيود.
    θ (rad) ≈ λ / d  و θ (rad) ≈ λ / a.
    """
    lam = h / (m * v_mean)
    # زاوية أول هدب تداخل: θ = λ / d_slit
    theta_i_rad = lam / d_slit
    theta_i_deg = theta_i_rad * 180 / np.pi
    # زاوية أول عقدة حيود: θ = λ / a_width
    theta_d_rad = lam / a_width
    theta_d_deg = theta_d_rad * 180 / np.pi
    return (theta_i_rad, theta_i_deg, theta_d_rad, theta_d_deg)

def de_broglie_wavelength(v):
    return h / (m * v)

def double_slit_intensity_single_velocity(x, v_par, L, a_width, d_slit):
    lam = de_broglie_wavelength(v_par)
    beta = (np.pi * d_slit * x) / (lam * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (lam * L
