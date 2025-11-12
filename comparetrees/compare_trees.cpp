#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TLeaf.h"

bool CompareTrees(TTree *t1, TTree *t2) {
    // Vérifier le nombre d'entrées
    if (t1->GetEntries() != t2->GetEntries()) {
        std::cerr << "Nombre d'entrées différent : " << t1->GetEntries() << " vs " << t2->GetEntries() << std::endl;
        return false;
    }

    // Vérifier le nombre de branches
    TObjArray *branches1 = t1->GetListOfBranches();
    TObjArray *branches2 = t2->GetListOfBranches();

    if (branches1->GetEntries() != branches2->GetEntries()) {
        std::cerr << "Nombre de branches différent." << std::endl;
        return false;
    }

    // Vérifier les noms et types des branches
    for (int i = 0; i < branches1->GetEntries(); i++) {
        TBranch *b1 = (TBranch*)branches1->At(i);
        TBranch *b2 = (TBranch*)branches2->At(i);

        if (strcmp(b1->GetName(), b2->GetName()) != 0) {
            std::cerr << "Nom de branche différent : " << b1->GetName() << " vs " << b2->GetName() << std::endl;
            return false;
        }

        // Vérifier que les branches ont des feuilles
        TObjArray *leaves1 = b1->GetListOfLeaves();
        TObjArray *leaves2 = b2->GetListOfLeaves();

        if (!leaves1 || !leaves2) {
            std::cerr << "Erreur : impossible de récupérer les feuilles pour la branche " << b1->GetName() << std::endl;
            return false;
        }

        if (leaves1->GetEntries() != leaves2->GetEntries()) {
            std::cerr << "Nombre de feuilles différent pour la branche " << b1->GetName() << std::endl;
            return false;
        }

        // Vérifier le type de la première feuille (simplification)
        TLeaf *leaf1 = (TLeaf*)leaves1->At(0);
        TLeaf *leaf2 = (TLeaf*)leaves2->At(0);

        if (strcmp(leaf1->GetTypeName(), leaf2->GetTypeName()) != 0) {
            std::cerr << "Type de feuille différent pour " << b1->GetName() << std::endl;
            return false;
        }
    }

    // Comparer les données
    for (Long64_t i = 0; i < t1->GetEntries(); i++) {
        t1->GetEntry(i);
        t2->GetEntry(i);

        for (int j = 0; j < branches1->GetEntries(); j++) {
            TBranch *b1 = (TBranch*)branches1->At(j);
            TBranch *b2 = (TBranch*)branches2->At(j);

            TObjArray *leaves1 = b1->GetListOfLeaves();
            TObjArray *leaves2 = b2->GetListOfLeaves();

            if (!leaves1 || !leaves2) {
                std::cerr << "Erreur : impossible de récupérer les feuilles pour la branche " << b1->GetName() << std::endl;
                return false;
            }

            TLeaf *leaf1 = (TLeaf*)leaves1->At(0);
            TLeaf *leaf2 = (TLeaf*)leaves2->At(0);

            // Vérifier que les feuilles existent
            if (!leaf1 || !leaf2) {
                std::cerr << "Erreur : feuille introuvable pour la branche " << b1->GetName() << std::endl;
                return false;
            }

            // Comparaison des valeurs
            if (leaf1->GetValue(0) != leaf2->GetValue(0)) {
                std::cerr << "Différence à l'entrée " << i << " pour la branche " << b1->GetName()
                          << " : " << leaf1->GetValue(0) << " vs " << leaf2->GetValue(0) << std::endl;
                return false;
            }
        }
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " fichier1.root fichier2.root" << std::endl;
        return EXIT_FAILURE;
    }

    TFile *f1 = TFile::Open(argv[1]);
    TFile *f2 = TFile::Open(argv[2]);

    if (!f1 || !f2) {
        std::cerr << "Erreur : impossible d'ouvrir un des fichiers." << std::endl;
        return EXIT_FAILURE;
    }

    TTree *t1 = (TTree*)f1->Get("DataTree");
    TTree *t2 = (TTree*)f2->Get("DataTree");

    if (!t1 || !t2) {
        std::cerr << "Erreur : impossible de trouver l'arbre 'DataTree' dans un des fichiers." << std::endl;
        return EXIT_FAILURE;
    }

    if (CompareTrees(t1, t2)) {
        std::cout << "Les arbres sont identiques." << std::endl;
    } else {
        std::cout << "Les arbres sont différents." << std::endl;
    }

    f1->Close();
    f2->Close();

    return EXIT_SUCCESS;
}
