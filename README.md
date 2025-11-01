Ces programmes permettent de convertir les fichiers **.fast** en fichiers **.root**, puis d’analyser ces données sous forme de **DataFrames pandas** dans Python.

Les données d’acquisition ont été obtenues à l’aide d’un détecteur **GADGET**, équipé de deux scintillateurs plastiques juxtaposés au-dessus de sa fenêtre d’entrée. Les signaux des trois photomultiplicateurs (PMT) de GADGET, désignés par **Opposite**, **Close** et **Bottom**, sont lus par un système d’acquisition **FASTER** en mode **QT2T**, respectivement sur les canaux **5**, **6** et **7**. L’acquisition des signaux des scintillateurs plastiques est réalisée sur ce même système, via les canaux **2** et **4**.

Outils de lecture des fichiers .fast et .root:
fasterac/fasterac.h         TFile.h
fasterac/group.h            TTree.h
fasterac/qdc.h              
fasterac/qt2t.h
fasterac/utils.h

Outils d'analyses Python:
os
numpy
pandas
uproot
matplotlib (.cm, .colors, .path, .collections)
