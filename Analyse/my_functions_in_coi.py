import numpy as np
import pandas as pd
import uproot as up 
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.path import Path
from matplotlib.collections import LineCollection
from matplotlib.ticker import MultipleLocator
import imageio.v2 as imageio  # v2 pour éviter des warnings
from natsort import natsorted 

def hist_sub_time(data_list=[],nb_bin=50,label_list=[]):
    #data = df.query("sub_time < 1000")["sub_time"]
    fig, ax = plt.subplots()
    for i, data in enumerate(data_list):
        plt.hist(data, bins=nb_bin, range=(np.min(data),np.max(data)),log=True,label=label_list[i])
    
    ax.set_xlabel("Time [ns]")
    ax.set_ylabel("Counts")
    ax.xaxis.set_major_locator(MultipleLocator(10))  # Graduations tous les 10 ns
    plt.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5)
    plt.grid(True, which="both", axis='x', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()


def plot_amp_ratio_hist2D(df, label="Data", channels=[5, 6, 7], bins=1000,
                            xlim=(0, 15), ylim=(0, 1200), save_dir=None, filename=None):
    """
    Pour chaque canal, affiche une figure contenant un histogramme 2D :
    X : ratio (q / max_amp) (en ADC)
    Y : max_amp (en mV)

    Avec :
    - Colorbar propre à chaque figure
    - Axes X/Y personnalisables
    """

    PMs = ["Opposite", "Close", "Bottom"]

    for i, ch in enumerate(channels):
        df_ch = df.query("sub_channel == @ch")
        x = df_ch["sub_Q"] / df_ch["sub_max_amp"]
        y = df_ch["sub_max_amp"]

        fig, ax = plt.subplots(figsize=(6, 5))

        h = ax.hist2d(x, y, bins=bins, range=[[xlim[0], xlim[1]], [ylim[0], ylim[1]]], cmap="viridis", norm=mcolors.LogNorm(vmin=1))
        if ch != "sum":
            ax.set_title(f"{label} - {PMs[i]}")
        else :
            ax.set_title(f"{label} - Sum")
        ax.set_xlabel("Q_tot / Amp_tot  (a.u.)")
        ax.set_ylabel("Amp_tot (mV)")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)

    cbar = fig.colorbar(h[3], ax=ax, label="Number of events (log)")

    plt.tight_layout()
    
    # Sauvegarde avec suffixe spécifique au canal
    if save_dir and filename:
        os.makedirs(save_dir, exist_ok=True)
        suffix = f"_PM{ch}" if ch != "sum" else "_sum"
        full_path = os.path.join(save_dir, f"{filename}{suffix}.png")
        fig.savefig(full_path, dpi=300)

    plt.show()   