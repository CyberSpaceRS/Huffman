#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

freq = {"a":7, "b":1, "c":3, "d":4, "e":12, "f":1, "g":1, "h":1, "i":6, "j":0, 
        "k":0, "l":5, "m":3, "n":6, "o":5, "p":2, "q":0, "r":6, "s":6, "t":6, 
        "u":4, "v":1, "w":0, "x":0, "y":0, "z":0, "à":0, "é":2, "è":0, ",":2, 
        "-":0, ".":1, ";":0, "!":0, "?":0, "\n":0, "<sp>":15}

ESCAPE_SYMBOL = "<ESC>"

class Noeud:
    def __init__(self, frequence, caractere=None, gauche=None, droite=None, parent=None):
        self._frequence = frequence
        self._caractere = caractere
        self._gauche = gauche
        self._droite = droite
        self._parent = parent

    def est_feuille(self):
        return self._gauche is None and self._droite is None

def construire_arbre(freq):
    freq = freq.copy()
    freq[ESCAPE_SYMBOL] = 0.000001  # Assure sa présence
    noeuds = [Noeud(f, c) for c, f in freq.items() if f > 0]
    while len(noeuds) > 1:
        noeuds.sort(key=lambda n: n._frequence)
        g = noeuds.pop(0)
        d = noeuds.pop(0)
        parent = Noeud(g._frequence + d._frequence, gauche=g, droite=d)
        g._parent = parent
        d._parent = parent
        noeuds.append(parent)
    return noeuds[0]

def generer_codes(noeud, prefix="", table=None):
    if table is None:
        table = {}
    if noeud.est_feuille():
        table[noeud._caractere] = prefix
    else:
        generer_codes(noeud._gauche, prefix + "0", table)
        generer_codes(noeud._droite, prefix + "1", table)
    return table

def encoder(texte, table):
    bits = []
    for c in texte:
        if c == " ":
            c = "<sp>"
        if c in table:
            bits.append(table[c])
        else:
            bits.append(table[ESCAPE_SYMBOL])
            utf = c.encode("utf-8")
            bits.append(f"{len(utf):08b}")
            bits += [f"{b:08b}" for b in utf]
    return ''.join(bits)

def decoder(bits, racine):
    i = 0
    resultat = []
    while i < len(bits):
        noeud = racine
        while not noeud.est_feuille() and i < len(bits):
            noeud = noeud._gauche if bits[i] == "0" else noeud._droite
            i += 1
        if noeud._caractere == ESCAPE_SYMBOL:
            longueur = int(bits[i:i+8], 2)
            i += 8
            octets = bytes(int(bits[i+j:i+j+8], 2) for j in range(0, longueur*8, 8))
            i += longueur * 8
            resultat.append(octets.decode("utf-8"))
        elif noeud._caractere == "<sp>":
            resultat.append(" ")
        else:
            resultat.append(noeud._caractere)
    return ''.join(resultat)

def bits_vers_octets(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def octets_vers_bits(b):
    return ''.join(f"{byte:08b}" for byte in b)

def ajouter_padding(bits):
    pad_len = (8 - len(bits) % 8) % 8
    return f"{pad_len:08b}" + bits + "0" * pad_len

def retirer_padding(bits):
    pad_len = int(bits[:8], 2)
    return bits[8:-pad_len] if pad_len > 0 else bits[8:]

def compresser(entree, sortie):
    with open(entree, "r", encoding="utf-8") as f:
        texte = f.read()
    racine = construire_arbre(freq)
    codes = generer_codes(racine)
    bits = encoder(texte, codes)
    padded = ajouter_padding(bits)
    with open(sortie, "wb") as f:
        f.write(bits_vers_octets(padded))

def decompresser(entree, sortie):
    with open(entree, "rb") as f:
        octets = f.read()
    bits = retirer_padding(octets_vers_bits(octets))
    racine = construire_arbre(freq)
    texte = decoder(bits, racine)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(texte)

def main():
    parser = argparse.ArgumentParser(description="Huffman statique avec symboles inconnus.")
    parser.add_argument("-e", help="Fichier texte à compresser")
    parser.add_argument("-d", help="Fichier .huf à décompresser")
    parser.add_argument("-o", required=True, help="Fichier de sortie")
    args = parser.parse_args()

    if args.e:
        compresser(args.e, args.o)
    elif args.d:
        decompresser(args.d, args.o)
    else:
        print("Spécifiez -e pour encoder ou -d pour décoder.")

if __name__ == "__main__":
    main()
