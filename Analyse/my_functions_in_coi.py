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

Adc_to_mV = 0.29175


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


def plot_amp_ratio_hist2D(df, no_sat = False, label="Data", channels=[5, 6, 7, "sum"], PMT = ["Opposite", "Close", "Bottom"], bins=1000,
                            xlim=(0, 15), ylim=(0, 1200), show_mean = False, txt_to_show = "", save_dir=None, filename=None):
    """
    Pour chaque canal, affiche une figure contenant un histogramme 2D :
    X : ratio (q / max_amp) (en ADC)
    Y : max_amp (en mV)

    Avec :
    - Colorbar propre à chaque figure
    - Axes X/Y personnalisables 
    """
    
    #data2 = pd.DataFrame(columns=['x_f2r_5', 'x_f2r_6','x_f2r_7', 'x_f2r_sum', 'y_f2r_5', 'y_f2r_6', 'y_f2r_7', 'y_f2r_sum'])
    
    bins_initial_value = bins    

    if no_sat == True:
        df = df.query("sub_sat == False")    
    for i, ch in enumerate(channels):
  
        fig, ax = plt.subplots(figsize=(6, 5))
        #print(f"i={i}, ch={ch}")
        if ch != "sum":
            #print("in if")
            df_ch = df.query("sub_channel == @ch")
            #print(f"df_ch={df_ch}")
            ax.set_title(f"{label} - {PMT[i]} (channel {ch})")
            ax.set_xlabel("Q / Amp  [a.u.]")
            ax.set_ylabel("Amp  [mV]")

            x = (df_ch["sub_Q"] / df_ch["sub_max_amp"]).reset_index(drop=True)
            #print(f"x={x}")
            
            y = (df_ch["sub_max_amp"]*Adc_to_mV).reset_index(drop=True)

            if bins_initial_value == 'sqrt':
                bins = round(np.sqrt(len(df_ch)))
                print(f'sqrt rule give nb of bins = {bins}\n')

            #print(f"y={y}")
            #
            #data2[f'x_f2r_{ch}']=x
            #data2[f'y_f2r_{ch}']=y
            #
        else :
            df=df.query("sub_type == 'QT2T'")
            sub_Q_sum = df.groupby('group_time')['sub_Q'].sum().reset_index() #necessaire #il n'y a rien qui empéche la somme de parcourir les QDC !!!!!!
            #print(f"sub_Q_sum={sub_Q_sum}")
            sub_max_amp_sum = df.groupby('group_time')['sub_max_amp'].sum().reset_index()  #necessaire
            #print(f"sub_max_amp={sub_max_amp_sum}")
            sub_ratio_sum = (sub_Q_sum.sub_Q / sub_max_amp_sum.sub_max_amp).reset_index(drop=True)
            x = sub_ratio_sum
            y = (sub_max_amp_sum.sub_max_amp*Adc_to_mV).reset_index(drop=True) 

            if bins_initial_value == 'sqrt':
                bins = round(np.sqrt(len(df["group_data_nb"].unique()))) #Dans le cas de "sum", comme df n'est pas filtré par un channel, il faut utiliser len(df["group_data_nb"].unique())
                print(f'sqrt rule give nb of bins = {bins}\n')



            #print(f"x=sub_ratio_sum={x}")
            #print(f"y={y}")
            
            #
            #data2[f'x_f2r_{ch}']=x
            #data2[f'y_f2r_{ch}']=y
            #

            ax.set_title(f"{label} - Sum")
            ax.set_xlabel("Q_tot / Amp_tot  [a.u.]")
            ax.set_ylabel("Amp_tot  [mV]")

        h = ax.hist2d(x, y, bins=bins, range=[[xlim[0], xlim[1]], [ylim[0], ylim[1]]], cmap="viridis", norm=mcolors.LogNorm(vmin=1))
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, which="both", axis='y', linestyle='--', linewidth=0.5, alpha=0.5)

        cbar = fig.colorbar(h[3], ax=ax, label="Number of events (log)")
        
        if show_mean:
            x_mean, y_mean , x_std, y_std = PSA_stat(df)
            plt.scatter(x_mean, y_mean, color="red", s=80, label="Mean")
            plt.text(x_mean-0.8, y_mean+10, f'[{x_mean:.1f} , {y_mean:.1f}]',color = "black", fontsize=7, fontweight=1000)

        plt.tight_layout()
    
        plt.text(1, -0.2, f"{txt_to_show}", transform=plt.gca().transAxes,
                 ha='right', va='bottom', fontsize=9, color='gray')

        #Affichage du rate et de l'erreur asssociée
        time_start = df['group_time'].min()
        time_end = df['group_time'].max()
        duration_s = (time_end - time_start) * 1e-9  # convertit ns en secondes
        count = len(df["group_data_nb"].unique())
        rate = count / duration_s
        rate_error = np.sqrt(count) / duration_s
        plt.text(xlim[1]-95/100*xlim[1], ylim[1]-10/100*ylim[1], f"Average rate on ~{duration_s/3600:.1f} h\nR = {rate:.2f} ± {rate_error:.2f}Hz",fontsize=10,
         ha='left', va='bottom', bbox=dict(facecolor='white', alpha=0.2, edgecolor='black', boxstyle='square'))
        plt.text(0.6, -0.2, f"{txt_to_show}", fontsize=8, color='gray', 
                    ha='right', va='bottom', transform=ax.transAxes)
        
        # Sauvegarde avec suffixe spécifique au canal
        if save_dir and filename:
            os.makedirs(save_dir, exist_ok=True)
            suffix = f"_PM{ch}" if ch != "sum" else "_sum"
            full_path = os.path.join(save_dir, f"{filename}{suffix}.png")
            fig.savefig(full_path, dpi=300)

        plt.show()
      
    return #data2

def channel_population(df, disp_percentage = True, show_abstract = True):
    
    #data=np.array(df['sub_channel']) # All commented code contain the "np.histogram()" version of this function 
    len_data = len(df)
    ch_pop = df['sub_channel'].value_counts() #We can use .value_counts() to get the nb of items instead of using count from np.histogram()
    ch_pop.sort_index(inplace=True)
    print(f'Series of channels population (obtain with .value_counts()): \n {ch_pop}')
    
    #count_and_bin = np.histogram(data,bins=16,range=(1,17)) # np.histogram() is what plt.hist() use to produce count and bin but plotting is not mandatory with the np one. 
    #ch_pop = count_and_bin[0].astype(int)
    
    if disp_percentage == True:
        ch_pop_plot = ch_pop/len_data*100
    else: ch_pop_plot = ch_pop

    print(f'We have a total of {len_data} events distributed in 12 channels as follow')

    #Harvesting the countings from ch_pop for each detectors 
    Det_1=[ch_pop_plot[1], ch_pop_plot[2], ch_pop_plot[3]]
    Det_2=[ch_pop_plot[5], ch_pop_plot[6], ch_pop_plot[7]]
    Det_3=[ch_pop_plot[9], ch_pop_plot[10], ch_pop_plot[11]]
    Det_4=[ch_pop_plot[13], ch_pop_plot[14], ch_pop_plot[15]]
    #Det_1 = [ch_pop_plot[i] for i in range(3)]
    #Det_2 = [ch_pop_plot[i] for i in range(4,7)]
    #Det_3 = [ch_pop_plot[i] for i in range(8,11)]
    #Det_4 = [ch_pop_plot[i] for i in range(12,15)]
    print(f'1: {Det_1}\n2: {Det_2}\n3: {Det_3}\n4: {Det_4}')

    if show_abstract == True :
        # Liste des canaux associés à chaque détecteur
        channels = {
            1: [1, 2, 3], 
            2: [5, 6, 7],  
            3: [9, 10, 11], 
            4: [13, 14, 15]}
        colors = ['Red','Blue','Yellow','White']
        print(f'We have a total of {len_data} events distributed in 12 channels as follow')
        # En-tête
        print( "-"*67)  
        print(f"| {'Name':<14} | {'Channel':<8} | {'Count':>15} | {'Percentage':>17} |")
        # Lignes pour chaque détecteur
        for det_num, det in enumerate([Det_1, Det_2, Det_3, Det_4], start=1):
            print( "-"*67) 
            for j, value in enumerate(det):
                channel = channels[det_num][j]
                percentage = (value / len_data) * 100
                print(f"| {f'Det_{det_num} ({colors[det_num-1]})':<14} | {channel:<8} | {ch_pop[channel]:15.0f} | {ch_pop[channel]/len_data*100:15.2f} % |")
        print( "-"*67) 

    #Making the bar plot for each channel and gathered them by Detector:
    plt.bar([1,2,3] ,Det_1,width=1,align="center",label='RED_GADGET',color='red',edgecolor="black")
    plt.bar([5,6,7] ,Det_2,width=1,align="center",label='BLUE_GADGET',color= 'blue',edgecolor="black")
    plt.bar([9,10,11],Det_3,width=1,align="center",label='YELLOW_GADGET',color='yellow',edgecolor="black")
    plt.bar([13,14,15],Det_4,width=1,align="center",label='WHITE_GADGET',color='grey',edgecolor="black")
    plt.legend()
    plt.xlabel("Channels")
    if disp_percentage == True:
        plt.ylabel("Fraction of the complete dataset [%]")
    else : 
        plt.ylabel("Count")    
    plt.grid(axis='y')
    plt.xticks([1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15])
    plt.show()
    return Det_1, Det_2, Det_3, Det_4


def set_detectors_channels(df, ch_RED = [1,2,3], ch_BLUE = [5,6,7], ch_YELLOW = [9,10,11], ch_WHITE = [13,14,15]):
    """This function work with df containing a column "sub_channel" listing the channel number of each events.
    It returns 4 df_COLOR containing only events with channels belonging to a given ch_COLOR list of 3 channels.
    A line array containing 
    """
    ch_arr = np.array([ch_RED, ch_BLUE, ch_YELLOW, ch_WHITE])

    df_RED = df.query("sub_channel == @ch_RED[0] | sub_channel == @ch_RED[1] | sub_channel == @ch_RED[2]")

    df_BLUE = df.query("sub_channel == @ch_BLUE[0] | sub_channel == @ch_BLUE[1] | sub_channel == @ch_BLUE[2]")

    df_YELLOW = df.query("sub_channel == @ch_YELLOW[0] | sub_channel == @ch_YELLOW[1] | sub_channel == @ch_YELLOW[2]")

    df_WHITE = df.query("sub_channel == @ch_WHITE[0] | sub_channel == @ch_WHITE[1] | sub_channel == @ch_WHITE[2]")

    return(df_RED, df_BLUE, df_YELLOW, df_WHITE, ch_arr)



def PSA_stat(df, Adc_to_mV = 0.29175, show_details = False):
    
    #Adding charge (resp. max amp) from the same coincidence group
    Q_sum = df.groupby('group_time')['sub_Q'].sum().reset_index()
    A_sum = df.groupby('group_time')['sub_max_amp'].sum().reset_index()
    
    if len(Q_sum) != len(A_sum):
        raise ValueError(f"Mismatch in the number of coincidence groups between sub_Q and sub_max_amp:"
                         f"\n{len(Q_sum)} for sub_Q ≠ {len(A_sum)} for sub_max_amp")
    if A_sum['sub_max_amp'].argmin() == 0:
        raise ValueError(f"The series of summed sub_max_amp by coi group contains (at least) a zero.")
        
    #Element wise division of charges series by amp series
    ratio_QA = Q_sum['sub_Q']/A_sum['sub_max_amp']
    
    mean_QA = ratio_QA.mean()
    std_QA = ratio_QA.std()
    
    A_sum_mV = A_sum['sub_max_amp']*Adc_to_mV
    
    mean_A_mV = A_sum_mV.mean()
    std_A_mV = A_sum_mV.std()
    
    if show_details:
        print(f"Q_sum :\n{Q_sum}\n\nA_sum :\n{A_sum}\n\nratio_QA :\n{ratio_QA}\n\nA_sum_mV :\n{A_sum_mV}\n")
        
    return(mean_QA, mean_A_mV, std_QA, std_A_mV)



def box_cut(df, lower_QA = 5, upper_QA = 10, lower_max_amp_mV = 30, upper_max_amp_mV = 200, Adc_to_mV = 0.29175):
    
    df=df.query("sub_type == 'QT2T'")
    
    # 1. Getting charge sum on each coincidence group (and their assocated 'group_time')
    
    coi_Q_sum = df.groupby('group_time')['sub_Q'].sum().reset_index() 
    
    print(f"coi_Q_sum =\n {coi_Q_sum}")
    
    
    # 2. Getting maximum amplitude sum on each coincidence group (and their assocated 'group_time')
    
    coi_max_amp_sum = df.groupby('group_time')['sub_max_amp'].sum().reset_index()  
    
    print(f"coi_max_amp_sum =\n {coi_max_amp_sum}")
    
     
    # 3. Merging coi_Q_sum and coi_max_amp_sum in one df according to their 'group_time'
    
    coi_data = pd.merge(coi_Q_sum, coi_max_amp_sum, on='group_time', suffixes=('_Q', '_max_amp'))
    
    print(f"coi_data =\n {coi_data}")
    
    
    # 4. Computing sub_QA and adding it as a new column of coi_data df
    
    coi_data['sub_QA'] = coi_data['sub_Q'] / coi_data['sub_max_amp']
    
    print(f"coi_data =\n {coi_data}")
    

    # 5. Keeping only coi events with sub_QA ∈ [lower_QA, upper_QA] & sub_max_amp ∈ [lower_max_amp, upper_max_amp]
    
    coi_data_cut = coi_data.query("sub_QA > @lower_QA  &  sub_QA < @upper_QA  &  sub_max_amp*@Adc_to_mV > @lower_max_amp_mV"
                                  "&  sub_max_amp*@Adc_to_mV < @upper_max_amp_mV")

    print(f"coi_data_cut =\n {coi_data_cut}")

    print(coi_data_cut["sub_max_amp"].max()*Adc_to_mV) #to check if we steal have values > upper_max_amp
    
    # 6. Extracting remaning group_time after cutting

    group_time_values = coi_data_cut['group_time']

    # 7. Keeping only events with the extrated group_time
    df_cutted = df[df['group_time'].isin(group_time_values)]
    
    return(df_cutted) 


