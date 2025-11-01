
//  std includes
#include <stdio.h>
#include <stdlib.h>
#include <string.h> // pour memcpy

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

//#define DATAFILENAME "Test_GADGET_GorG2orG4orG24_0001.fast"
#define ROOTFILENAME "GADGET_coind_all.root"
#define NO_DATA -999999




int main(int argc, char* argv[]) {

    // Récupérations des noms fichiers et vérif
    
    if (argc != 3){
        fprintf(stderr,"mon_group2tree require 2 arguments, one for the input faster file and the other for the output \
root file \n Exemple: ./mon_group2tree Faster_file_0001.fast Root_file.root \n");
        return EXIT_FAILURE;
    }
    
    const char* input_filename  = argv[1];  // .fast en argument 1
    const char* output_filename = argv[2];  // .root en argument 2


    // Ouvrir le fichier .fast
    faster_file_reader_p reader = faster_file_reader_open(input_filename);
    if (!reader) {
        fprintf(stderr, "Erreur : impossible d'ouvrir le fichier %s\n", input_filename);
        return EXIT_FAILURE;
    }

    // Créer le fichier ROOT
    
    TFile* root_file = new TFile(output_filename, "RECREATE");
    if (root_file->IsZombie()) {
        fprintf(stderr, "Erreur : impossible de créer le fichier ROOT %s\n", output_filename);
        return EXIT_FAILURE;
    }


    faster_data_p data;
    faster_buffer_reader_p group_reader;
    void* group_buffer;
    unsigned short lsize;
    faster_data_p group_data;

    qdc_x2 qdc;

    qt2t qt;


    int enter_if;
    enter_if = 0;

    TTree* tree = new TTree("DataTree", "Group-only FASTER data");

    Int_t qdc_2_q1, qdc_2_q2, qdc_2_q3, qdc_2_q4;
    Int_t qdc_4_q1, qdc_4_q2, qdc_4_q3, qdc_4_q4;
    Bool_t qdc_2_q1_saturated, qdc_2_q2_saturated, qdc_2_q3_saturated, qdc_2_q4_saturated;
    Bool_t qdc_4_q1_saturated, qdc_4_q2_saturated, qdc_4_q3_saturated, qdc_4_q4_saturated;

    Int_t qt2t_5_q, qt2t_6_q, qt2t_7_q;
    Int_t qt2t_5_width, qt2t_6_width, qt2t_7_width;
    Int_t qt2t_5_max_ampl, qt2t_6_max_ampl, qt2t_7_max_ampl;
    Double_t qt2t_5_max_pos, qt2t_6_max_pos, qt2t_7_max_pos;
    Int_t qt2t_5_q_baseline, qt2t_6_q_baseline, qt2t_7_q_baseline;
    Bool_t qt2t_5_saturated, qt2t_6_saturated, qt2t_7_saturated;
    Double_t group_time;

    Int_t counter_2;
    Int_t counter_4;
    Int_t counter_5;
    Int_t counter_6;
    Int_t counter_7;
    Int_t counter_mult_2;
    Int_t counter_mult_4;
    Int_t counter_mult_5;
    Int_t counter_mult_6;
    Int_t counter_mult_7;
    



    tree->Branch("group_time", &group_time, "group_time/D");
    
    tree->Branch("QDC_2", &qdc_2_q1);
    tree->Branch("QDC_4", &qdc_4_q1);
    tree->Branch("QDC_2_sat", &qdc_2_q1_saturated);
    tree->Branch("QDC_4_sat", &qdc_4_q1_saturated);
    tree->Branch("QDC_2_q2", &qdc_2_q2);
    tree->Branch("QDC_4_q2", &qdc_4_q2);        
    tree->Branch("QDC_2_q2_sat", &qdc_2_q2_saturated);
    tree->Branch("QDC_4_q2_sat", &qdc_4_q2_saturated);

    tree->Branch("QT2T_5_q", &qt2t_5_q, "QT2T_5_q/I");
    tree->Branch("QT2T_6_q", &qt2t_6_q, "QT2T_6_q/I");
    tree->Branch("QT2T_7_q", &qt2t_7_q, "QT2T_7_q/I");
    tree->Branch("QT2T_5_width", &qt2t_5_width, "QT2T_5_width/I");
    tree->Branch("QT2T_6_width", &qt2t_6_width, "QT2T_6_width/I");
    tree->Branch("QT2T_7_width", &qt2t_7_width, "QT2T_7_width/I");
    tree->Branch("QT2T_5_max_amp", &qt2t_5_max_ampl, "QT2T_5_max_amp/I");
    tree->Branch("QT2T_6_max_amp", &qt2t_6_max_ampl, "QT2T_6_max_amp/I");
    tree->Branch("QT2T_7_max_amp", &qt2t_7_max_ampl, "QT2T_7_max_amp/I");
    tree->Branch("QT2T_5_max_pos", &qt2t_5_max_pos, "QT2T_5_max_pos/D");
    tree->Branch("QT2T_6_max_pos", &qt2t_6_max_pos, "QT2T_6_max_pos/D");
    tree->Branch("QT2T_7_max_pos", &qt2t_7_max_pos, "QT2T_7_max_pos/D");
    tree->Branch("QT2T_5_q_base_line", &qt2t_5_q_baseline, "QT2T_5_q_base_line/I");
    tree->Branch("QT2T_6_q_base_line", &qt2t_6_q_baseline, "QT2T_6_q_base_line/I");
    tree->Branch("QT2T_7_q_base_line", &qt2t_7_q_baseline, "QT2T_7_q_base_line/I");
    tree->Branch("QT2T_5_sat", &qt2t_5_saturated, "QT2T_5_saturated/O");
    tree->Branch("QT2T_6_sat", &qt2t_6_saturated, "QT2T_6_saturated/O");
    tree->Branch("QT2T_7_sat", &qt2t_7_saturated, "QT2T_7_saturated/O");

    tree->Branch("Counter_2", &counter_2, "Counter_2/I");
    tree->Branch("Counter_4", &counter_4, "Counter_4/I");
    tree->Branch("Counter_5", &counter_5, "Counter_5/I");
    tree->Branch("Counter_6", &counter_6, "Counter_6/I");
    tree->Branch("Counter_7", &counter_7, "Counter_7/I");

    tree->Branch("Counter_mult_2", &counter_mult_2, "Counter_mult_2/I");
    tree->Branch("Counter_mult_4", &counter_mult_4, "Counter_mult_4/I");
    tree->Branch("Counter_mult_5", &counter_mult_5, "Counter_mult_5/I");
    tree->Branch("Counter_mult_6", &counter_mult_6, "Counter_mult_6/I");
    tree->Branch("Counter_mult_7", &counter_mult_7, "Counter_mult_7/I");



    while ((data = faster_file_reader_next(reader)) != NULL) {
        group_time = faster_data_clock_ns(data);
        if (faster_data_type_alias(data) != GROUP_TYPE_ALIAS) continue;

        group_buffer = faster_data_load_p(data);
        lsize = faster_data_load_size(data);
        group_reader = faster_buffer_reader_open(group_buffer, lsize);

        // RAZ
        qdc_2_q1 = qdc_2_q2 = qdc_2_q3 = qdc_2_q4 = NO_DATA;
        qdc_4_q1 = qdc_4_q2 = qdc_4_q3 = qdc_4_q4 = NO_DATA;
        qdc_2_q1_saturated = qdc_2_q2_saturated = false;
        qdc_4_q1_saturated = qdc_4_q2_saturated = false;

        qt2t_5_q = qt2t_6_q = qt2t_7_q = NO_DATA;
        qt2t_5_width = qt2t_6_width = qt2t_7_width = NO_DATA;
        qt2t_5_max_ampl = qt2t_6_max_ampl = qt2t_7_max_ampl = NO_DATA;
        qt2t_5_max_pos = qt2t_6_max_pos = qt2t_7_max_pos = NO_DATA;
        qt2t_5_q_baseline = qt2t_6_q_baseline = qt2t_7_q_baseline = NO_DATA;
        qt2t_5_saturated = qt2t_6_saturated = qt2t_7_saturated = false;
        
        counter_2 = counter_4 = counter_5 = counter_6 = counter_7 = 0;
        counter_mult_2 = counter_mult_4  = counter_mult_5 = counter_mult_6 = counter_mult_7 = 0; 

    
        
        while ((group_data = faster_buffer_reader_next(group_reader)) != NULL) {
            unsigned short label = faster_data_label(group_data);
            unsigned char alias = faster_data_type_alias(group_data);
            
            

            if (alias == QDC_X1_TYPE_ALIAS) {
                
                qdc_x1 qdc;

                memcpy(&qdc, faster_data_load_p(group_data), sizeof(qdc_x1));
                if (label == 2) {
                    if (counter_2 == 0) {    //On récupére les valeurs d'une voie seulement sur sa premiére occurence dans le groupe de coincidence.
                        
                        qdc_2_q1 = qdc.q1;
                        qdc_2_q1_saturated = qdc.q1_saturated;

                        counter_2++;
                    }    

                counter_mult_2++;
                    
                } else if (label == 4) {
                    if (counter_4 == 0) {

                        qdc_4_q1 = qdc.q1;
                        qdc_4_q1_saturated = qdc.q1_saturated;
                    
                        counter_4++;
                    }

                counter_mult_4++;

                }
            }
            if (alias == QDC_X2_TYPE_ALIAS) {
                
                qdc_x2 qdc;

                memcpy(&qdc, faster_data_load_p(group_data), sizeof(qdc_x2));
                if (label == 2) {
                    if (counter_2 == 0) {  
                        
                        qdc_2_q1 = qdc.q1;
                        qdc_2_q2 = qdc.q2;
                        qdc_2_q1_saturated = qdc.q1_saturated;
                        qdc_2_q2_saturated = qdc.q2_saturated;                        

                        counter_2++;
                    }    

                counter_mult_2++;
                    
                } else if (label == 4) {
                    if (counter_4 == 0) {

                        qdc_4_q1 = qdc.q1;
                        qdc_4_q2 = qdc.q2;
                        qdc_4_q1_saturated = qdc.q1_saturated;
                        qdc_4_q2_saturated = qdc.q2_saturated;
                    
                        counter_4++;
                    }

                counter_mult_4++;

                }
            }

            if (alias == QT2T_TYPE_ALIAS) {
                memcpy(&qt, faster_data_load_p(group_data), sizeof(qt2t));
                Int_t* q = nullptr, *width = nullptr, *max_ampl = nullptr, *q_baseline = nullptr;
                Double_t* max_pos = nullptr;
                Bool_t* saturated = nullptr;

                if (label == 5) {
                    if (counter_5 == 0) {
                        q = &qt2t_5_q; width = &qt2t_5_width; max_ampl = &qt2t_5_max_ampl;
                        max_pos = &qt2t_5_max_pos; q_baseline = &qt2t_5_q_baseline; saturated = &qt2t_5_saturated;
                        
                        counter_5++;
                    }

                    counter_mult_5++;

                } else if (label == 6) {
                    if (counter_6 == 0) {
                        q = &qt2t_6_q; width = &qt2t_6_width; max_ampl = &qt2t_6_max_ampl;
                        max_pos = &qt2t_6_max_pos; q_baseline = &qt2t_6_q_baseline; saturated = &qt2t_6_saturated;
                    
                        counter_6++;    
                    }

                    counter_mult_6++;

                } else if (label == 7) {
                    if (counter_7 == 0) {
                        q = &qt2t_7_q; width = &qt2t_7_width; max_ampl = &qt2t_7_max_ampl;
                        max_pos = &qt2t_7_max_pos; q_baseline = &qt2t_7_q_baseline; saturated = &qt2t_7_saturated;

                        counter_7++;
                    }

                    counter_mult_7++;
                }

                if (q) {      
                    *q = qt.q;
                    *width = qt.w;
                    *max_ampl = qt.a_max;
                    *max_pos = qt.t_max;
                    *q_baseline = qt.q_baseline;
                    *saturated = qt.saturated;
                }
            }
        }

        tree->Fill();

        faster_buffer_reader_close(group_reader);
    }

    faster_file_reader_close(reader);
    root_file->Write();
    root_file->Close();
    return EXIT_SUCCESS;
}
