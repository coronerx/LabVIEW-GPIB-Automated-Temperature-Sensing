"""
LabVIEW/GPIB Automated Data Acquisition — Post-Processing
Physics 327, Lab 9

Re-analyzes data captured via GPIB (HP 34401A multimeter) and LabVIEW VIs
built for this lab: thermistor resistance response, and the AD590/LM741
temperature-transducer circuit.

Data files expected in ./data/:
  thermistor_room_temp.csv     - resistance vs time at room temperature (provided)
  thermistor_hand_hold.csv     - resistance vs time while holding sensor  (optional, drop in if you still have it)
  thermistor_release.csv       - resistance vs time after releasing      (optional)
  ad590_temp_raw.csv           - temperature vs time, x3 scaling error   (optional)
  ad590_temp_corrected.csv     - temperature vs time, corrected scaling  (optional)

Any file that isn't present is simply skipped — the script still runs
on whatever data you have.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

DATA_DIR = "data"
OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)


def exp_decay(t, a, tau, c):
    """R(t) = a * exp(-t/tau) + c"""
    return a * np.exp(-t / tau) + c


def exp_growth(t, a, tau, c):
    """R(t) = c - a * exp(-t/tau)  (approaches c from below)"""
    return c - a * np.exp(-t / tau)


def load(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def fit_and_plot(df, ycol, title, fname, model=exp_decay, p0=None):
    t = df["time_s"].to_numpy(dtype=float)
    y = df[ycol].to_numpy(dtype=float)

    if p0 is None:
        p0 = [y[0] - y[-1], (t[-1] - t[0]) / 2, y[-1]]

    try:
        popt, pcov = curve_fit(model, t, y, p0=p0, maxfev=10000)
        perr = np.sqrt(np.diag(pcov))
        fit_ok = True
    except RuntimeError:
        popt, perr, fit_ok = None, None, False

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(t, y, color="tab:blue", label="measured", zorder=3)

    if fit_ok:
        t_fine = np.linspace(t.min(), t.max(), 300)
        ax.plot(t_fine, model(t_fine, *popt), color="tab:red", lw=1.5,
                 label=f"fit: tau={popt[1]:.2f}s +/- {perr[1]:.2f}s")
        print(f"[{title}] amplitude={popt[0]:.3f}, tau={popt[1]:.3f} s "
              f"(+/-{perr[1]:.3f}), asymptote={popt[2]:.3f}")
    else:
        print(f"[{title}] exponential fit did not converge — check data/p0")

    ax.set_xlabel("time / s")
    ax.set_ylabel(ycol)
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, fname), dpi=150)
    plt.close(fig)
    print(f"  -> saved {os.path.join(OUT_DIR, fname)}\n")


def main():
    # --- Thermistor at room temperature (baseline drift) ---
    df = load("thermistor_room_temp.csv")
    if df is not None:
        fit_and_plot(df, "resistance_ohm",
                     "Thermistor resistance — room temperature baseline",
                     "thermistor_room_temp.png",
                     model=exp_decay,
                     p0=[300, 5, 862700])

    # --- Thermistor while hand-holding (should decay toward lower R) ---
    df = load("thermistor_hand_hold.csv")
    if df is not None:
        fit_and_plot(df, "resistance_ohm",
                     "Thermistor resistance — hand-held (heating)",
                     "thermistor_hand_hold.png",
                     model=exp_decay)
    else:
        print("[skip] thermistor_hand_hold.csv not found — drop your raw "
              "log in data/ to include Figure 3's 10-point series.")

    # --- Thermistor after release (relaxing back toward room temp) ---
    df = load("thermistor_release.csv")
    if df is not None:
        fit_and_plot(df, "resistance_ohm",
                     "Thermistor resistance — after release (cooling back)",
                     "thermistor_release.png",
                     model=exp_growth)
    else:
        print("[skip] thermistor_release.csv not found — drop your raw "
              "log in data/ to include Figure 4's 20-point series.")

    # --- AD590/LM741 raw (x3 scaling error) ---
    df = load("ad590_temp_raw.csv")
    if df is not None:
        fit_and_plot(df, "temperature_K",
                     "AD590 temperature — raw (x3 scaling bug)",
                     "ad590_temp_raw.png")
    else:
        print("[skip] ad590_temp_raw.csv not found — this is the dataset "
              "behind the x3 calibration-error story (Figure 5).")

    # --- AD590/LM741 corrected ---
    df = load("ad590_temp_corrected.csv")
    if df is not None:
        fit_and_plot(df, "temperature_K",
                     "AD590 temperature — corrected scaling",
                     "ad590_temp_corrected.png")
    else:
        print("[skip] ad590_temp_corrected.csv not found — corresponds "
              "to Figure 6, the corrected -100x conversion.")


if __name__ == "__main__":
    main()
