# OCR Document Scanner

**Une application OCR avec interface graphique développée en Python, permettant d’analyser des documents d'identité (Passeports, CIN...) via la reconnaissance de zone MRZ, de les corriger automatiquement et de sauvegarder les résultats dans une base de données SQLite.**

---

##  Fonctionnalités principales

1. Reconnaissance automatique des zones MRZ à partir d’images ou de fichiers PDF.  
2. Extraction des champs : prénom, nom, numéro de document, sexe, date de naissance, date d’expiration, pays, etc.  
3. Correction intelligente des noms via une base de données linguistique (NLTK).  
4. Sauvegarde des documents analysés dans une base SQLite.  
5. Historique complet des documents scannés.  
6. Support des formats image (JPEG/PNG) et PDF (extraction automatique de la première page).

---

##  Structure des fonctions principales

| Partie | Description |
|--------|-------------|
| `Loader` | Classe pour charger les fichiers (PDF ou image) |
| `Document` | Modèle de données pour représenter un document OCR extrait |
| `get_content()` | Lance Tesseract en sous-processus pour extraire le texte brut |
| `parse_mrz()` | Identifie automatiquement si le MRZ est un passeport ou une CIN |
| `parse_passport()` / `parse_id_card()` | Analyse la structure du MRZ ligne par ligne |
| `correct_name_ml()` | Corrige les noms grâce à une base NLTK (`nltk.corpus.names`) |
| `init_db()` / `save_document_to_db()` / `get_all_documents()` | Gère la base de données SQLite (`ocr_documents.db`) |
| `stringify_date()` | Formate les dates de naissance et d’expiration à partir du MRZ |
| `get_id_passport()` / `get_cnie()` | Détecte et formate les numéros de document |
| `find_closest_sex()` | Localise la position du sexe (M/F) dans le MRZ de manière robuste |

---

##  Interface graphique (GUI)

L'application dispose d'une interface simple et moderne construite avec **Tkinter**. Elle permet de :

- Importer une image ou un PDF contenant une zone MRZ.
- Lancer automatiquement l'OCR et parser les informations détectées.
- Afficher et enregistrer les résultats avec l'image associée.
- Consulter l'historique des documents analysés.
- Supprimer des éléments de l'historique.

---

##  Importation des images et extraction des données

### Exemple 1 (Passeport)

**passport1 :**  
![passport1](https://github.com/user-attachments/assets/0e3ae98c-9587-49d7-a209-e8f8858e8868)

**Résultat :**  
![result1](https://github.com/user-attachments/assets/b6cb2cda-e602-4289-b858-0d497784666a)

**passport2 :**  
![passport2](https://github.com/user-attachments/assets/b053423f-b6ef-4f7a-9181-ed35009752dd)

**Résultat :**  
![result2](https://github.com/user-attachments/assets/464921c1-d5e6-46f3-8548-f2bb02f0a57a)

---

### Exemple 2 (Carte nationale d'identité - CIN marocaine)

**Carte :**  
![id_maroc](https://github.com/user-attachments/assets/61d1f3cd-78ef-445f-8999-f5c71f503bc9)

**Résultat :**  
![id_result](https://github.com/user-attachments/assets/10df2143-919f-4d83-b396-3b79ce7b6041)

---

##  Partie Historique

La section **Historique** permet d’afficher la liste des documents précédemment analysés et enregistrés dans la base SQLite (`ocr_documents.db`).

Pour chaque document, l’interface affiche :

- Une miniature de l’image du document (si disponible).
- Les informations extraites : nom, prénom, type, numéro, etc.
- Un bouton "Supprimer" pour retirer l’entrée de la base de données.
- La possibilité de cliquer sur un élément pour réafficher les détails complets dans la vue principale.

![historique](https://github.com/user-attachments/assets/097ef819-0f99-4ac9-bd01-bc6f846888c6)

---

##  Limites connues

| Limite | Description |
|--------|-------------|
| Qualité d’image | Une mauvaise qualité d’image (floue, sombre, inclinée) peut fausser la reconnaissance OCR. |
| Numéro de document incorrect | Des caractères erronés comme `$`, `%`, `ddd` peuvent apparaître dans le champ *Document Number* à cause d’une mauvaise capture. |
| Correction de nom limitée | Le correcteur basé sur `nltk.corpus.names` ne couvre pas tous les noms étrangers ou rares. |
| MRZ incomplète ou absente | Si la zone MRZ est mal cadrée, absente ou tronquée, l’analyse échoue ou est incomplète. |
| PDF multi-pages non gérés | Seule la **première page** est extraite dans les fichiers PDF (via `extract_first_jpeg_in_pdf`). |

---

##  Pistes d'amélioration

| Solution | Description |
|----------|-------------|
| Prétraitement d’image | Appliquer des filtres d’amélioration : binarisation, redressement, débruitage avant OCR. |
| Nettoyage post-OCR | Supprimer les symboles indésirables (`[^A-Z0-9]`) dans les champs critiques comme *Document Number*. |
| Amélioration des noms | Utiliser une base de prénoms enrichie (multi-langues) ou un modèle de correction basé sur l’IA. |
| Ajustement Tesseract | Tester plusieurs `--psm` (Page Segmentation Mode) selon le type de document ou image. |
| Support PDF avancé | Extraire toutes les pages PDF ou détecter automatiquement celle contenant la MRZ. |

---
