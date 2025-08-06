*OCR Document Scanner*  :


- Une application OCR avec interface graphique développée en Python, qui permet d’analyser des documents d'identité (Passeports, CIN...) via la reconnaissance de zone MRZ, de les corriger automatiquement et de sauvegarder les résultats dans une base de données SQLite.

  

1.Reconnaissance automatique des zones MRZ à partir d’images ou de fichiers PDF.

2.Extraction des champs : prénom, nom, numéro de document, sexe, date de naissance, date d’expiration, pays, etc.

3.Correction intelligente des noms via une base de données linguistique (NLTK).

4.Sauvegarde des documents analysés dans une base SQLite.

5.Historique complet des documents scannés.

6.Supporte les images (JPEG/PNG) et les PDF (extraction automatique de l’image de la première



###  Structure des fonctions principales

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
