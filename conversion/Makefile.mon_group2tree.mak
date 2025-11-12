# Nom des exécutables
TARGETS = mon_group2tree_v3 Faster2root

# Cible par défaut
all: $(TARGETS)

# Compilation
CXX = g++
CXXFLAGS = $(shell root-config --cflags)
LDFLAGS  = $(shell root-config --libs) -lfasterac

# Règle de compilation

mon_group2tree_v3: mon_group2tree_v3.cpp
	$(CXX) -o $@ $< $(CXXFLAGS) $(LDFLAGS)

Faster2root: Faster2root.cpp
	$(CXX) -o $@ $< $(CXXFLAGS) $(LDFLAGS)

# Nettoyage
clean:
	rm -f $(TARGETS)
