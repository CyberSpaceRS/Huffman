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

# Structure d’un nœud dans l’arbre de Huffman
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

# Construction de l’arbre de Huffman
def build_tree(freq_dict):
    local = freq_dict.copy()
    local[ESCAPE_SYMBOL] = 0.000001  # assurer sa présence même à faible poids
    heap = [Node(s, f) for s, f in local.items() if f > 0]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(None, a.freq + b.freq, a, b))
    return heap[0]

# Création du dictionnaire (symboles → codes binaires)
def build_codes(node, prefix="", table=None):
    if table is None:
        table = {}
    if node.symbol is not None:
        table[node.symbol] = prefix
    else:
        build_codes(node.left, prefix + "0", table)
        build_codes(node.right, prefix + "1", table)
    return table

# Codage du texte avec prise en charge des caractères inconnus
def encode(text, code_table):
    bits = []
    for char in text:
        if char == " ":
            char = "<sp>"
        if char in code_table:
            bits.append(code_table[char])
        else:
            # Code d’échappement + longueur + octets UTF-8
            bits.append(code_table[ESCAPE_SYMBOL])
            utf8_bytes = char.encode("utf-8")
            bits.append(f"{len(utf8_bytes):08b}")
            for b in utf8_bytes:
                bits.append(f"{b:08b}")
    return ''.join(bits)

# Ajout du padding (multiple de 8 bits) avec longueur en tête
def pad_bits(bits):
    padding = (8 - len(bits) % 8) % 8
    return f"{padding:08b}" + bits + "0" * padding

def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

# Conversion inverse (fichier compressé → binaire brut)
def bytes_to_bits(b):
    return ''.join(f"{byte:08b}" for byte in b)

def unpad_bits(bits):
    padding = int(bits[:8], 2)
    return bits[8:-padding] if padding > 0 else bits[8:]

# Décodage du flux binaire
def decode(bits, root):
    result = []
    i = 0
    while i < len(bits):
        node = root
        while node.symbol is None and i < len(bits):
            node = node.left if bits[i] == '0' else node.right
            i += 1
        if node.symbol == ESCAPE_SYMBOL:
            if i + 8 > len(bits): break
            length = int(bits[i:i+8], 2)
            i += 8
            byte_str = bits[i:i + 8 * length]
            i += 8 * length
            result.append(bytes(int(byte_str[j:j+8], 2) for j in range(0, len(byte_str), 8)).decode("utf-8"))
        elif node.symbol == "<sp>":
            result.append(" ")
        else:
            result.append(node.symbol)
    return ''.join(result)

# Fonction principale de compression
def compress(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    root = build_tree(freq)
    codes = build_codes(root)
    bits = encode(text, codes)
    padded = pad_bits(bits)
    byte_data = bits_to_bytes(padded)
    with open(output_path, "wb") as out:
        out.write(byte_data)

# Fonction principale de décompression
def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        byte_data = f.read()
    bits = unpad_bits(bytes_to_bits(byte_data))
    root = build_tree(freq)
    decoded = decode(bits, root)
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
