#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse


freq = {"a":7, "b":1, "c":3, "d":4, "e":12, "f":1, "g":1, "h":1, "i":6, "j":0, 
        "k":0, "l":5, "m":3, "n":6, "o":5, "p":2, "q":0, "r":6, "s":6, "t":6, 
        "u":4, "v":1, "w":0, "x":0, "y":0, "z":0, "à":0, "é":2, "è":0, ",":2, 
        "-":0, ".":1, ";":0, "!":0, "?":0, "\n":0, "<sp>":15}

class Noeud:
    def __init__(self, frequence: int, caractere=None, gauche=None, droite=None, parent=None) -> None:
        self._frequence = frequence
        self._caractere = caractere
        self._gauche = gauche
        self._droite = droite
        self._parent = parent

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

    def est_feuille(self) -> bool:
        return self._gauche is None and self._droite is None
    

def trier_dic(frequence) -> dict:
    """
    Cette fonction permet de trier le dictionnaire selon les valeurs dans un ordre croissant.
    Le résultat de ce tri sera toujours le même, même si plusieurs valeurs sont identiques, car sorted est déterministe

    Entrée : dictionnaire de frequence freq
    Sortie : dictionnaire de frequence freq_trie
    """
    frequenceTrie : dict
    frequenceTrie = dict(sorted(frequence.items(), key=lambda item: item[1]))

    return frequenceTrie

def creer_liste_noeuds(itemList: list[tuple[str, int]]) -> list[Noeud]:
    """
    Cette fonction transforme une liste de tuples (clé (caractere), valeur (fréquence))
    en une liste de Noeud.
    """
    listeNoeuds: list[Noeud] = []
    listeNoeuds.append(Noeud(0, "<inconnu>"))
    
    for item in itemList:
        listeNoeuds.append(Noeud(item[1], item[0]))

    return listeNoeuds

def dic_2_tree(dictionnaire) -> Noeud:
    """
    Cette fonction prend un dictionnaire trie de frequences de caracteres pour en faire un arbre
    Entree : dictionnaire de frequence trie
    Sortie : Noeud racine de l'arbre de frequences
    """
    items = list(dictionnaire.items())
    listeNoeuds = creer_liste_noeuds(items)

    while len(listeNoeuds) >= 2:
        gauche = listeNoeuds.pop(0)
        droite = listeNoeuds.pop(0)
        
        # creer le noeud parent
        frequence_parent = gauche.get_frequence() + droite.get_frequence()
        noeudParent = Noeud(frequence_parent, gauche=gauche, droite=droite)
        gauche.set_parent(noeudParent)
        droite.set_parent(noeudParent)

        # ajouter le parent et trier a nouveau la liste par frequence croissante
        listeNoeuds.append(noeudParent)
        listeNoeuds.sort(key=lambda n: n.get_frequence())
    
    return listeNoeuds[0]

def generer_codes(noeud_racine) -> dict[str, str]:
    """
    Cette fonction parcourt l'arbre de Huffman à partir du noeud racine pour générer les codes binaires
    de chaque caractère.
    Entree : noeud_racine
    Sortie : dictionnaire {caractere: code_binaire}
    """
    codes = {}

    def parcours(noeud, chemin=""):
        if noeud is None:
            return
        if noeud.est_feuille():
            if noeud.get_caractere() is not None:
                codes[noeud.get_caractere()] = chemin
        else:
            parcours(noeud.get_gauche(), chemin + "0")
            parcours(noeud.get_droite(), chemin + "1")

    parcours(noeud_racine)
    return codes

def fichier_txt_2_str(chemin_fichier):
    """
    Lit le contenu d'un fichier texte et le retourne sous forme de chaîne de caractères.
    Entree : chemin_fichier (str) - Le chemin vers le fichier à lire.
    Sortie : str - Le contenu du fichier, ou None si une erreur survient.
    """
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        contenu = f.read()
    return contenu

def texte_2_binaire(texte, dictionnaire):
    """
    Lit le texte (str) pour renvoyer une liste de nombres binaires
    """
    binaire_final = []
    for caractere in texte:
        original_caractere = caractere # Conserver l'original pour l'encodage UTF-8 si inconnu
        if caractere == " ":
            caractere = "<sp>" # Convertir l'espace en token <sp>

        if caractere in dictionnaire:
            binaire_final.append(dictionnaire[caractere])
        else:
            # Si même après conversion (ou si ce n'était pas un espace), il est inconnu
            # Utiliser original_caractere pour l'encodage UTF-8
            octets = original_caractere.encode('utf-8') 
            # Ajouter la longueur des octets UTF-8 ici, comme dans huffman_tristan.py
            binaire_final.append(dictionnaire["<inconnu>"])
            binaire_final.append(f"{len(octets):08b}") # Longueur UTF-8 sur 8 bits
            for byte in octets:
                binaire_final.append(f'{byte:08b}') # Chaque octet encodé sur 8 bits
    
    return binaire_final

def liste_binaires_2_tableau_octets(liste_bin : list):
    """
    Convertit une liste de chaînes binaires en tableau d'octets (bytearray), avec padding à la fin si nécessaire.
    Le padding est stocké dans le premier octet du résultat.
    """
    message_bin = bytearray()
    str_bin = "".join(liste_bin)

    stock_binaire = ""
    for bin in str_bin:
        stock_binaire += bin
        if len(stock_binaire) == 8:
            octet_base_2 = int(stock_binaire, 2)
            message_bin.append(octet_base_2)
            stock_binaire = ""

    # Padding si le dernier octet est incomplet
    padding = 0
    if len(stock_binaire) > 0:
        padding = 8 - len(stock_binaire)
        stock_binaire += "0" * padding  # Ajout du padding
        octet_base_2 = int(stock_binaire, 2)
        message_bin.append(octet_base_2)

    # On stocke la taille du padding dans le premier octet du fichier
    return bytearray([padding]) + message_bin

# ---

# Partie décodage

# ---

def octets_2_texte(fichier_binaire, racine_arbre):
    """
    Décode un fichier compressé Huffman en parcourant l’arbre.
    Entrée :
        - fichier_binaire : chemin du fichier compressé
        - racine_arbre : racine de l’arbre de Huffman utilisé à l’encodage
    Sortie :
        - texte décodé (str)
    """
    with open(fichier_binaire, 'rb') as f:
        contenu = f.read()

    padding = contenu[0]
    octets_utiles = contenu[1:]

    # Reconstituer la chaîne binaire
    str_bin = ''.join(f'{byte:08b}' for byte in octets_utiles)
    if padding > 0:
        str_bin = str_bin[:-padding]

    texte_decode = ""
    noeud = racine_arbre
    i = 0
    while i < len(str_bin):
        bit = str_bin[i]
        noeud = noeud.get_gauche() if bit == "0" else noeud.get_droite()

        if noeud.est_feuille():
            caractere = noeud.get_caractere()

            if caractere == "<sp>":
                texte_decode += " "
            elif caractere == "<inconnu>":
                i += 1
                longueur = int(str_bin[i:i+8], 2)
                i += 8
                octets_utf8 = []
                for _ in range(longueur):
                    octet_bin = str_bin[i:i+8]
                    octets_utf8.append(int(octet_bin, 2))
                    i += 8
                texte_decode += bytes(octets_utf8).decode('utf-8')
                noeud = racine_arbre
                continue
            else:
                texte_decode += caractere
            noeud = racine_arbre
        i += 1

    return texte_decode

def main():
    # gestion des arguments

    parser = argparse.ArgumentParser(description="Encode ou décode des fichiers avec l'algorithme de Huffman statique.")
    parser.add_argument("-e", "--encode", metavar="FICHIER_ENTREE", help="Chemin vers le fichier à encoder.")
    parser.add_argument("-o", "--output", metavar="FICHIER_SORTIE", help="Chemin vers le fichier de sortie pour l'encodage/décodage.")
    parser.add_argument("-d", "--decode", metavar="FICHIER_COMPRESSE", help="Chemin vers le fichier compressé à décoder.")

    args = parser.parse_args()
    
    dic_trie = trier_dic(freq)
    arbre_de_huffman = dic_2_tree(dic_trie)
    dic_final = generer_codes(arbre_de_huffman)

    if args.encode and args.output:
        print(f"Encodage du fichier : {args.encode}")
        print(f"Fichier de sortie : {args.output}")

        texte_en_str = fichier_txt_2_str(args.encode)
        binaire = texte_2_binaire(texte_en_str, dic_final)
        
        texte_encode = liste_binaires_2_tableau_octets(binaire)
        with open(args.output, 'wb') as f_sortie:
            f_sortie.write(texte_encode)
    
    elif args.decode and args.output:
        print(f"Décodage du fichier : {args.decode}")
        print(f"Fichier de sortie : {args.output}")
        
        texte_decode = octets_2_texte(args.decode, arbre_de_huffman)

        with open(args.output, 'w', encoding='utf-8') as f_out:
            f_out.write(texte_decode)
        
if __name__ == "__main__":
    main()
