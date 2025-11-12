#Importation des modules
import os  # Module pour manipuler les chemins de fichiers
import glob  # Module pour lister les fichiers dans un dossier (utilisé pour trouver automatiquement les fichiers FASTER).

#Definition des chemins

FASTER_DIR = "data/faster/" 
ROOT_F2R_DIR = "data/root/faster2root/"
ROOT_G2T_DIR = "data/root/group2tree_v3/"

#Definiton des type de fichier (extensions)

FASTER_EXT = ".fast"
ROOT_EXT = ".root"

#Liste de fichiers faster

faster_files = glob.glob(f"{FASTER_DIR}*{FASTER_EXT}")


#Création des chemins virtuels vers les futurs fichiers root associés à chaques fichiers faster 

rule all:
    input:
        #Fichiers générés par mon_group2tree_v3
        expand("{root_dir}{faster_name}{root_ext}",
               root_dir=ROOT_G2T_DIR,
               faster_name=[os.path.basename(f).replace(FASTER_EXT, "") for f in faster_files],
               root_ext=ROOT_EXT),

        #Fichiers générés par Faster2root
        expand("{root_dir}{faster_name}{root_ext}",
               root_dir=ROOT_F2R_DIR,
               faster_name=[os.path.basename(f).replace(FASTER_EXT, "") for f in faster_files],
               root_ext=ROOT_EXT)

#Application de mon_group2tree_v3 et de Faster2root pour créer les fichiers root aux emplacements prévues 

#Règle pour mon_group2tree_v3:

rule convert_with_root2tree:
    input:
        faster_file = FASTER_DIR + "{faster_name}" + FASTER_EXT
    output:
        root_file = ROOT_G2T_DIR + "{faster_name}" + ROOT_EXT
    shell:
        """
        ./conversion/mon_group2tree_v3 {input.faster_file} {output.root_file}
        """

# Règle pour Faster2root:

rule convert_with_faster2root:
    input:
        faster_file = FASTER_DIR + "{faster_name}" + FASTER_EXT
    output:
        root_file = ROOT_F2R_DIR + "{faster_name}" + ROOT_EXT
    shell:
        """
        ./conversion/Faster2root {input.faster_file} {output.root_file}
        """
