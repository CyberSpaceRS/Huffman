
# 📦 Projet de compression de texte — Algorithme de Huffman

Ce projet implémente trois variantes de l’algorithme de Huffman pour la compression de texte :

- 🔒 **Huffman Statique** — dictionnaire fixe connu à l'avance
- 📐 **Huffman Classique** — dictionnaire dynamique inclus dans le fichier compressé
- 🌊 **Huffman Streaming (Adaptatif)** — dictionnaire construit en temps réel au fil du flux

## 🗂 Arborescence du projet

```

.
├── le-horla.txt                   # Fichier original à compresser
├── le-horla.huf                  # Fichier compressé (sortie)
├── le-horla-decompressed.txt     # Fichier après décompression
├── README.md
├── rapport.pdf                   # Rapport du projet
│
├── 1-huffman-static/
│   └── huffman-static.py
│
├── 2-huffman-classic/
│   └── huffman-classic.py
│
└── 3-huffman-streaming/
├── huffman-streaming.py
└── demo/
└── huffman-streaming-demo.py

````

---

## 🚀 Utilisation

Tous les scripts sont utilisables en ligne de commande via `python3`.

### 1️⃣ Huffman Statique

Compression avec un dictionnaire de fréquences fixe (inspiré de Wikipédia).  
⚠️ Les caractères inconnus sont encodés en UTF-8 avec un symbole d’échappement.

```bash
# Compression
python3 1-huffman-static/huffman-static.py -e le-horla.txt -o le-horla.huf

# Décompression
python3 1-huffman-static/huffman-static.py -d le-horla.huf -o le-horla-decompressed.txt
````

---

### 2️⃣ Huffman Classique

Compression dynamique avec inclusion de l’arbre Huffman dans le fichier compressé.

```bash
# Compression
python3 2-huffman-classic/huffman-classic.py -e le-horla.txt -o le-horla.huf

# Décompression
python3 2-huffman-classic/huffman-classic.py -d le-horla.huf -o le-horla-decompressed.txt
```

---

### 3️⃣ Huffman Streaming (Adaptatif)

Compression en temps réel sans connaissance préalable du dictionnaire.
L'arbre évolue au fil du flux d'entrée (implémentation basée sur [Adaptive Huffman Coding](https://en.wikipedia.org/wiki/Adaptive_Huffman_coding)).

```bash
# Compression
python3 3-huffman-streaming/huffman-streaming.py -e le-horla.txt -o le-horla.huf

# Décompression
python3 3-huffman-streaming/huffman-streaming.py -d le-horla.huf -o le-horla-decompressed.txt
```

Un fichier de démonstration est disponible :

```bash
python3 3-huffman-streaming/demo/huffman-streaming-demo.py
```

---

## 🧪 Tests & Validation

* Tous les fichiers compressés peuvent être décompressés avec exactitude.
* Comparaison possible avec `diff` :

```bash
diff le-horla.txt le-horla-decompressed.txt
```

Aucune sortie signifie que la compression/décompression a été **bit à bit fidèle** ✅
