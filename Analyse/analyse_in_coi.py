import numpy as np
import pandas as pd
import uproot as up 
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.path import Path
from matplotlib.collections import LineCollection


on_lab_desktop = False
on_my_laptop = not on_lab_desktop

#saving fig path
if on_lab_desktop == True:
    save_dir_path = "/home/vezon/bruit_de_fond"
if on_my_laptop == True:
    save_dir_path = "/Users/antoinevezon/Desktop/"


### LECTURE DU DATATREE ###                                                                            |Corresponding names manually created with mon_group2tree_v3       

rootfile_name_a = "Test_GADGET_GorG2orG4orG24_0001.root"         # 500mbar                             |GorG2orG4orG24.root" 500 mbar
rootfile_name_b = "Test_GADGET_GorG2orG4orG24_V2_0001.root"      # 500mbar                             |GorG2orG4orG24_V2.root" 500 mbar
rootfile_name_c = "Test_GADGET_1bar_GorG2orG4orG24.root"         #                                     |1bar_GorG2orG4orG24.root
rootfile_name_d = "Test_GADGET_1.5bar_GorG2orG4orG24_0001.root"  #                                     |1.5bar_GorG2orG4orG24.root

rootfile_name_e = "New_plastics_2000V_atleast_GADGET_withblackcover_500mbar_0001.root"  # \            |New_plastics_atleastGAD_500mbar.root
rootfile_name_f = "New_plastics_2500V_atleast_GADGET_withblackcover_1000mbar_0001.root" #  |           |New_plastics_atleastGAD_1000mbar.root
rootfile_name_g = "New_plastics_2500V_atleast_GADGET_withblackcover_ascension_0001.root"# /¦ 1500mbar  |New_plastics_atleastGAD_1500mbar.root
rootfile_name_h = "New_plastics_2000V_atleastGAD_Empty_0001.root"#                         ¦           |New_plastics_atleastGAD_Empty.root 
rootfile_name_i = "New_plastics_atleastGAD_Empty_V2_0001.root"   #                         ¦           |New_plastics_atleastGAD_Empty_V2.root
#                                                                                          v  
#                                                            QDC_2 & QDC_4 = resp. Right & Left_pastic ! 
#                                                            Donc il faut les échanger pour etre identique aux Empty                                    
##################################
rootfile_use = rootfile_name_i
##################################

if on_lab_desktop == True:
    path_to_DataTree = f"/home/vezon/bruit_de_fond/data/root/faster2root/{rootfile_use}:DataTree;1"
if on_my_laptop == True:
    path_to_DataTree = f"/Users/antoinevezon/Desktop/bruit_de_fond/data/root/faster2root/{rootfile_use}:DataTree;1"
   

DataTree = up.open(path_to_DataTree)

DataTree.show()
Keys = DataTree.keys()
print(f"Keys = {Keys}")

df = DataTree.arrays(Keys, library="pd")

print(df.iloc[:,:6].head(20))


data=df.query("sub_time == 0")["sub_Q"]


plt.hist(data, bins=500, range=(np.min(data),np.max(data)),log=True)
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
"""
plot_amp_ratio_hist2D(df)
plt.show()"""