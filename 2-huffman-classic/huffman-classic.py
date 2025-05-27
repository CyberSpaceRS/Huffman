#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import heapq
from collections import Counter

# Classe représentant un nœud de l’arbre de Huffman
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol      # caractère (feuille) ou None (nœud interne)
        self.freq = freq          # fréquence du caractère
        self.left = left          # sous-arbre gauche
        self.right = right        # sous-arbre droit
    def __lt__(self, other):
        return self.freq < other.freq  # pour comparaison dans la heap

# Construit un arbre de Huffman à partir d’un dictionnaire de fréquences
def build_tree(freq_dict):
    heap = [Node(s, f) for s, f in freq_dict.items()]  # crée des nœuds pour chaque caractère
    heapq.heapify(heap)  # transforme en tas min
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        heapq.heappush(heap, Node(None, n1.freq + n2.freq, n1, n2))
    return heap[0]

# Construit la table de codage de Huffman depuis l’arbre
def build_codes(node, prefix="", table=None):
    if table is None:
        table = {}
    if node.symbol is not None:
        table[node.symbol] = prefix  # feuille → code binaire
    else:
        build_codes(node.left, prefix + "0", table)
        build_codes(node.right, prefix + "1", table)
    return table

# Sérialise l’arbre sous forme binaire pour l’inclure dans le fichier compressé
def serialize_tree(node):
    if node.symbol is not None:
        encoded = node.symbol.encode("utf-8")
        return "1" + format(len(encoded), "08b") + ''.join(f"{b:08b}" for b in encoded)
    return "0" + serialize_tree(node.left) + serialize_tree(node.right)

# Désérialise un arbre Huffman depuis une chaîne de bits
def deserialize_tree(bits, index=0):
    if bits[index] == "1":
        length = int(bits[index+1:index+9], 2)
        index += 9
        data = bytes(int(bits[index+i:index+i+8], 2) for i in range(0, 8 * length, 8))
        symbol = data.decode("utf-8")
        index += 8 * length
        return Node(symbol=symbol), index
    index += 1
    left, i1 = deserialize_tree(bits, index)
    right, i2 = deserialize_tree(bits, i1)
    return Node(left=left, right=right), i2

# Encode le texte avec la table de Huffman
def encode(text, code_table):
    return ''.join(code_table[c] for c in text)

# Ajoute un padding pour garantir un alignement sur 8 bits
def pad_bits(bits):
    pad_len = (8 - len(bits) % 8) % 8
    return f"{pad_len:08b}" + bits + "0" * pad_len

# Supprime le padding lors de la lecture
def unpad_bits(bits):
    pad_len = int(bits[:8], 2)
    return bits[8:-pad_len] if pad_len > 0 else bits[8:]

# Convertit une chaîne de bits en octets
def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

# Convertit une séquence d’octets en chaîne de bits
def bytes_to_bits(b):
    return ''.join(f"{byte:08b}" for byte in b)

# Décodage d’une chaîne de bits à l’aide de l’arbre
def decode(bits, root):
    result = []
    i = 0
    while i < len(bits):
        current = root
        while current.symbol is None:
            current = current.left if bits[i] == "0" else current.right
            i += 1
        result.append(current.symbol)
    return ''.join(result)

# Fonction principale de compression
def compress(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    freq = Counter(text)                  # calcule les fréquences réelles
    root = build_tree(freq)              # construit l’arbre Huffman
    code_table = build_codes(root)       # génère la table de codage
    tree_bits = serialize_tree(root)     # encode l’arbre
    data_bits = encode(text, code_table) # encode les données
    full_bits = tree_bits + data_bits    # concatène les deux
    padded = pad_bits(full_bits)         # ajoute le padding
    byte_data = bits_to_bytes(padded)    # transforme en octets
    with open(output_path, "wb") as out:
        out.write(byte_data)

# Fonction principale de décompression
def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        byte_data = f.read()
    bit_str = bytes_to_bits(byte_data)
    bits = unpad_bits(bit_str)
    root, index = deserialize_tree(bits)         # reconstruit l’arbre
    text = decode(bits[index:], root)            # décode les données
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

# Interface CLI
def main():
    parser = argparse.ArgumentParser(description="Huffman Classique Compression")
    parser.add_argument("-e", metavar="input", help="Fichier à compresser")
    parser.add_argument("-d", metavar="input", help="Fichier à décompresser")
    parser.add_argument("-o", metavar="output", required=True, help="Fichier de sortie")
    args = parser.parse_args()

    if args.e:
        compress(args.e, args.o)
    elif args.d:
        decompress(args.d, args.o)
    else:
        print("Spécifiez soit -e (encode), soit -d (decode).")

if __name__ == "__main__":
    main()
