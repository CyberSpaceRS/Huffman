#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict

# Classe représentant un nœud de l’arbre de Huffman
class Node:
    def __init__(self, symbol=None, weight=0, parent=None, left=None, right=None, number=0):
        self.symbol = symbol      # Caractère (None pour NYT ou nœuds internes)
        self.weight = weight      # Poids du nœud (nombre d’occurrences)
        self.parent = parent      # Nœud parent
        self.left = left          # Enfant gauche
        self.right = right        # Enfant droit
        self.number = number      # Numéro unique (utilisé pour les échanges de nœuds)

# Classe principale pour le codage Huffman adaptatif (FGK algorithm)
class AdaptiveHuffman:
    def __init__(self):
        self.NYT = Node(symbol=None, weight=0, number=512)  # Noeud NYT (Not Yet Transmitted)
        self.root = self.NYT
        self.nodes = {None: self.NYT}          # Table de tous les nœuds (par symboles)
        self.symbol_table = {}                 # Table des symboles rencontrés

    # Retourne le code binaire d’un nœud à partir de la racine
    def get_code(self, node):
        code = ""
        current = node
        while current.parent:
            if current.parent.left == current:
                code = "0" + code
            else:
                code = "1" + code
            current = current.parent
        return code

    # Échange les positions de deux nœuds
    def swap(self, node1, node2):
        if not node1 or not node2:
            return
        if node1.parent == node2.parent:
            if node1.parent.left == node1:
                node1.parent.left, node1.parent.right = node2, node1
            else:
                node1.parent.right, node1.parent.left = node2, node1
        else:
            p1, p2 = node1.parent, node2.parent
            if p1.left == node1:
                p1.left = node2
            else:
                p1.right = node2
            if p2.left == node2:
                p2.left = node1
            else:
                p2.right = node1
            node1.parent, node2.parent = p2, p1
        node1.number, node2.number = node2.number, node1.number

    # Met à jour l’arbre après insertion d’un caractère
    def update_tree(self, node):
        while node:
            # Recherche le nœud le plus haut avec le même poids pour un éventuel échange
            max_number = node.number
            max_node = node
            stack = [self.root]
            while stack:
                n = stack.pop()
                if n.weight == node.weight and n.number > max_number and n != node and n != node.parent:
                    max_node = n
                    max_number = n.number
                if n.right:
                    stack.append(n.right)
                if n.left:
                    stack.append(n.left)
            if max_node != node:
                self.swap(node, max_node)
            node.weight += 1
            node = node.parent

    # Encode une chaîne de caractères en bits (compression)
    def encode(self, text):
        output_bits = ""
        for char in text:
            if char in self.symbol_table:
                # Si symbole connu, on encode selon l’arbre
                node = self.symbol_table[char]
                output_bits += self.get_code(node)
            else:
                # Sinon, on encode le NYT suivi du code UTF-8 du caractère
                nyt_code = self.get_code(self.NYT)
                utf = char.encode("utf-8")
                bin_utf = f"{len(utf):08b}" + ''.join(f"{b:08b}" for b in utf)
                output_bits += nyt_code + bin_utf

                # Ajout du nouveau symbole à l’arbre
                new_NYT = Node(symbol=None, weight=0, number=self.NYT.number - 2)
                new_leaf = Node(symbol=char, weight=1, number=self.NYT.number - 1)
                self.NYT.left = new_NYT
                self.NYT.right = new_leaf
                new_NYT.parent = self.NYT
                new_leaf.parent = self.NYT

                self.symbol_table[char] = new_leaf
                self.NYT = new_NYT
                self.update_tree(new_leaf.parent)
                continue
            self.update_tree(self.symbol_table[char])
        return output_bits

    # Decode une suite de bits en texte (décompression)
    def decode(self, bits):
        i = 0
        node = self.root
        output = []
        while i < len(bits):
            if node.left is None and node.right is None:
                if node.symbol is None:
                    # Lecture du caractère UTF-8 encodé après un NYT
                    length = int(bits[i:i+8], 2)
                    i += 8
                    byte_str = bits[i:i+8*length]
                    i += 8 * length
                    utf8_char = bytes(int(byte_str[j:j+8], 2) for j in range(0, len(byte_str), 8)).decode("utf-8")

                    # Mise à jour de l’arbre avec le nouveau symbole
                    new_NYT = Node(symbol=None, weight=0, number=self.NYT.number - 2)
                    new_leaf = Node(symbol=utf8_char, weight=1, number=self.NYT.number - 1)
                    self.NYT.left = new_NYT
                    self.NYT.right = new_leaf
                    new_NYT.parent = self.NYT
                    new_leaf.parent = self.NYT

                    self.symbol_table[utf8_char] = new_leaf
                    self.NYT = new_NYT
                    self.update_tree(new_leaf.parent)
                    output.append(utf8_char)
                else:
                    output.append(node.symbol)
                    self.update_tree(node)
                node = self.root
                continue
            node = node.left if bits[i] == "0" else node.right
            i += 1
        return ''.join(output)

# Padding pour aligner sur 8 bits
def pad(bits):
    pad_len = (8 - len(bits) % 8) % 8
    return f"{pad_len:08b}" + bits + "0" * pad_len

def unpad(bits):
    pad_len = int(bits[:8], 2)
    return bits[8:-pad_len] if pad_len > 0 else bits[8:]

# Conversion binaire ↔ octets
def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def bytes_to_bits(b):
    return ''.join(f"{byte:08b}" for byte in b)

# Fonction de compression
def compress(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    huff = AdaptiveHuffman()
    bitstring = huff.encode(text)
    padded = pad(bitstring)
    with open(output_path, "wb") as f:
        f.write(bits_to_bytes(padded))

# Fonction de décompression
def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        byte_data = f.read()
    bits = unpad(bytes_to_bits(byte_data))
    huff = AdaptiveHuffman()
    text = huff.decode(bits)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

# Entrée ligne de commande
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", help="Fichier à compresser")
    parser.add_argument("-d", help="Fichier à décompresser")
    parser.add_argument("-o", required=True, help="Fichier de sortie")
    args = parser.parse_args()

    if args.e:
        compress(args.e, args.o)
    elif args.d:
        decompress(args.d, args.o)
    else:
        print("Veuillez spécifier -e ou -d.")

if __name__ == "__main__":
    main()
