#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

# implementation classe noeud

class Noeud:
    def __init__(self, frequence: int, caractere=None, gauche=None, droite=None, parent=None, numero: int = 0) -> None:
        self._frequence = frequence
        self._caractere = caractere
        self._gauche = gauche
        self._droite = droite
        self._parent = parent
        self._numero = numero

    def get_frequence(self) -> int:
        return self._frequence

    def get_caractere(self):
        return self._caractere

    def get_gauche(self):
        return self._gauche

    def get_droite(self):
        return self._droite

    def get_parent(self):
        return self._parent
    
    def get_numero(self) -> int:
        return self._numero

    def set_frequence(self, frequence: int):
        self._frequence = frequence

    def set_caractere(self, caractere):
        self._caractere = caractere

    def set_gauche(self, gauche):
        self._gauche = gauche

    def set_droite(self, droite):
        self._droite = droite

    def set_parent(self, parent):
        self._parent = parent
        
    def set_numero(self, numero: int):
        self._numero = numero

    def est_feuille(self) -> bool:
        return self._gauche is None and self._droite is None

# implementation classe arbre

class ArbreHuffman:
    def __init__(self):
        self.NYT = Noeud(frequence=0, caractere=None, numero=512) 
        self.racine = self.NYT
        self.symbole_vers_noeud = {}
        self.numero_vers_noeud = {1000: self.NYT}
        self.numero_max = 1000

    def obtenir_code(self, symbole):
        """
        Retourne le code binaire associé à un symbole
        Si le symbole est nouveau, encode le chemin vers le NYT et le symbole en UTF-8
        """
        if symbole in self.symbole_vers_noeud:
            return self.obtenir_chemin(self.symbole_vers_noeud[symbole])
        else: 
            # si le symbole est nouveau, on envoie le code du NYT puis le symbole lui-même
            symbole_encode_en_octets = symbole.encode('utf-8')
            # Chemin vers NYT + représentation binaire de la longueur des octets du symbole + représentation binaire des octets du symbole
            chemin_nyt = self.obtenir_chemin(self.NYT)  # obtenir le chemin binaire vers le NYT
            longueur_utf8 = f"{len(symbole_encode_en_octets):08b}"
            octets_utf8 = ''.join(f"{octet:08b}" for octet in symbole_encode_en_octets)

            # concaténation du chemin NYT, de la longueur UTF-8 et des octets UTF-8
            code_binaire = chemin_nyt + longueur_utf8 + octets_utf8

            return code_binaire

    def obtenir_chemin(self, noeud):
        """
        Calcule le chemin binaire d'un nœud en remontant jusqu'à la racine
        """
        chemin = ""
        noeud_courant = noeud
        while noeud_courant is not None and noeud_courant != self.racine:
            parent_noeud = noeud_courant.get_parent()
            if parent_noeud.get_gauche() == noeud_courant:
                chemin = "0" + chemin
            else:
                chemin = "1" + chemin
            noeud_courant = parent_noeud
        return chemin

    def mettre_a_jour(self, symbole):
        """
        Met à jour l'arbre après avoir traité un symbole
        Ajoute un nouveau nœud si le symbole est nouveau, ou incrémente la fréquence sinon
        """
        noeud_a_incrementer_ou_parent_du_nouveau = None

        if symbole in self.symbole_vers_noeud:
            # le symbole existe déjà donc on va incrémenter sa feuille
            noeud_actuel = self.symbole_vers_noeud[symbole]
            noeud_a_incrementer_ou_parent_du_nouveau = noeud_actuel
        else:
            # c'est un nouveau symbole
            # on étend l'arbre à partir du NYT
            parent_NYT = self.NYT.get_parent()
            nouveau_noeud_interne = Noeud(frequence=0, parent=parent_NYT, numero=self.numero_max - 1)
            # la nouvelle feuille pour le symbole et l'ancien NYT deviennent enfants du nouveau noeud interne
            nouvelle_feuille = Noeud(frequence=0, caractere=symbole, parent=nouveau_noeud_interne, numero=self.numero_max - 2)
            
            nouveau_noeud_interne.set_gauche(self.NYT)
            nouveau_noeud_interne.set_droite(nouvelle_feuille)
            self.NYT.set_parent(nouveau_noeud_interne)

            if parent_NYT is not None:
                if parent_NYT.get_gauche() == self.NYT: # Si NYT était le fils gauche de son parent
                    parent_NYT.set_gauche(nouveau_noeud_interne)
                else: # Si NYT était le fils droit
                    parent_NYT.set_droite(nouveau_noeud_interne)
            else: # NYT était la racine
                self.racine = nouveau_noeud_interne

            self.numero_max -= 2
            self.numero_vers_noeud[nouveau_noeud_interne.get_numero()] = nouveau_noeud_interne
            self.numero_vers_noeud[nouvelle_feuille.get_numero()] = nouvelle_feuille
            self.symbole_vers_noeud[symbole] = nouvelle_feuille

            # on commence l'incrémentation à partir du parent du nouveau noeud (le nouveau noeud interne)
            noeud_a_incrementer_ou_parent_du_nouveau = nouveau_noeud_interne

        # on remonte vers la racine en bouclant jusqu'à ce qu'on l'atteigne
        noeud_courant_pour_maj = noeud_a_incrementer_ou_parent_du_nouveau
        while noeud_courant_pour_maj is not None:
            meneur = self.trouver_leader(noeud_courant_pour_maj)
            # si un meneur existe, n'est pas le noeud courant lui-même, et n'est pas son parent (pour éviter des échanges invalides)
            if meneur is not None and meneur != noeud_courant_pour_maj and meneur != noeud_courant_pour_maj.get_parent():
                self.echanger_noeuds(noeud_courant_pour_maj, meneur)
            
            noeud_courant_pour_maj.set_frequence(noeud_courant_pour_maj.get_frequence() + 1)
            noeud_courant_pour_maj = noeud_courant_pour_maj.get_parent()

    def trouver_leader(self, noeud_ref):
        """
        Trouve le nœud leader ayant la même fréquence que le nœud de référence,
        mais avec un numéro plus élevé
        """
        frequence_ref = noeud_ref.get_frequence()
        candidats = []
        for n in self.numero_vers_noeud.values():
            # Un meneur doit avoir la même fréquence, ne pas être le noeud de référence lui-même,
            # et ne pas être le parent du noeud de référence
            if n.get_frequence() == frequence_ref and n != noeud_ref and n.get_parent() != noeud_ref:
                candidats.append(n)
        
        if not candidats:
            return None
        # Le meneur est celui avec le plus grand numéro parmi les candidats
        return max(candidats, key=lambda x: x.get_numero())

    def echanger_noeuds(self, noeud_a, noeud_b):
        """
        Échange deux nœuds dans l'arbre, en mettant à jour leurs parents et leurs numéros
        """
        parent_a = noeud_a.get_parent()
        parent_b = noeud_b.get_parent()
        
        # on met à jour les noeuds gauche et droite des noeuds parents
        if parent_a is not None:
            if parent_a.get_gauche() == noeud_a:
                parent_a.set_gauche(noeud_b)
            else:
                parent_a.set_droite(noeud_b)
        else: # noeud_a = la racine
            self.racine = noeud_b

        if parent_b is not None:
            if parent_b.get_gauche() == noeud_b:
                parent_b.set_gauche(noeud_a)
            else:
                parent_b.set_droite(noeud_a)
        else: # noeud_b = la racine
            self.racine = noeud_a
            
        # Mettre à jour les parents des noeuds échangés
        noeud_a.set_parent(parent_b)
        noeud_b.set_parent(parent_a)
        
        # Échanger les numéros
        num_a = noeud_a.get_numero()
        num_b = noeud_b.get_numero()
        noeud_a.set_numero(num_b)
        noeud_b.set_numero(num_a)
        
        # on met à jour le dictionnaire numero_vers_noeud
        self.numero_vers_noeud[noeud_a.get_numero()] = noeud_a
        self.numero_vers_noeud[noeud_b.get_numero()] = noeud_b
        
        # Mise à jour du symbole_vers_noeud si les noeuds sont des feuilles avec des symboles
        if noeud_a.est_feuille() and noeud_a.get_caractere() is not None:
            self.symbole_vers_noeud[noeud_a.get_caractere()] = noeud_a
        if noeud_b.est_feuille() and noeud_b.get_caractere() is not None:
            self.symbole_vers_noeud[noeud_b.get_caractere()] = noeud_b

# compression

def compresser(chemin_entree, chemin_sortie):
    """
    Compresse un fichier texte en utilisant l'algorithme de Huffman adaptatif
    """
    arbre = ArbreHuffman()
    with open(chemin_entree, 'r', encoding='utf-8') as f_entree:
        texte_original = f_entree.read()

    liste_de_codes_bits = [] # Utiliser une liste pour accumuler les codes
    for caractere_actuel in texte_original:
        code_pour_caractere = arbre.obtenir_code(caractere_actuel)
        liste_de_codes_bits.append(code_pour_caractere)
        arbre.mettre_a_jour(caractere_actuel)

    flux_bits_concatene = "".join(liste_de_codes_bits) # Concaténer à la fin

    # Calcul + application du padding
    longueur_flux_avant_padding = len(flux_bits_concatene)
    reste_division_par_8 = longueur_flux_avant_padding % 8
    
    longueur_padding = 0
    if reste_division_par_8 != 0:
        longueur_padding = 8 - reste_division_par_8

    bits_info_padding = format(longueur_padding, '08b')
    
    flux_bits_avec_info_padding = bits_info_padding + flux_bits_concatene
    
    # Ajout des bits de padding effectifs
    padding_zeros = '0' * longueur_padding
    flux_bits_final_a_ecrire = flux_bits_avec_info_padding + padding_zeros

    # on va stocker tous nos octets dans le bytearray
    octets_a_ecrire = bytearray()
    index_courant = 0
    while index_courant < len(flux_bits_final_a_ecrire):
        bloc_huit_bits = flux_bits_final_a_ecrire[index_courant : index_courant + 8]
        valeur_octet = int(bloc_huit_bits, 2)
        octets_a_ecrire.append(valeur_octet)
        index_courant += 8

    with open(chemin_sortie, 'wb') as f_sortie:
        f_sortie.write(octets_a_ecrire)

# decompression

def decompresser(chemin_entree, chemin_sortie):
    """
    Décompresse un fichier compressé en utilisant l'algorithme de Huffman adaptatif
    """
    # on reproduit l'arbre qu'on va enrichir au
    # fur et a mesure pour décompresser le fichier
    arbre = ArbreHuffman()
    
    contenu_binaire_fichier = b''

    # on vérifie que le fichier existe
    try:
        with open(chemin_entree, 'rb') as f_entree:
            contenu_binaire_fichier = f_entree.read()
    except FileNotFoundError:
        print(f"Erreur : Le fichier d'entrée '{chemin_entree}' est introuvable.")
        return

    liste_bits_entree = []
    for octet_lu in contenu_binaire_fichier:
        representation_binaire_octet = format(octet_lu, '08b')
        liste_bits_entree.append(representation_binaire_octet)
    bits_entree_complets = "".join(liste_bits_entree)

    bits_longueur_padding = bits_entree_complets[0:8]
    longueur_padding = int(bits_longueur_padding, 2)
    
    index_debut_bits_effectifs = 8
    index_fin_bits_effectifs = len(bits_entree_complets)
    if longueur_padding > 0:
        index_fin_bits_effectifs -= longueur_padding
    
    bits_effectifs = bits_entree_complets[index_debut_bits_effectifs:index_fin_bits_effectifs]

    indice_bit_courant = 0
    liste_caracteres_decodes = [] 

    while indice_bit_courant < len(bits_effectifs):
        noeud_parcours = arbre.racine

        while not noeud_parcours.est_feuille():
            if indice_bit_courant >= len(bits_effectifs):
                # Fin inattendue du flux de bits pendant la traversée
                print("Avertissement: Fin inattendue du flux de bits pendant la recherche d'un symbole.")
                break 
            
            bit_actuel = bits_effectifs[indice_bit_courant]

            if bit_actuel == '0':
                noeud_parcours = noeud_parcours.get_gauche()
            else:
                noeud_parcours = noeud_parcours.get_droite()
            
            indice_bit_courant += 1
            if noeud_parcours is None:
                print("Erreur: Chemin invalide (nœud null) dans l'arbre pendant la décompression.")
                with open(chemin_sortie, 'w', encoding='utf-8') as f_sortie_erreur:
                    f_sortie_erreur.write("".join(liste_caracteres_decodes))
                return
        
        if noeud_parcours is None or (not noeud_parcours.est_feuille() and indice_bit_courant >= len(bits_effectifs)):
            # Si noeud_parcours est None ou si on n'a pas atteint une feuille et qu'il n'y a plus de bits
            print("Avertissement: Impossible de décoder un symbole complet à la fin du flux.")
            break 

        symbole_resultat_decodage = None

        if noeud_parcours == arbre.NYT: # Comparaison avec l'objet NYT de l'arbre
            # Décodage d'un nouveau symbole (NYT)
            # Lire d'abord la longueur du symbole en UTF-8 (1 octet pour la longueur)
            if indice_bit_courant + 8 > len(bits_effectifs):
                print("Avertissement: Flux de bits insuffisant pour lire la longueur d'un nouveau symbole (NYT).")
                break
            
            bits_pour_longueur_symbole_utf8 = bits_effectifs[indice_bit_courant : indice_bit_courant + 8]
            longueur_symbole_utf8 = int(bits_pour_longueur_symbole_utf8, 2)
            indice_bit_courant += 8
            
            # Lire les octets du symbole UTF-8
            if indice_bit_courant + 8 * longueur_symbole_utf8 > len(bits_effectifs):
                print(f"Avertissement: Flux de bits insuffisant pour lire les {longueur_symbole_utf8} octets d'un nouveau symbole (NYT).")
                break
            
            liste_octets_pour_symbole = []
            compteur_octets_lus = 0
            while compteur_octets_lus < longueur_symbole_utf8:
                bits_pour_un_octet_symbole = bits_effectifs[indice_bit_courant : indice_bit_courant + 8]
                valeur_octet_symbole = int(bits_pour_un_octet_symbole, 2)
                liste_octets_pour_symbole.append(valeur_octet_symbole)
                indice_bit_courant += 8
                compteur_octets_lus += 1
            
            octets_symbole_complets = bytes(liste_octets_pour_symbole)
            try:
                symbole_resultat_decodage = octets_symbole_complets.decode('utf-8')
            except UnicodeDecodeError:
                print(f"Erreur de décodage UTF-8 pour la séquence d'octets: {octets_symbole_complets}")
                symbole_resultat_decodage = "" # Caractère de remplacement
        
        elif noeud_parcours is not None and noeud_parcours.est_feuille(): # C'est une feuille existante
            symbole_resultat_decodage = noeud_parcours.get_caractere()

        if symbole_resultat_decodage is None:
            # Cela peut se produire si le flux de bits se termine de manière inattendue
            # ou si une erreur de logique interne s'est produite.
            print("Avertissement: Symbole non décodé lors d'une itération, arrêt de la décompression.")
            break 

        liste_caracteres_decodes.append(symbole_resultat_decodage)
        arbre.mettre_a_jour(symbole_resultat_decodage)

    texte_sortie_final = "".join(liste_caracteres_decodes)
    # on ecrit dans le fichier
    with open(chemin_sortie, 'w', encoding='utf-8') as f_sortie:
        f_sortie.write(texte_sortie_final)



def main():
    analyseur = argparse.ArgumentParser(description="Compression Huffman adaptative (streaming, UTF-8)")
    analyseur.add_argument("-e", metavar="fichier_entree", help="Fichier à compresser")
    analyseur.add_argument("-d", metavar="fichier_entree", help="Fichier à décompresser")
    analyseur.add_argument("-o", metavar="fichier_sortie", required=True, help="Fichier de sortie")
    arguments = analyseur.parse_args()

    debut = time.time()
    if arguments.e:
        compresser(arguments.e, arguments.o)
        print(f"Fichier compressé : {arguments.o}")
    elif arguments.d:
        decompresser(arguments.d, arguments.o)
        print(f"Fichier décompressé : {arguments.o}")
    else:
        print("Spécifiez -e (encoder) ou -d (décoder).") 
    fin = time.time()
    print(f"temps d'exécution : {fin - debut:.3f} secondes")

if __name__ == "__main__":
    main()