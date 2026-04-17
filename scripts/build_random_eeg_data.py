"""
Random-EEG control: replace the 5-band EEG (x_Delta..x_Gamma) with i.i.d.
Gaussian noise matched to the original per-band mean/std, then re-derive all
downstream EEG-side features, co-reconstruction features, point-level events,
and Ricci time series. Quantum side is untouched. E_Ricci is also replaced
per-session with Gaussian noise matched to the original E_Ricci stats
(time-shuffled equivalent), and Q_Ricci_affine is re-aligned to the new
E_Ricci. Writes output to IDPC_Reproduction_random/ and
IDPC_Reproduction_ricci_random/.
"""
from __future__ import annotations

import os
import glob
import math
import shutil

import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import spearmanr

RNG_SEED = 42
SRC_EEG_DIR = "IDPC_Reproduction"
SRC_RICCI_DIR = "IDPC_Reproduction_ricci"
DST_EEG_DIR = "IDPC_Reproduction_random"
DST_RICCI_DIR = "IDPC_Reproduction_ricci_random"

BAND_COLS = ["x_Delta", "x_Theta", "x_Alpha", "x_Beta", "x_Gamma"]
CIRCLE_ANGLES = np.array([2 * np.pi / 5 * k for k in range(5)], float)
C_COS = np.cos(CIRCLE_ANGLES)
C_SIN = np.sin(CIRCLE_ANGLES)


def ensure_clean_dir(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def wrap_pi(a: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * a))


def dtheta_series(theta: np.ndarray) -> np.ndarray:
    theta = np.asarray(theta, float)
    out = np.full_like(theta, np.nan, dtype=float)
    m = np.isfinite(theta)
    if m.sum() < 3:
        return out
    t = np.arange(len(theta))
    th = theta.copy()
    if not m.all():
        th[~m] = np.interp(t[~m], t[m], th[m])
    d1 = wrap_pi(np.diff(th))
    out[1:] = d1
    out[~m] = np.nan
    return out


def d2theta_series(theta: np.ndarray) -> np.ndarray:
    theta = np.asarray(theta, float)
    out = np.full_like(theta, np.nan, dtype=float)
    m = np.isfinite(theta)
    if m.sum() < 4:
        return out
    t = np.arange(len(theta))
    th = theta.copy()
    if not m.all():
        th[~m] = np.interp(t[~m], t[m], th[m])
    d1 = wrap_pi(np.diff(th))
    d2 = wrap_pi(np.diff(d1))
    out[2:] = d2
    out[~m] = np.nan
    return out


def zscore_cols_safe(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0)
    sd = np.where(~np.isfinite(sd) | (sd < 1e-12), 1.0, sd)
    mu = np.where(np.isfinite(mu), mu, 0.0)
    return (X - mu) / sd


def circular_theta_radius(X5: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Xz = zscore_cols_safe(X5)
    Xz = np.nan_to_num(Xz, nan=0.0, posinf=0.0, neginf=0.0)
    real = Xz @ C_COS
    imag = Xz @ C_SIN
    theta_h = np.arctan2(imag, real)
    radius = np.sqrt(real ** 2 + imag ** 2)
    return theta_h.astype(float), radius.astype(float)


def rederive_eeg_features(ts: pd.DataFrame) -> pd.DataFrame:
    X5 = ts[BAND_COLS].to_numpy(float)
    theta_h, radius = circular_theta_radius(X5)
    d1 = dtheta_series(theta_h)
    d2 = d2theta_series(theta_h)
    dr1 = np.full(len(radius), np.nan, float)
    dr1[1:] = np.diff(radius)
    dr2 = np.full(len(radius), np.nan, float)
    dr2[2:] = np.diff(dr1[1:])
    ts = ts.copy()
    ts["theta_h"] = theta_h
    ts["radius"] = radius
    ts["dtheta"] = d1
    ts["d2theta"] = d2
    ts["kappa_torus"] = np.abs(d2)
    ts["dr"] = dr1
    ts["d2r"] = dr2
    ts["kappa_geom"] = np.abs(dr2)
    return ts


def randomize_eeg_bands(ts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    ts = ts.copy()
    for col in BAND_COLS:
        x = pd.to_numeric(ts[col], errors="coerce").to_numpy(float)
        mu = float(np.nanmean(x))
        sd = float(np.nanstd(x))
        sd = sd if np.isfinite(sd) and sd > 1e-12 else 1.0
        ts[col] = rng.normal(loc=mu, scale=sd, size=len(x))
    return rederive_eeg_features(ts)


# ----- Co-reconstruction parameters (frozen) -----
W_COR = 30
L_LAG = 15
MU = 0.07473502200287789
LAM = -0.38142551842370215
ALPHA = -0.008316367642562725
BETA_K = -0.35188553134398226
GAMMA = 6.898081504641525e-05


def z_nan(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    m = np.nanmean(x)
    s = np.nanstd(x)
    if not np.isfinite(s) or s == 0:
        return x * 0.0
    return (x - m) / s


def corr_safe(a: np.ndarray, b: np.ndarray) -> float:
    m = np.isfinite(a) & np.isfinite(b)
    if np.sum(m) < 10:
        return np.nan
    aa = a[m]
    bb = b[m]
    if np.std(aa) == 0 or np.std(bb) == 0:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def best_corr_lagsearch(kz: np.ndarray, mz: np.ndarray, W: int, L: int) -> np.ndarray:
    T = len(kz)
    out = np.full(T, np.nan)
    for t0 in range(0, T - W):
        aa = kz[t0:t0 + W]
        if np.any(~np.isfinite(aa)):
            continue
        best = -np.inf
        bestC = np.nan
        for lag in range(-L, L + 1):
            j0 = t0 + lag
            j1 = j0 + W
            if j0 < 0 or j1 > T:
                continue
            bb = mz[j0:j1]
            if np.any(~np.isfinite(bb)):
                continue
            c = corr_safe(aa, bb)
            if not np.isfinite(c):
                continue
            if abs(c) > best:
                best = abs(c)
                bestC = c
        out[t0] = bestC
    return out


def roll_median(x: np.ndarray, W: int) -> np.ndarray:
    T = len(x)
    out = np.full(T, np.nan)
    for t0 in range(0, T - W):
        seg = x[t0:t0 + W]
        seg = seg[np.isfinite(seg)]
        if len(seg):
            out[t0] = np.median(seg)
    return out


def roll_slope(x: np.ndarray, W: int) -> np.ndarray:
    T = len(x)
    out = np.full(T, np.nan)
    for t0 in range(0, T - W):
        seg = x[t0:t0 + W]
        m = np.isfinite(seg)
        if np.sum(m) < 10:
            continue
        y = seg[m]
        xx = np.arange(len(seg))[m]
        vx = np.var(xx)
        if vx == 0:
            continue
        out[t0] = np.cov(xx, y, bias=True)[0, 1] / vx
    return out


def build_co_recon(eeg_ts: pd.DataFrame, q_ts: pd.DataFrame) -> pd.DataFrame:
    d2 = eeg_ts["d2theta"].to_numpy(float)
    kappa = np.abs(d2)

    radQ = q_ts["radius"].to_numpy(float)
    MQ_task = z_nan(radQ)
    mq = (
        eeg_ts["task_idx"].astype(int).to_frame()
        .merge(
            pd.DataFrame({
                "task_idx": q_ts["task_idx"].astype(int).to_numpy(),
                "MQ": MQ_task,
            }),
            on="task_idx",
            how="left",
        )["MQ"].to_numpy(float)
    )

    kz = z_nan(kappa)
    mz = z_nan(mq)

    bc = best_corr_lagsearch(kz, mz, W_COR, L_LAG)
    a = np.abs(bc)

    kL = roll_median(kappa, W_COR)
    kS = roll_slope(kappa, W_COR)
    mL = roll_median(mq, W_COR)

    g = ALPHA * kL + BETA_K * kS + GAMMA * mL
    h = g - MU * a - LAM * (a ** 3)

    valid = np.zeros(len(a), bool)
    valid[:max(0, len(a) - W_COR)] = True

    return pd.DataFrame({
        "t": np.arange(len(eeg_ts)),
        "valid": valid,
        "kappa": kappa,
        "mq": mq,
        "a": a,
        "kL": kL,
        "kS": kS,
        "mqL": mL,
        "g": g,
        "h": h,
    })


def points_from_co_recon(co: pd.DataFrame) -> pd.DataFrame:
    """Reconstruct the points CSV schema used downstream. Only columns
    required by Chapter 7 data-prep (h, a, valid) need to be meaningful;
    MRS_* are filled with zeros since downstream usage is independent."""
    out = pd.DataFrame({
        "t": co["t"].astype(float),
        "valid": co["valid"].astype(int),
        "kappa": co["kappa"],
        "MQ": co["mq"],
        "a": co["a"],
        "kL": co["kL"],
        "kS": co["kS"],
        "mL": co["mqL"],
        "g": co["g"],
        "h": co["h"],
        "MRS_old": 0,
        "MRS_valley": 0,
        "MRS_gmm": 0,
        "MRS_h": 0,
    })
    return out


def affine_match_safe(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    src = np.asarray(src, float)
    ref = np.asarray(ref, float)
    if np.isfinite(src).sum() < 3 or np.isfinite(ref).sum() < 3:
        return src.copy()
    ms = float(np.nanmean(src))
    ss = float(np.nanstd(src)) + 1e-12
    mr = float(np.nanmean(ref))
    sr = float(np.nanstd(ref)) + 1e-12
    return (src - ms) * (sr / ss) + mr


def corr_at_lag(x, y, lag):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    if lag > 0:
        return x[:n - lag], y[lag:]
    if lag < 0:
        k = -lag
        return x[k:], y[:n - k]
    return x, y


def best_lag_by_absrho(x, y, lags=range(-6, 7), min_overlap=8):
    best = None
    for lag in lags:
        xa, ya = corr_at_lag(x, y, lag)
        if xa.size < min_overlap:
            continue
        rho, _ = spearmanr(xa, ya)
        if not np.isfinite(rho):
            continue
        cand = {"lag": int(lag), "rho": float(rho), "absrho": float(abs(rho))}
        if best is None or cand["absrho"] > best["absrho"]:
            best = cand
    return best


def make_shift(Q: np.ndarray, lag: int) -> np.ndarray:
    Q = np.asarray(Q, float)
    N = len(Q)
    out = np.full(N, np.nan, float)
    if lag > 0:
        out[lag:] = Q[:-lag]
    elif lag < 0:
        k = -lag
        out[:-k] = Q[k:]
    else:
        out[:] = Q[:]
    return out


def randomize_ricci(ricci_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    orig_E = pd.to_numeric(ricci_df["E_Ricci"], errors="coerce").to_numpy(float)
    mu = float(np.nanmean(orig_E))
    sd = float(np.nanstd(orig_E))
    sd = sd if np.isfinite(sd) and sd > 1e-12 else 1.0
    mask = np.isfinite(orig_E)
    new_E = orig_E.copy()
    new_E[mask] = rng.normal(loc=mu, scale=sd, size=int(mask.sum()))
    Q = pd.to_numeric(ricci_df["Q_Ricci"], errors="coerce").to_numpy(float)

    best = best_lag_by_absrho(Q[np.isfinite(Q) & np.isfinite(new_E)],
                              new_E[np.isfinite(Q) & np.isfinite(new_E)])
    lag = 0 if best is None else int(best["lag"])
    Q_shifted = make_shift(Q, lag)
    Q_affine = affine_match_safe(Q_shifted, new_E)

    return pd.DataFrame({
        "task_idx": ricci_df["task_idx"].astype(int).to_numpy(),
        "E_Ricci": new_E,
        "Q_Ricci": Q,
        "Q_Ricci_shifted": Q_shifted,
        "Q_Ricci_affine": Q_affine,
    })


def list_sessions(src_dir: str) -> list[str]:
    files = sorted(glob.glob(os.path.join(src_dir, "*_eeg_timeseries.csv")))
    return [os.path.basename(f).replace("_eeg_timeseries.csv", "") for f in files]


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    ensure_clean_dir(DST_EEG_DIR)
    ensure_clean_dir(DST_RICCI_DIR)

    sessions = list_sessions(SRC_EEG_DIR)
    print(f"Sessions: {len(sessions)}")

    for lab in sessions:
        eeg = pd.read_csv(os.path.join(SRC_EEG_DIR, f"{lab}_eeg_timeseries.csv"))
        q = pd.read_csv(os.path.join(SRC_EEG_DIR, f"{lab}_quantum_timeseries.csv"))

        eeg_rand = randomize_eeg_bands(eeg, rng)
        co = build_co_recon(eeg_rand, q)
        pts = points_from_co_recon(co)

        eeg_rand.to_csv(os.path.join(DST_EEG_DIR, f"{lab}_eeg_timeseries.csv"), index=False)
        q.to_csv(os.path.join(DST_EEG_DIR, f"{lab}_quantum_timeseries.csv"), index=False)
        co.to_csv(os.path.join(DST_EEG_DIR, f"{lab}_co_recon_features_W30.csv"), index=False)
        pts.to_csv(os.path.join(DST_EEG_DIR, f"{lab}_co_recon_features_W30_points.csv"), index=False)

        src_ricci_path = os.path.join(SRC_RICCI_DIR, f"{lab}_timeseries.csv")
        if os.path.exists(src_ricci_path):
            ricci = pd.read_csv(src_ricci_path)
            ricci_rand = randomize_ricci(ricci, rng)
            ricci_rand.to_csv(os.path.join(DST_RICCI_DIR, f"{lab}_timeseries.csv"), index=False)

        print(f"  {lab}: wrote {len(eeg_rand)} eeg rows, {len(co)} co_recon rows")

    print("\nDone.")
    print("EEG random dir:", DST_EEG_DIR)
    print("Ricci random dir:", DST_RICCI_DIR)


if __name__ == "__main__":
    main()
