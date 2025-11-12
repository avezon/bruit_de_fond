//  std includes
#include <stdio.h>
#include <stdlib.h>
#include <string.h> // pour memcpy
#include <string>
#include <vector>

//  root includes
#include "TFile.h"
#include "TTree.h"
#include "TH1.h"

//  fasterac includes
extern "C" {
#include "fasterac/fasterac.h"
#include "fasterac/group.h"
#include "fasterac/qdc.h"
#include "fasterac/qt2t.h"
#include "fasterac/utils.h"
}

#define ROOTFILENAME ""

const Double_t NO_DATA = -999999.0;


int main(int argc, char* argv[]) {

    // Récupération du nom des fichiers et vérif
    
    if (argc != 3){
        fprintf(stderr,"Faster2root require 2 arguments, one for the input faster file and the other for the output \
root file \n Exemple: ./Faster2root Faster_file_0001.fast Root_file.root \n");
        return EXIT_FAILURE;
    }
    
    const char* input_filename  = argv[1];  // .fast en argument 1
    const char* output_filename = argv[2];  // .root en argument 2


    // Ouverture du fichier .fast
    faster_file_reader_p reader = faster_file_reader_open(input_filename);
    if (!reader) {
        fprintf(stderr, "Erreur : impossible d'ouvrir le fichier %s\n", input_filename);
        return EXIT_FAILURE;
    }

    // Création du fichier .root    
    TFile* root_file = new TFile(output_filename, "RECREATE");
    if (root_file->IsZombie()) {
        fprintf(stderr, "Erreur : impossible de créer le fichier ROOT %s\n", output_filename);
        return EXIT_FAILURE;
    }


    // Déclaration et initialisation des variables

    //Pour type group
    Long64_t group_time = NO_DATA;
    Long64_t group_data_nb = NO_DATA;
    Int_t group_size = NO_DATA;
    Long64_t data_counter = 0;// compteur global des enregistrements "data" dans le fichier .fast

    //Pour les sous-événements :
    //pour tous les types de sous evenement
    Double_t sub_time = NO_DATA;
    Int_t sub_channel = NO_DATA;
    Int_t sub_type = NO_DATA;
    Char_t sub_type_string[8] = "";
    Int_t sub_num = 0;
    //pour type QDC_X1 et QDC_X2 (resp. un et deux intervals d'intégration de charge)
    Int_t sub_q1 = NO_DATA, sub_q2 = NO_DATA;
    Bool_t sub_q1_sat = false, sub_q2_sat = false;
    //pour type QT2T 
    Int_t sub_Q = NO_DATA;
    Int_t sub_width = NO_DATA;
    Int_t sub_max_amp = NO_DATA;
    Int_t sub_max_pos = NO_DATA;
    Int_t sub_baseline = NO_DATA;
    Bool_t sub_sat = false;

    //pour les pointeurs et les var. de faster
    faster_data_p data;
    faster_buffer_reader_p group_reader;
    void* group_buffer;
    unsigned short lsize;
    faster_data_p group_data;
    qdc_x1 qdcx1;  //
    qdc_x2 qdcx2;  //--> On peux aussi definir ces pointeurs seulement à la détection du TYPE_ALIAS
    qt2t qt;       //

    // Définir le TTree et ses Branches à remplir
    TTree *t = new TTree("DataTree", "Group events");
 
    t->Branch("group_data_nb", &group_data_nb);  // Les &var1, &var2, ... sont les emplacements mémoire
    t->Branch("group_size", &group_size);        // associés aux variables var1, var2, ... ! Dés que var
    t->Branch("group_time", &group_time);        // se voit attribué une valeur, celle-ci est récupérable
                                                 // à l'emplacement &var
    
    t->Branch("sub_num", &sub_num);
    t->Branch("sub_time", &sub_time);           
    t->Branch("sub_type", sub_type_string, "sub_type/C"); //Pas de & devant (c’est déjà une adresse), le format /C indique à ROOT que c’est une chaîne de caractères C (char[]).
    t->Branch("sub_channel", &sub_channel);
    
    t->Branch("sub_Q", &sub_Q);
    t->Branch("sub_width", &sub_width);
    t->Branch("sub_max_amp", &sub_max_amp);
    t->Branch("sub_max_pos", &sub_max_pos);
    t->Branch("sub_baseline", &sub_baseline);
    t->Branch("sub_sat", &sub_sat);

    t->Branch("sub_q1", &sub_q1);
    t->Branch("sub_q1_sat", &sub_q1_sat);
    t->Branch("sub_q2", &sub_q2);
    t->Branch("sub_q2_sat", &sub_q2_sat);

    //Parcours des événements dans le fichier .fast ouvert tant que le suivant est non vide
    while ((data = faster_file_reader_next(reader)) != NULL) {

        // incrementation du compteur global pour TOUT les evenements 
        data_counter++;

        if (faster_data_type_alias(data) != GROUP_TYPE_ALIAS) continue; //continue nous fait passer directement à l'itération suivante de while sans faire tout ce qu'il y a en dessous.
        group_buffer = faster_data_load_p(data);                        // "The continue statement breaks one iteration (in the loop), if a specified condition occurs, and continues with the next iteration in the loop."
        group_size = faster_data_load_size(data); //j'ai remplacé le nom "lsize" par "group_size".On le lit maintenant car on a besoin de sa valeur pour ouvrir le buffer. Mais on le re-lirat dans la boucle des sub-events car on le veux à CHAQUES lignes. 
        group_reader = faster_buffer_reader_open(group_buffer, group_size);

        sub_num = 0; //RAZ du compteur de sous-evenements

        //Parcours des sous-événements dans le group/buffer ouvert tant que le suivant est non vide
        while ((group_data = faster_buffer_reader_next(group_reader)) != NULL) {

            unsigned short label = faster_data_label(group_data); //faster_data_label dans le buffer nous donne le channel ! 
            unsigned char alias = faster_data_type_alias(group_data);
            group_time = faster_data_clock_ns(data); 
            group_data_nb = data_counter - 1; //Dans Faster le 1er evenement est n°0 mais je doit incrémenter le counter avant de lire sa valeur (car on veut ajouter 1 à chaque event). Donc sans le -1 le 1er evenement serait n°1.

            // Initialisation pour ce sous-événement
            sub_time = faster_data_clock_ns(group_data) - group_time; // temps relatif
            sub_channel = label;
            sub_type = alias;
            
            // Incrémentation du numéro d'événement au sein du groupe
            sub_num ++;

            // RAZ
            strcpy(sub_type_string, "");
            sub_q1 = sub_q2 = NO_DATA;
            sub_q1_sat = sub_q2_sat = sub_sat = false;
            sub_Q = sub_width = sub_max_amp = sub_max_pos = sub_baseline = NO_DATA;

            // Décodage selon le type

            if (alias == QDC_X1_TYPE_ALIAS) {
                //qdc_x1 qdcx1;
                memcpy(&qdcx1, faster_data_load_p(group_data), sizeof(qdc_x1));
		        strcpy(sub_type_string, "QDC_X1");
                sub_q1 = qdcx1.q1;
                sub_q1_sat = qdcx1.q1_saturated;
            }
            else if (alias == QDC_X2_TYPE_ALIAS) {
                //qdc_x2 qdcx2;
                memcpy(&qdcx2, faster_data_load_p(group_data), sizeof(qdc_x2));
		        strcpy(sub_type_string, "QDC_X2");
                sub_q1 = qdcx2.q1;
                sub_q2 = qdcx2.q2;
                sub_q1_sat = qdcx2.q1_saturated;
                sub_q2_sat = qdcx2.q2_saturated;
            }
            else if (alias == QT2T_TYPE_ALIAS) {
                //qt2t qt;
                memcpy(&qt, faster_data_load_p(group_data), sizeof(qt2t));
		        strcpy(sub_type_string, "QT2T");
                sub_Q = qt.q;
                sub_width = qt.w;
                sub_max_amp = qt.a_max;
                sub_max_pos = qt.t_max;
                sub_baseline = qt.q_baseline;
                sub_sat = qt.saturated;
            }
            else {
                // Types non traités
                continue;
            }

        t->Fill();// C'est ici que toutes les valeurs stockées dans les var sont ajoutées au TTree !
        }
        faster_buffer_reader_close(group_reader);
        
    }    
    // Sauvegarde
    faster_file_reader_close(reader);
    root_file->Write();
    root_file->Close();
    return EXIT_SUCCESS;
}

