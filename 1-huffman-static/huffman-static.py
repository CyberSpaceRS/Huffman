#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import heapq

# Dictionnaire statique imposé (ne pas modifier)
freq = {
    "a":7, "b":1, "c":3, "d":4, "e":12, "f":1, "g":1, "h":1, "i":6, "j":0,
    "k":0, "l":5, "m":3, "n":6, "o":5, "p":2, "q":0, "r":6, "s":6, "t":6,
    "u":4, "v":1, "w":0, "x":0, "y":0, "z":0, "à":0, "é":2, "è":0, ",":2,
    "-":0, ".":1, ";":0, "!":0, "?":0, "\n":0, "<sp>":15
}

ESCAPE_SYMBOL = "<ESC>"      # symbole d’échappement pour caractères inconnus
ESCAPE_CODE = "1111111"      # code spécifique de 7 bits réservé


# Classe représentant un nœud dans l’arbre de Huffman
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol  # Le caractère (ou None pour les nœuds internes)
        self.freq = freq      # Fréquence du caractère (ou somme des fréquences pour nœuds internes)
        self.left = left      # Fils gauche
        self.right = right    # Fils droit

    def __lt__(self, other):
        # Permet de comparer deux nœuds dans une file de priorité (heapq)
        return self.freq < other.freq


# Construction de l’arbre de Huffman
def build_tree(freq_dict):
    # Copier le dictionnaire des fréquences pour ne pas modifier l’original
    local = freq_dict.copy()
    local[ESCAPE_SYMBOL] = 0.000001  # Ajouter un symbole d’échappement avec un poids minimal non nul

    # Créer une liste de nœuds à partir du dictionnaire (seulement ceux avec une fréquence > 0)
    heap = [Node(s, f) for s, f in local.items() if f > 0]
    heapq.heapify(heap)  # Transformer la liste en un tas binaire (file de priorité)

    # Fusion des nœuds les plus légers jusqu’à obtenir un arbre complet
    while len(heap) > 1:
        a = heapq.heappop(heap)  # Nœud 1 le plus petit
        b = heapq.heappop(heap)  # Nœud 2 le plus petit
        # Créer un nouveau nœud parent avec les deux comme enfants
        heapq.heappush(heap, Node(None, a.freq + b.freq, a, b))

    return heap[0]  # La racine de l’arbre


# Création du dictionnaire (symboles vers du codes binaires)
def build_codes(node, prefix="", table=None):
    if table is None:
        table = {}

    if node.symbol is not None:
        # Cas feuille : on associe le code binaire construit au symbole
        table[node.symbol] = prefix
    else:
        # Récursion à gauche et à droite avec ajout de 0 ou 1
        build_codes(node.left, prefix + "0", table)
        build_codes(node.right, prefix + "1", table)

    return table  # Dictionnaire final {caractère: code_binaire}


# Codage du texte avec prise en charge des caractères inconnus
def encode(text, code_table):
    bits = []

    for char in text:
        if char == " ":
            char = "<sp>"  # Remplace l’espace par le code <sp> selon la table imposée

        if char in code_table:
            bits.append(code_table[char])  # Encodage direct
        else:
            # Caractère inconnu : on utilise le symbole d’échappement
            bits.append(code_table[ESCAPE_SYMBOL])
            utf8_bytes = char.encode("utf-8")
            bits.append(f"{len(utf8_bytes):08b}")  # Longueur UTF-8 sur 8 bits
            for b in utf8_bytes:
                bits.append(f"{b:08b}")  # Chaque octet encodé sur 8 bits

    return ''.join(bits)  # On retourne la chaîne binaire complète


# Ajout du padding (multiple de 8 bits) avec longueur en tête
def pad_bits(bits):
    padding = (8 - len(bits) % 8) % 8  # Nombre de bits à ajouter pour compléter un octet
    return f"{padding:08b}" + bits + "0" * padding  # On préfixe avec la taille du padding


def bits_to_bytes(bits):
    # Découpe les bits par groupes de 8 et transforme chaque groupe en octet
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

# Conversion inverse (fichier compressé → binaire brut)
def bytes_to_bits(b):
    # Transforme chaque octet (byte) en 8 bits (string)
    return ''.join(f"{byte:08b}" for byte in b)

# Suppression du padding en tête du flux binaire
def unpad_bits(bits):
    padding = int(bits[:8], 2)  # On lit les 8 premiers bits pour connaître la taille du padding
    return bits[8:-padding] if padding > 0 else bits[8:]  # On enlève le padding à la fin

# Décodage du flux binaire à partir de l'arbre de Huffman
def decode(bits, root):
    result = []  # Liste pour accumuler les caractères décodés
    i = 0  # Pointeur dans la chaîne de bits
    
    # On parcourt tous les bits jusqu'à la fin
    while i < len(bits):
        node = root  # On commence à la racine de l'arbre de Huffman
        
        # On descend dans l'arbre jusqu'à atteindre une feuille
        while node.symbol is None and i < len(bits):
            # Si le bit est 0, aller à gauche, sinon à droite
            node = node.left if bits[i] == '0' else node.right
            i += 1

        # Si le symbole atteint est un caractère inconnu (échappé)
        if node.symbol == ESCAPE_SYMBOL:
            # Vérifier qu'on a au moins 8 bits pour la longueur du caractère UTF-8
            if i + 8 > len(bits):
                break  # Si pas assez de bits restants, on sort (fichier corrompu ou incomplet)
            
            # Lire la longueur en octets (sur 8 bits)
            length = int(bits[i:i+8], 2)
            i += 8
            
            # Lire les bits correspondant aux octets UTF-8
            byte_str = bits[i:i + 8 * length]
            i += 8 * length

            # Convertir les bits en bytes, puis en caractère UTF-8
            result.append(
                bytes(int(byte_str[j:j+8], 2) for j in range(0, len(byte_str), 8)).decode("utf-8")
            )

        # Si le caractère est "<sp>", on ajoute un espace
        elif node.symbol == "<sp>":
            result.append(" ")

        # Sinon, c’est un caractère connu, on l’ajoute directement
        else:
            result.append(node.symbol)
    
    # On retourne le texte reconstitué
    return ''.join(result)

# Fonction principale de compression
def compress(input_path, output_path):
    # Lire le contenu du fichier texte en UTF-8
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Construire l’arbre de Huffman à partir du dictionnaire statique imposé (avec ESCAPE_SYMBOL)
    root = build_tree(freq)
    
    # Générer la table de codes binaires pour chaque caractère
    codes = build_codes(root)
    
    # Encoder le texte en une suite de bits selon la table de Huffman
    bits = encode(text, codes)
    
    # Ajouter du padding pour que la longueur soit un multiple de 8 bits
    padded = pad_bits(bits)
    
    # Convertir la chaîne de bits en données binaires (bytes)
    byte_data = bits_to_bytes(padded)
    
    # Écrire les données binaires dans un fichier de sortie
    with open(output_path, "wb") as out:
        out.write(byte_data)


# Fonction principale de décompression
def decompress(input_path, output_path):
    # Lire les données binaires du fichier compressé
    with open(input_path, "rb") as f:
        byte_data = f.read()
    
    # Convertir les bytes en chaîne de bits (ex: "01001100...")
    bits = unpad_bits(bytes_to_bits(byte_data))
    
    # Reconstruire l’arbre de Huffman à partir du dictionnaire statique
    root = build_tree(freq)
    
    # Décoder la chaîne de bits en texte à l’aide de l’arbre
    decoded = decode(bits, root)
    
    # Écrire le texte décompressé dans un fichier UTF-8
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decoded)


# Interface ligne de commande
def main():
    parser = argparse.ArgumentParser(description="Huffman statique avec gestion des caractères inconnus")
    parser.add_argument("-e", metavar="input", help="Fichier texte à compresser")
    parser.add_argument("-d", metavar="input", help="Fichier compressé à décompresser")
    parser.add_argument("-o", metavar="output", required=True, help="Fichier de sortie")
    args = parser.parse_args()

    if args.e:
        compress(args.e, args.o)
    elif args.d:
        decompress(args.d, args.o)
    else:
        print("Veuillez spécifier un mode : -e (encode) ou -d (decode).")

if __name__ == "__main__":
    main()
