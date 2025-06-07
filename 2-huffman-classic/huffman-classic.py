#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse


class Noeud:
    def __init__(self, frequence=0, caractere=None, gauche=None, droite=None):
        # Un nœud de l'arbre de Huffman, contenant un caractère, sa fréquence
        # et des références aux sous-arbres gauche et droit
        self.caractere = caractere
        self.frequence = frequence
        self.gauche = gauche
        self.droite = droite


def compter_frequences(texte):
    """Compte les fréquences des caractères dans un texte."""
    # Crée un dictionnaire où chaque caractère est une clé et sa fréquence est la valeur
    frequences = {}
    for caractere in texte:
        frequences[caractere] = frequences.get(caractere, 0) + 1
    return frequences


def construire_arbre(dictionnaire_frequences):
    """Construit l'arbre de Huffman à partir d'un dictionnaire de fréquences."""
    # Crée une liste de nœuds à partir des fréquences des caractères
    liste_noeuds = [Noeud(frequence=f, caractere=c) for c, f in dictionnaire_frequences.items() if f > 0]

    # cas spéciaux
    if not liste_noeuds:
        # Si aucun caractère n'est présent, retourne None
        return None
    if len(liste_noeuds) == 1:
        # Si un seul caractère est présent, retourne ce nœud comme racine
        return liste_noeuds[0]

    # Combine les deux nœuds de plus faible fréquence jusqu'à ce qu'il ne reste qu'un seul nœud
    while len(liste_noeuds) > 1:
        liste_noeuds.sort(key=lambda noeud: noeud.frequence)  # Trie par fréquence croissante
        a = liste_noeuds.pop(0)  # Nœud avec la plus petite fréquence
        b = liste_noeuds.pop(0)  # Deuxième plus petite fréquence

        # Crée un nœud parent avec la somme des fréquences
        parent = Noeud(frequence=a.frequence + b.frequence, gauche=a, droite=b)
        liste_noeuds.append(parent)

    return liste_noeuds[0]  # Le dernier nœud est la racine de l'arbre


def generer_codes(noeud, prefixe="", table=None):
    """Génère un dictionnaire de codes binaires à partir de l'arbre de Huffman."""
    if table is None:
        table = {}

    if noeud is None:
        return table

    if noeud.caractere is not None:
        # Si le nœud est une feuille, associe le caractère au code binaire
        table[noeud.caractere] = prefixe if prefixe else "0"
    else:
        # Parcours récursif des sous-arbres gauche et droit
        if noeud.gauche:
            generer_codes(noeud.gauche, prefixe + "0", table)
        if noeud.droite:
            generer_codes(noeud.droite, prefixe + "1", table)

    return table


def serialiser_arbre(noeud):
    """Sérialise l'arbre de Huffman en une chaîne de bits."""
    if noeud is None:
        return ""

    if noeud.caractere is not None:
        # Sérialise une feuille : "1" suivi de la longueur et des bits du caractère
        encodage = noeud.caractere.encode("utf-8")
        longueur_symbole = format(len(encodage), "08b")
        bits_symbole = "".join(f"{octet:08b}" for octet in encodage)
        return "1" + longueur_symbole + bits_symbole

    # Sérialise récursivement les sous-arbres gauche et droit
    gauche_bits = serialiser_arbre(noeud.gauche) if noeud.gauche else ""
    droite_bits = serialiser_arbre(noeud.droite) if noeud.droite else ""
    return "0" + gauche_bits + droite_bits


def deserialiser_arbre(bits, index_ref):
    """Désérialise un arbre de Huffman à partir d'une chaîne de bits."""
    if index_ref[0] >= len(bits):
        return None, index_ref[0]

    bit_courant = bits[index_ref[0]]
    index_ref[0] += 1

    if bit_courant == "1":
        # Désérialise une feuille : lit la longueur et les bits du caractère
        longueur = int(bits[index_ref[0]:index_ref[0] + 8], 2)
        index_ref[0] += 8
        symbole_bits = bits[index_ref[0]:index_ref[0] + (longueur * 8)]
        index_ref[0] += longueur * 8
        symbole = bytes(int(symbole_bits[i:i + 8], 2) for i in range(0, len(symbole_bits), 8)).decode("utf-8")
        return Noeud(caractere=symbole), index_ref[0]
    else:
        # Désérialise récursivement les sous-arbres gauche et droit
        gauche, _ = deserialiser_arbre(bits, index_ref)
        droite, _ = deserialiser_arbre(bits, index_ref)
        return Noeud(gauche=gauche, droite=droite), index_ref[0]


def encoder(texte, table_codes):
    """Encode un texte en une chaîne de bits selon une table de codes."""
    # Remplace chaque caractère par son code binaire
    return ''.join(table_codes[caractere] for caractere in texte)


def ajouter_padding(bits):
    """Ajoute du padding pour aligner les bits sur un multiple de 8."""
    longueur_padding = (8 - len(bits) % 8) % 8
    return f"{longueur_padding:08b}" + bits + "0" * longueur_padding


def retirer_padding(bits):
    """Supprime le padding d'une chaîne de bits."""
    longueur_padding = int(bits[:8], 2)
    return bits[8:len(bits) - longueur_padding]


def bits_vers_octets(bits):
    """Convertit une chaîne de bits en octets."""
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def octets_vers_bits(octets):
    """Convertit des octets en une chaîne de bits."""
    return ''.join(f"{octet:08b}" for octet in octets)


def decoder(bits, racine):
    """Décode une chaîne de bits en texte à l'aide de l'arbre de Huffman."""
    if not racine or not bits:
        return ""

    resultat = []
    noeud_courant = racine
    for bit in bits:
        # Parcours l'arbre selon les bits (0 = gauche, 1 = droite)
        noeud_courant = noeud_courant.gauche if bit == "0" else noeud_courant.droite
        if noeud_courant.caractere is not None:
            # Si une feuille est atteinte, ajoute le caractère au résultat
            resultat.append(noeud_courant.caractere)
            noeud_courant = racine

    return ''.join(resultat)


def compresser(chemin_entree, chemin_sortie):
    """Compresse un fichier texte en fichier binaire avec Huffman."""
    with open(chemin_entree, "r", encoding="utf-8") as fichier:
        texte = fichier.read()

    if not texte:
        # Si le fichier est vide, crée un fichier de sortie vide
        with open(chemin_sortie, "wb") as fichier_sortie:
            fichier_sortie.write(b"")
        return

    # Étapes de la compression : fréquences -> arbre -> codes -> bits -> octets
    frequences = compter_frequences(texte)
    racine = construire_arbre(frequences)
    table_codes = generer_codes(racine)
    bits_arbre = serialiser_arbre(racine)
    bits_donnees = encoder(texte, table_codes)
    bits_complets = ajouter_padding(bits_arbre + bits_donnees)
    octets = bits_vers_octets(bits_complets)

    with open(chemin_sortie, "wb") as fichier_sortie:
        fichier_sortie.write(octets)


def decompresser(chemin_entree, chemin_sortie):
    """Décompresse un fichier binaire en texte avec Huffman."""
    with open(chemin_entree, "rb") as fichier:
        octets = fichier.read()

    bits = retirer_padding(octets_vers_bits(octets))
    index_ref = [0]
    racine, index_apres_arbre = deserialiser_arbre(bits, index_ref)
    texte = decoder(bits[index_apres_arbre:], racine)

    with open(chemin_sortie, "w", encoding="utf-8") as fichier_sortie:
        fichier_sortie.write(texte)


def main():
    parser = argparse.ArgumentParser(description="Compression Huffman classique (avec arbre inclus)")
    parser.add_argument("-e", metavar="input", help="Fichier à compresser")
    parser.add_argument("-d", metavar="input", help="Fichier à décompresser")
    parser.add_argument("-o", metavar="output", required=True, help="Fichier de sortie")
    args = parser.parse_args()

    if args.e:
        compresser(args.e, args.o)
    elif args.d:
        decompresser(args.d, args.o)
    else:
        parser.print_help()
        print("\nSpécifiez soit -e (encode), soit -d (decode).")


if __name__ == "__main__":
    main()