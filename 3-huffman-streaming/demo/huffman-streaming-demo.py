#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os

# Chemins
base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(base_dir, ".."))
script_path = os.path.join(root_dir, "huffman-streaming.py")
demo_input = os.path.join(base_dir, "demo-input.txt")
demo_output = os.path.join(base_dir, "demo-output.txt")
compressed_file = os.path.join(base_dir, "demo-output.huf")

# Étape 1 : écrire un petit texte pour tester
demo_text = """Depuis plusieurs décennies, les montagnes russes ont connu une évolution spectaculaire.
Des wooden coasters classiques en bois aux hypercoasters de plus de 60 mètres de haut,
les parcs d'attractions rivalisent d'ingéniosité pour proposer des sensations toujours plus extrêmes.
Des éléments comme les launchs magnétiques, les inversions en série et les drops à 90° font désormais partie intégrante de l'expérience.

Des parcs comme Europa-Park, Cedar Point ou le parc Astérix repoussent chaque année les limites de la technologie
pour offrir des coasters toujours plus rapides, plus fluides et immersifs. Le public passionné suit de près les classements internationaux,
comme le fameux Golden Ticket Awards, qui récompense les meilleures attractions au monde.

Le coaster n'est plus seulement un manège, c'est une œuvre d'ingénierie et de storytelling, 
capable de mêler vitesse, airtime et narration dans une seule expérience mémorable."""

with open(demo_input, "w", encoding="utf-8") as f:
    f.write(demo_text)

# Étape 2 : compression
print("Compression en cours...")
subprocess.run(["python3", script_path, "-e", demo_input, "-o", compressed_file], check=True)

# Étape 3 : décompression
print("Décompression en cours...")
subprocess.run(["python3", script_path, "-d", compressed_file, "-o", demo_output], check=True)

# Étape 4 : lecture du fichier décompressé
with open(demo_output, "r", encoding="utf-8") as f:
    result = f.read()

print("\nTexte décompressé :\n")
print(result)

# Nettoyage (optionnel)
# os.remove(demo_input)
# os.remove(demo_output)
# os.remove(compressed_file)
