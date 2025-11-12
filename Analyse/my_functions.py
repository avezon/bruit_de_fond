#!/usr/bin/env python
# coding: utf-8

# In[15]:


import numpy as np
import pandas as pd
import uproot as up 
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.path import Path
from matplotlib.collections import LineCollection
import imageio.v2 as imageio  # v2 pour éviter des warnings
from natsort import natsorted 
#import dataframe_image as dfi


# In[16]:


def hist_567_compare_q(df_1, df_2, title_line_0="", title_line_1="", title_suffix="", just_sum=False, save_dir=None, filename=None):
    """
    Affiche les histogrammes des charges QT2T_5_q à QT2T_7_q + QT2T_sum_q :
    - 2 lignes (df_1 et df_2), 4 colonnes (1 par PM)
    - Si just_sum=True : n'affiche que la colonne QT2T_sum_q
    """
    
    # Colonnes à traiter
    if just_sum:
        cols = ["QT2T_sum_q"]
        PMs = ["Sum"]
        fig, axes = plt.subplots(2, 1, figsize=(6, 6), sharey='row')
    else:
        cols = ["QT2T_5_q", "QT2T_6_q", "QT2T_7_q", "QT2T_sum_q"]
        PMs = ["Opposite", "Close", "Bottom", "Sum"]
        fig, axes = plt.subplots(2, 4, figsize=(15, 8), sharey='row')

    #plt.subplots_adjust(hspace=0.4)

    for i, col in enumerate(cols):
        # Récupérer le sous-axe si just_sum=True (axes 1D dans ce cas)
        ax_top = axes[0, i] if not just_sum else axes[0]
        ax_bot = axes[1, i] if not just_sum else axes[1]

        # Définition du range commun 
        min_val = min(df_1[col].min(), df_2[col].min())
        x_range = (min_val, 60000 if col != "QT2T_sum_q" else 100000)

        # Ligne 1
        data_1 = df_1[col].dropna()
        ax_top.hist(data_1, bins=500, range=x_range, alpha=0.7, color='skyblue')
        if col == "QT2T_sum_q":   # Pour éviter les problèmes d’échelle : forcer des bornes
            ax_top.set_yscale('log')
            ax_top.set_xlabel("Q_tot (a.u.)")
        else:
            ax_top.set_xlabel("Q (a.u.)")
        ax_top.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
        ax_top.set_title(f"{PMs[i]} ({title_line_0})")
        if i == 0:
            ax_top.set_ylabel("Number of events")

        # Ligne 2
        data_2 = df_2[col].dropna()
        ax_bot.hist(data_2, bins=500, range=x_range, alpha=0.7, color='salmon')
        if col == "QT2T_sum_q":
            ax_bot.set_yscale('log')
            ax_bot.set_xlabel("Q_tot (a.u.)")
        else:
            ax_bot.set_xlabel("Q (a.u.)")
        ax_bot.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
        ax_bot.set_title(f"{PMs[i]} ({title_line_1})")
        if i == 0:
            ax_bot.set_ylabel("Number of events")

    # Titre général
    fig.suptitle(f"{title_suffix}", fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.subplots_adjust(left=0.07)# espace à gauche pour le label y

    # Enregistrement
    if save_dir and filename:
        full_path = os.path.join(save_dir, f"{filename}.png")
        plt.savefig(full_path, dpi=300)




def plot_dalitz_triangle_scat(df, df_tot, rootfile, subdivisions=4, Gain_norm=None, Title="Charge repartition ternary plot", charge_interval=None, save_dir=None, filename=None):
    """Cette fonction trace le triangle de répartition des charges vu par les 3 PMP. À chaques événements de df, on associe un point dans le triangle dont les coordonnées cartésiennes dépendent de Qt2t 5, 6 et 7 : 
    ( x , y ) = ( 1/2*(Q5+2*Q6)/Q_gr , √3/2*Q_5/Q_gr )
        """
    # Sélection des colonnes Qt2t
    qt1 = df["QT2T_5_q"]
    qt2 = df["QT2T_6_q"]
    qt3 = df["QT2T_7_q"]

    if Gain_norm is not None :
        qt1 = qt1/Gain_norm[0]
        qt2 = qt2/Gain_norm[1]
        qt3 = qt3/Gain_norm[2]

    Qgr = qt1 + qt2 + qt3
    
    x = 0.5 * (qt1 + 2 * qt2) / Qgr
    y = (np.sqrt(3) / 2) * qt1 / Qgr

    if Qgr.any() <= 0:
        raise ValueError("Qgr <= 0")

    # Triangle équilatéral : sommets A, B, C
    triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])  # C, B, A
    C, B, A = triangle[0], triangle[1], triangle[2]

    fig, ax = plt.subplots(figsize=(7, 7))

    # Points
    ax.scatter(x, y, s=0.1, alpha=0.5)

    # Bissectrices
    lines = []
    color_list = ['r', 'g', 'b']    
    bissect = np.array( [[C,1/2*A+1/2*B],[B,1/2*A],[A,1/2*B]])
    for b in range(0,3):
        lines.append(bissect[b])
        
    line_collection = LineCollection(lines, colors=color_list, linewidths=1, linestyles='-')
    ax.add_collection(line_collection) 

    # Triangle principal
    ax.plot(*zip(*np.vstack([triangle, triangle[0]])), 'k-', lw=1)

    # Grille triangulaire interne
    """Pour s subdivisions, il y a (s - 1) graduations qui ne sont pas un sommet (i.e qui ne sont pas 0% ou 100%)
    Ce sont ces graduations qui forment les points à relier correctement pour obtenire le maillage triangulaire. 
    Chaques graduations doit être reliée à celle qui lui est symétrique par rapport une des bissecrices (celles non-perp. ausegment coté gradué) soit
    3*(s - 1) segments au total"""

    lines = []
    color_list_grid = []   

    for i in range(1, subdivisions):
        f = i / subdivisions

        # Lignes parallèles aux côtés
        p1 = (1 - f) * A + f * B
        lines.append([p1, (1 - f) * C + f * B])  # parallèle à AC (perp. à la bissectrice verte)
        
        color_list_grid.append('g')

        p2 = (1 - f) * A + f * C
        lines.append([p2, (1 - f) * A + f * B])  # parallèle à CB (perp. à la bissectrisse bleue)
        
        color_list_grid.append('b')

        p3 = (1 - f) * B + f * C
        lines.append([p3, (1 - f) * A + f * C])  # parallèle à BA (perp. à la bissectrice rouge)
    
        color_list_grid.append('r')

    line_collection = LineCollection(lines, colors=color_list_grid, linewidths=1, linestyles='--')
    ax.add_collection(line_collection)

    # Légendes des côtés
    
    def place_label(p, label, offset=(0, 0), f_color='black'):
        ax.text(p[0] + offset[0], p[1] + offset[1], label,
                ha='center', va='center', fontsize=12, fontweight='bold', bbox=dict(facecolor=f_color))

    place_label(A, "PM_Opp", offset=(0, 0.04), f_color='tab:cyan')
    place_label(B, "PM_Cls", offset=(0.02, -0.05), f_color='green')
    place_label(C, "PM_Bot", offset=(-0.02, -0.05), f_color='red')

    def add_ticks_on_side(ax, P1, P2, N, tick_length=0.015, label=False):
        """
        Ajoute des ticks entre deux sommets d’un triangle.
        P1, P2 : coordonnées des deux sommets
        N : nombre de subdivisions
        tick_length : longueur des ticks
        label : True pour ajouter des labels numériques
        """
        direction = P2 - P1
        normal = np.array([-direction[1], direction[0]])
        normal = normal / np.linalg.norm(normal) * tick_length

        for i in range(1, N):  # on ignore les extrémités
            f = i / N
            point = (1 - f) * P1 + f * P2
            tick_start = point - normal / 2
            tick_end = point + normal / 2
            ax.plot([tick_start[0], tick_end[0]], [tick_start[1], tick_end[1]], color='black', lw=0.5)

            if label:
                ax.text(point[0] + normal[0]*1.5, point[1] + normal[1]*1.5,
                        f"{f:.2f}", fontsize=6, ha='center', va='center')

        
    add_ticks_on_side(ax, A, B, subdivisions)
    add_ticks_on_side(ax, B, C, subdivisions)
    add_ticks_on_side(ax, C, A, subdivisions)        


    def add_labeled_ticks(ax, P1, P2, tick_values=(0.25, 0.5, 0.75), tick_length=0.02, label_offset=0.05 , color_values='black'):
        """
        Ajoute des ticks à des fractions spécifiques entre deux sommets.
        P1, P2 : coordonnées des sommets
        tick_values : fractions (0–1) où mettre des ticks
        """
        direction = P1 - P2
        normal = np.array([direction[1], -direction[0]])
        normal = normal / np.linalg.norm(normal) * tick_length
        label_offset_vec = normal * (1 + label_offset / tick_length)

        for f in tick_values:
            point = (1 - f) * P1 + f * P2
            tick_start = point - normal / 2
            tick_end = point + normal / 2
            ax.plot([tick_start[0], tick_end[0]], [tick_start[1], tick_end[1]], color=color_values, lw=0.8)

            # Ajoute le texte
            ax.text(point[0] + label_offset_vec[0],
                    point[1] + label_offset_vec[1],
                    f"{int(f*100)}%", fontsize=12, ha='center', va='center',color=color_values)
            
    add_labeled_ticks(ax, A, B, color_values = 'green')  # côté PM_Opp ↔ PM_Cls
    add_labeled_ticks(ax, B, C, color_values = 'red')  # côté PM_Cls ↔ PM_Bot
    add_labeled_ticks(ax, C, A, color_values = 'blue')  # côté PM_Bot ↔ PM_Opp

    # Style
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, np.sqrt(3)/2 + 0.1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(Title, fontsize=10)
    ax.text(0.7, -0.2, f"File: {rootfile}", fontsize=8, color='gray', 
                    ha='right', va='bottom', transform=ax.transAxes)
    
    # Affichage de l'intervalle de charge utiliser s'il y en a un
    if charge_interval is not None:
        interval_text = f"Interval = [{charge_interval[0]}, {charge_interval[1]}]"
        plt.text(1.0, 0.02, interval_text, transform=plt.gca().transAxes,
                 ha='right', va='bottom', fontsize=9, color='gray')
        
    #Affichage du rate et de l'erreur asssociée
    time_start = df['group_time'].min()
    time_end = df['group_time'].max()
    duration_s = (time_end - time_start) * 1e-9  # convertit ns en secondes
    count = len(df)
    rate = count / duration_s
    rate_error = np.sqrt(count) / duration_s
    plt.text(1.0, -0.2, f"Average trigger rate : {rate:.4f} ± {rate_error:.4f} Hz over {duration_s/3600:.2f} h",fontsize=12,
         ha='right', va='bottom')
    #f"Nb_tot Group : {count}"

    # Enregistrement si souhaité
    if save_dir and filename:
        full_path = os.path.join(save_dir, f"{filename}.png")
        plt.savefig(full_path, dpi=300)
        #plt.close()


# In[ ]:

def plot_amp_ratio_hist2D_row(df, label="Data", channels=[5, 6, 7], bins=1000,
                              xlim=(0, 15), ylim=(0, 1200)):
    """
    Affiche un seul graphique avec une ligne de subplots 2D (un par canal) :
    X : ratio (q / max_amp) (en ADC)
    Y : max_amp (en mV)
    
    Avec :
    - 1 figure, len(channels) subplots en ligne
    - 1 colorbar par subplot
    - Axes X/Y personnalisables
    """
    nb_channels = len(channels)
    fig, axes = plt.subplots(1, nb_channels, figsize=(6 * nb_channels, 5), sharey=True)

    if nb_channels == 1:
        axes = [axes]  # uniformiser la boucle même avec un seul canal

    for i, ch in enumerate(channels):
        ax = axes[i]
        x = df[f"QT2T_{ch}_q"] / df[f"QT2T_{ch}_max_amp"]#.replace(0,np.nan)
        y = df[f"QT2T_{ch}_max_amp_mV"]

        h = ax.hist2d(
            x, y,
            bins=bins,
            range=[[xlim[0], xlim[1]], [ylim[0], ylim[1]]],
            cmap="viridis",
            norm=mcolors.LogNorm(vmin=1)
        )

        ax.set_title(f"{label} - Channel {ch}")
        ax.set_xlabel("q / max_amp (a.u.)")
        if i == 0:
            ax.set_ylabel("max_amp (mV)")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)

        # Colorbar propre à chaque subplot
        cbar = fig.colorbar(h[3], ax=ax, orientation='horizontal', pad=0.15)
        cbar.set_label("Number of events (log)")

        plt.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.9, wspace=0.3)



def plot_amp_ratio_hist2D(df, label="Data", channels=[5, 6, 7, "sum"], bins=1000,
                                      xlim=(0, 15), ylim=(0, 1200), rootfile='', save_dir=None, filename=None):
    """
    Pour chaque canal, affiche une figure contenant un histogramme 2D :
    X : ratio (q / max_amp) (en ADC)
    Y : max_amp (en mV)
    
    Avec :
    - Colorbar propre à chaque figure
    - Axes X/Y personnalisables
    """

    PMs = ["Opposite", "Close", "Bottom", "Sum"]
 
    for i, ch in enumerate(channels):
        x = df[f"QT2T_{ch}_q"] / df[f"QT2T_{ch}_max_amp"]
        y = df[f"QT2T_{ch}_max_amp_mV"]

        fig, ax = plt.subplots(figsize=(6, 5))

        h = ax.hist2d(x, y, bins=bins, range=[[xlim[0], xlim[1]], [ylim[0], ylim[1]]], cmap="viridis", norm=mcolors.LogNorm(vmin=1))
        if ch != "sum":
            ax.set_title(f"{label} - {PMs[i]}")
            ax.set_xlabel("Q / Amp  (a.u.)")
            ax.set_ylabel("Amp (mV)")
        else :
            ax.set_title(f"{label} - Sum")
            ax.set_xlabel("Q_tot / Amp_tot  (a.u.)")
            ax.set_ylabel("Amp_tot (mV)")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)

        cbar = fig.colorbar(h[3], ax=ax, label="Number of events (log)")

        plt.tight_layout()
        ax.text(0.7, -0.15, f"File: {rootfile}", fontsize=8, color='gray', ha='right', va='bottom', transform=ax.transAxes)

        # Sauvegarde avec suffixe spécifique au canal
        if save_dir and filename:
            os.makedirs(save_dir, exist_ok=True)
            suffix = f"_PM{ch}" if ch != "sum" else "_sum"
            full_path = os.path.join(save_dir, f"{filename}{suffix}.png")
            fig.savefig(full_path, dpi=300)





def split_in_sub_df(df, delta_t, show_sub_df = False, show_abstract = False, plot_rate_var = False, save_abstract = False, txt_to_show = '', save_dir=None, filename=None):
    """Découpe le dataframe fournit (df) en plusieurs dataframes (sub_df) par interval de temps delta_t en h. Un evenement de df se produisant 
    à un instant t est rangé dans le iéme sub_df ssi : t ∈ ] i×Δt ; (i+1)×Δt ] . 
    La fonction renvoie :
    - sub_df : liste des sous-dataframes (type = dictionnaire de pandas DataFrame)
    - durations : array contenant la durée totale de chaques sous-dataframes 
    - t_left_array : array contenant le 1er timestamp de chaques sous-dataframes 
    - rate : array contenant le rate moyen de chaque sous-dataframes

    Options :
    - show_sub_df = True : Montre le 1er, le 2em et le dernier sous-df contenue dans sub_df.
    - show_abstract = True : Résume dans un tableau les " Start , Stop, Events, Duration, Rate " de chaques sous-df.
    - plot_rate_var = True : Trace l'évolution temporelle du taux de déclenchement moyen. Chaque sous-df est représenté par une marche à 
      droite de largeur (t_n_sub_df - t_0_sub_df), placée à t = t_0_sub_df, et de hauteur = rate_sub_df. """

    t_start = df.iat[0,0]
    t_end   = df.iat[-1,0]

    t_min = df['group_time'].min()
    t_max = df['group_time'].max()

    tot_duration = t_max - t_min 
    
    # Verif que les 2 méthodes donnent la meme valeur
    if (t_min != t_start) :
        raise ValueError("Le premier group_time n'est pas le plus petit")

    if (t_max != t_end) :
        raise ValueError("Le dernier group_time n'est pas le plus grand") 
        
    print(f"First group event at : {t_start} ns = {t_start*10**-9} s = {(t_start*10**-9)/60} min \n"
          f"Last  group event at : {t_end} ns = {t_end*10**-9} s = {(t_end*10**-9)/60} min = {(t_end*10**-9)/3600} h")

    delta_t_ns = delta_t*3600*10**9 #ns
    
    #création des sous df
    sub_df = {}
    durations = [] #liste vide -> pas de taille à préciser
    #errors = []
    for i in range(0,1000):  # sub_df0: 0 < t ≤ delta_t_ns , sub_df1: delta_t_ns < t ≤ 2delta_t_ns , ...
        
        sub_df[i] = df[(df.group_time > i*delta_t_ns) & (df.group_time <= (i+1)*delta_t_ns)] # t ∈ ] i×Δt ; (i+1)×Δt ]

        t_firsts = sub_df[i].iat[0,0] #ns
        t_lasts = sub_df[i].iat[-1,0] #ns
        durations.append(t_lasts - t_firsts)  #ns
        """if durations[i] == 0 :
            raise ValueError(f"Division par zero pour {durations[i]}")
        errors.append(np.sqrt(len(sub_df[i]))/durations[i]) #"""
        
        if sub_df[i].iat[-1,0] == df.iat[-1,0]: #On s'arrete dés que le dernier evenement d'un sub_df a le
            break                               #meme time_stamp que le dernier evenement du df complet.sub_df = {}
     
    durations = np.array(durations)
    #errors = np.array(errors)

    nb_sub_df = len(sub_df)

    print(f"There is {nb_sub_df} sub_df in total")
    
    if show_sub_df == True:
        print(f"sub_df0 :\n{sub_df[0]}\nsub_df1 :\n{sub_df[1]}\nsub_df_{nb_sub_df-1} :\n{sub_df[nb_sub_df-1]}")
    

    t_left_arr = np.zeros(nb_sub_df) # Array pour le t_first de chaques sub_df
    t_right_arr = np.zeros(nb_sub_df) # Array pour le t_last de chaques sub_df
    rate = np.zeros(nb_sub_df) # Array pour le rates de chaques sub_df
    errors = np.zeros(nb_sub_df)    
    for i in range(nb_sub_df):
        
        t_first = sub_df[i].iat[0,0] #ns
        
        t_last = sub_df[i].iat[-1,0] #ns
        
        rate[i] = len(sub_df[i]) / (durations[i]*10**(-9)) #1/s

        errors[i] = np.sqrt(len(sub_df[i]))/(durations[i]*10**(-9))
        
        t_left_arr[i] = t_first*10**(-9)
        
        t_right_arr[i] = t_last*10**(-9)



    # x:9.4f permet d'afficher la valeur du float x avec un total de 10 caractéres (largeur du nombre avec ".")
    # et 4 chiffres aprés la virgule. Fixer la largeur d'un nombre dans le print permet d'avoir la virgule
    # toujours alignée verticalement avec celle du print suivant : /    0.8163/    
    #                                                              / 3600.6777/

    # en-tête 
    print(f"{'Name':<10} | {'Start [s]':>15} | {'Stop [s]':>15} | {'Events':>7} | {'Duration [s]':>12} | {'Rate [Hz]':>10} | {'Error':>10} |")
    print("-" * 100)
    # ligne complète
    print(f"{'Entire df':<10} | {df.iat[0,0]*1e-9:15.4f} | {df.iat[-1,0]*1e-9:15.4f} | {len(df):7d} | {tot_duration*1e-9:12.4f} | {len(df)/(tot_duration*1e-9):10.4f} | {np.sqrt(len(df))/(tot_duration*1e-9):10.4f} |")
    print("-" * 100)

    if show_abstract == True :
        # lignes des sous-df
        for i in range(len(sub_df)):
            print(f"{f'sub_df{i}':<10} | {t_left_arr[i]:15.4f} | {t_right_arr[i]:15.4f} | {len(sub_df[i]):7d} | {durations[i]*1e-9:12.4f} | {rate[i]:10.4f} | {errors[i]:10.4f} |")
    if save_abstract == True : 

        # === Construction du tableau principal ===
        rows = [{
            "Name": "Entire df",
            "Start [s]": df.iat[0,0]*1e-9,
            "Stop [s]": df.iat[-1,0]*1e-9,
            "Events": len(df),
            "Duration [s]": tot_duration*1e-9,
            "Rate [Hz]": len(df)/(tot_duration*1e-9),
            "Error": np.sqrt(len(df))/(tot_duration*1e-9)
        }]

        # Ajout des sous-tableaux si demandé
        if show_abstract:
            for i in range(len(sub_df)):
                rows.append({
                    "Name": f"sub_df{i}",
                    "Start [s]": t_left_arr[i],
                    "Stop [s]": t_right_arr[i],
                    "Events": len(sub_df[i]),
                    "Duration [s]": durations[i]*1e-9,
                    "Rate [Hz]": rate[i],
                    "Error": errors[i]
                })

        # === Conversion en DataFrame pandas ===
        table_df = pd.DataFrame(rows)

        # === Application d’un style pandas ===
        styled = (
            table_df.style
                .set_caption("Résumé des événements détectés")
                .format({
                    "Start [s]": "{:.4f}",
                    "Stop [s]": "{:.4f}",
                    "Duration [s]": "{:.4f}",
                    "Rate [Hz]": "{:.4f}",
                    "Error": "{:.4f}"
                })
                .set_properties(**{"text-align": "center"})
                .background_gradient(subset=["Rate [Hz]"], cmap="Greens")
                .highlight_max(subset=["Events"], color="lightgreen")
                .set_table_styles([
                    {"selector": "caption", "props": [("caption-side", "top"), ("font-size", "16px"), ("font-weight", "bold")]},
                    {"selector": "th", "props": [("background-color", "#dddddd"), ("text-align", "center")]}
                ])
        )

        # === Export en image PNG ===
        """dfi.export(styled, "event_summary.png")
        print(f"Tableau enregistré sous 'event_summary.png'")"""


    if plot_rate_var == True :

        plt.bar(t_left_arr/3600, rate, width=durations/(10**9*3600), align="edge", alpha=0.2, edgecolor="black")
        plt.step(t_left_arr/3600, rate, where="post")#,marker=".",color="red")
        plt.xlabel("Temps [h]")
        plt.ylabel("Rate [Hz]")
        plt.title(f"Évolution temporelle du taux de déclenchement moyen par pas de {delta_t} h")
        plt.text(0.2, -0.15, f"{txt_to_show}", transform=plt.gca().transAxes,
                 ha='right', va='bottom', fontsize=9, color='gray')
        #plt.text(1.0, -0.2, f"Average trigger rate : {rate:.4f} ± {errors:.4f} Hz over {durations/3600:.2f} h",fontsize=12,
        # ha='right', va='bottom')
        plt.grid()
        plt.show()    

        # Enregistrement
        if save_dir and filename:
            full_path = os.path.join(save_dir, f"{filename}.png")
            plt.savefig(full_path, dpi=300)
    
    return sub_df, durations, t_left_arr, rate





def split_in_sub_df_v2(df, delta_t, show_sub_df = False, show_abstract = False, plot_rate_var = False, save_abstract = False, txt_to_show = '', save_dir=None, filename=None):
    """Découpe le dataframe fournit (df) en plusieurs dataframes (sub_df) par interval de temps delta_t. Un evenement de df se produisant 
    à un instant t est rangé dans le iéme sub_df ssi : t ∈ ] i×Δt ; (i+1)×Δt ] . 
    La fonction renvoie :
    - sub_df : liste des sous-dataframes (type = dictionnaire de pandas DataFrame)
    - durations : array contenant la durée totale de chaques sous-dataframes 
    - t_left_array : array contenant le 1er timestamp de chaques sous-dataframes 
    - rate : array contenant le rate moyen de chaque sous-dataframes

    Options :
    - show_sub_df = True : Montre le 1er, le 2em et le dernier sous-df contenue dans sub_df.
    - show_abstract = True : Résume dans un tableau les " Start , Stop, Events, Duration, Rate " de chaques sous-df.
    - plot_rate_var = True : Trace l'évolution temporelle du taux de déclenchement moyen. Chaque sous-df est représenté par une marche à 
      droite de largeur (t_n_sub_df - t_0_sub_df), placée à t = t_0_sub_df, et de hauteur = rate_sub_df. """
    
    col_grt = df.columns.get_loc("group_time") #
    t_start = df.iat[0,col_grt]
    t_end   = df.iat[-1,col_grt] # df.at[-1,"group_time"] ne fonctionne pas ! Seul .iat prend les indices négatifs 
    
    t_min = df['group_time'].min()
    t_max = df['group_time'].max()

    tot_duration = t_max - t_min 
    """
    # Verif que les 2 méthodes donnent la meme valeur
    if (t_min != t_start) :
        raise ValueError("Le premier group_time n'est pas le plus petit")

    if (t_max != t_end) :
        raise ValueError("Le dernier group_time n'est pas le plus grand") 
    """    
    print(f"First group event at : {t_start} ns ~ {t_start*10**-9:.2f} s ~ {(t_start*10**-9)/60:.2f} min \n"
          f"Last  group event at : {t_end} ns ~ {t_end*10**-9:.2f} s ~ {(t_end*10**-9)/60:.2f} min ~ {(t_end*10**-9)/3600:.2f} h")

    delta_t_ns = delta_t*3600*10**9 #ns
    
    #création des sous df
    sub_df = {}
    t_firsts = []
    t_lasts = []
    nb_sub_evts = []
    durations = [] #liste vide -> pas de taille à préciser
    rates = []
    errors = []

    for i in range(0,1000):  # sub_df0: 0 < t ≤ delta_t_ns , sub_df1: delta_t_ns < t ≤ 2delta_t_ns , ...
        
        sub_df[i] = df[(df.group_time > i*delta_t_ns) & (df.group_time <= (i+1)*delta_t_ns)] #  t ∈ ] i×Δt ; (i+1)×Δt ]

        t_first = sub_df[i].iat[0,col_grt] #ns
        t_firsts.append(t_first)

        t_last = sub_df[i].iat[-1,col_grt] #ns
        t_lasts.append(t_last)

        nb_sub_evts.append(len(sub_df[i])) #int

        durations.append(t_last - t_first)  #ns

        rates.append(nb_sub_evts[i] / (durations[i])) #1/ns

        if durations[i] == 0 :
            raise ValueError(f"Division par zero dans le calcul de l'erreur pour le sub_df{i} car duration = 0")
        errors.append(np.sqrt(nb_sub_evts[i]) / durations[i]) # 1/ns
        
        if sub_df[i].iat[-1,col_grt] == df.iat[-1,col_grt]: #On s'arrete dés que le dernier evenement d'un sub_df a le
            break                               #meme time_stamp que le dernier evenement du df complet.sub_df = {}
     
    t_firsts    = np.array(t_firsts)*10**-9  #s 
    t_lasts     = np.array(t_lasts)*10**-9   #s
    nb_sub_evts = np.array(nb_sub_evts)
    durations   = np.array(durations)*10**-9 #s
    rates       = np.array(rates)*10**9      #1/s
    errors      = np.array(errors)*10**9     #1/s
    
    nb_sub_df = len(sub_df)

    print(f"There is {nb_sub_df} sub_df in total")
    
    if show_sub_df == True:
        print(f"sub_df0 :\n{sub_df[0]}\nsub_df1 :\n{sub_df[1]}\nsub_df_{nb_sub_df-1} :\n{sub_df[nb_sub_df-1]}")
    

    # x:9.4f permet d'afficher la valeur du float x avec un total de 10 caractéres (largeur du nombre avec ".")
    # et 4 chiffres aprés la virgule. Fixer la largeur d'un nombre dans le print permet d'avoir la virgule
    # toujours alignée verticalement avec celle du print suivant : /    0.8163/    
    #                                                              / 3600.6777/

    # en-tête 
    print(f"{'Name':<10} | {'Start [s]':>15} | {'Stop [s]':>15} | {'Events':>7} | {'Duration [s]':>12} | {'Rate [Hz]':>10} | {'Error':>10} |")
    print("-" * 100)
    # ligne du df entier
    print(f"{'Entire df':<10} | {df.iat[0,col_grt]*1e-9:15.4f} | {df.iat[-1,col_grt]*1e-9:15.4f} | {len(df):7d} | {tot_duration*1e-9:12.4f} | {len(df)/(tot_duration*1e-9):10.4f} | {np.sqrt(len(df))/(tot_duration*1e-9):10.4f} |")
    print("-" * 100)

    if show_abstract == True :
        # lignes des sous-df
        for i in range(len(sub_df)):
            print(f"{f'sub_df{i}':<10} | {t_firsts[i]:15.4f} | {t_lasts[i]:15.4f} | {nb_sub_evts[i]:7d} | {durations[i]:12.4f} | {rates[i]:10.4f} | {errors[i]:10.4f} |")
    if save_abstract == True : 

        # === Construction du tableau principal ===
        rows = [{
            "Name": "Entire df",
            "Start [s]": df.iat[0,col_grt]*1e-9,
            "Stop [s]": df.iat[-1,col_grt]*1e-9,
            "Events": len(df),
            "Duration [s]": tot_duration*1e-9,
            "Rate [Hz]": len(df)/(tot_duration*1e-9),
            "Error": np.sqrt(len(df))/(tot_duration*1e-9)
        }]

        # Ajout des sous-tableaux si demandé
        if show_abstract:
            for i in range(len(sub_df)):
                rows.append({
                    "Name": f"sub_df{i}",
                    "Start [s]": t_first[i],
                    "Stop [s]": t_lasts[i],
                    "Events": nb_sub_evts[i],
                    "Duration [s]": durations[i],
                    "Rate [Hz]": rates[i],
                    "Error": errors[i]
                })

        # === Conversion en DataFrame pandas ===
        table_df = pd.DataFrame(rows)

        # === Application d’un style pandas ===
        styled = (
            table_df.style
                .set_caption("Résumé des événements détectés")
                .format({
                    "Start [s]": "{:.4f}",
                    "Stop [s]": "{:.4f}",
                    "Duration [s]": "{:.4f}",
                    "Rate [Hz]": "{:.4f}",
                    "Error": "{:.4f}"
                })
                .set_properties(**{"text-align": "center"})
                .background_gradient(subset=["Rate [Hz]"], cmap="Greens")
                .highlight_max(subset=["Events"], color="lightgreen")
                .set_table_styles([
                    {"selector": "caption", "props": [("caption-side", "top"), ("font-size", "16px"), ("font-weight", "bold")]},
                    {"selector": "th", "props": [("background-color", "#dddddd"), ("text-align", "center")]}
                ])
        )

        # === Export en image PNG ===
        """dfi.export(styled, "event_summary.png")
        print(f"Tableau enregistré sous 'event_summary.png'")"""


    if plot_rate_var == True :
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.bar(t_firsts/3600, rates, width=durations/3600, align="edge", alpha=0.2, edgecolor="black")
        plt.step(t_firsts/3600, rates, where="post")#,marker=".",color="red")
        plt.xlabel("Temps [h]")
        plt.ylabel("Rate [Hz]")
        plt.title(f"Évolution temporelle du taux de déclenchement moyen par pas de {delta_t} h")
        plt.text(0.2, -0.15, f"{txt_to_show}", transform=plt.gca().transAxes,
                 ha='right', va='bottom', fontsize=9, color='gray')
        #plt.text(1.0, -0.2, f"Average trigger rate : {rate:.4f} ± {errors:.4f} Hz over {durations/3600:.2f} h",fontsize=12,
        # ha='right', va='bottom')
        plt.grid()
        plt.show()    

        # Enregistrement
        if save_dir and filename:
            full_path = os.path.join(save_dir, f"{filename}.png")
            fig.savefig(full_path, dpi=300)
    
    return sub_df, durations, t_firsts, rates





