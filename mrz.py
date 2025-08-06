import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import numpy as np
import datetime
import subprocess
import webbrowser
import sqlite3
from PassportEye.passporteye.util.pdf import extract_first_jpeg_in_pdf
from skimage import io as skimage_io
import nltk
from nltk.corpus import names
from difflib import get_close_matches

nltk.download('names')
name_list = names.words()

DB_NAME = "ocr_documents.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT,
            country_code TEXT,
            first_name TEXT,
            last_name TEXT,
            document_number TEXT,
            sex TEXT,
            birth_date TEXT,
            expire_date TEXT,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_document_to_db(data, image_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (
            document_type, country_code, first_name,
            last_name, document_number, sex,
            birth_date, expire_date, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["Document Type"],
        data["Country Code"],
        data["First Name"],
        data["Last Name"],
        data["Document Number"],
        data["Sex"],
        data["Birth Date"],
        data["Expire Date"],
        image_path
    ))
    conn.commit()
    conn.close()

def delete_document_from_db(document_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()

def get_all_documents():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return records

def delete_document_from_db(document_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
class Loader:
    def __init__(self, file=None):
        self.file = file

    def __call__(self):
        if isinstance(self.file, str):
            if self.file.lower().endswith('.pdf'):
                with open(self.file, 'rb') as f:
                    img_data = extract_first_jpeg_in_pdf(f)
                if img_data is None:
                    return None
                return skimage_io.imread(img_data, as_gray=False)
            else:
                return skimage_io.imread(self.file, as_gray=False)
        return None

class Document:
    def __init__(self, document_type, country_code, first_name, last_name, document_number, sex, birth_date, expire_date):
        self.document_type = self.normalize_document_type(document_type)
        self.country_code = country_code
        self.first_name = first_name
        self.last_name = last_name
        self.document_number = document_number
        self.sex = sex
        self.birth_date = birth_date
        self.expire_date = expire_date

    def normalize_document_type(self, raw_type):
        raw = raw_type.upper()
        if any(x in raw for x in ["P", "P>", "PP", "PI"]):
            return "Passport"
        elif any(x in raw for x in ["I", "ID", "D"]):
            return "Identit\u00e9"
        return raw_type

    def to_dict(self):
        return {
            "Document Type": self.document_type,
            "Country Code": self.country_code,
            "First Name": self.first_name,
            "Last Name": self.last_name,
            "Document Number": self.document_number,
            "Sex": self.sex,
            "Birth Date": self.birth_date,
            "Expire Date": self.expire_date
        }

def correct_name_ml(name):
    name = name.strip().capitalize()
    matches = get_close_matches(name, name_list, n=1, cutoff=0.8)
    return matches[0] if matches else name

def get_content(image_path):
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '--psm', '4', '--oem', '1'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e)

def parse_mrz(mrz_text):
    lines = mrz_text.split('\n')
    lines = [line.replace('\u003c', '<') for line in lines]
    if len(lines) == 2:
        return parse_passport(lines[0], lines[1])
    elif len(lines) == 3:
        return parse_id_card(lines[0], lines[1], lines[2])
    else:
        raise ValueError("MRZ non reconnue")

def parse_passport(line1, line2):
    doc_type = my_trim(line1[0:2])
    country_code = my_trim(line1[2:5])
    names = line1[5:]
    first_name, last_name = get_names(names)
    doc_number = get_id_passport(line2)
    sex_index = find_closest_sex(line2, 20)
    sex, birth_date, expire_date = None, None, None
    if sex_index != -1:
        sex = line2[sex_index]
        birth_date = stringify_date(line2[sex_index-7:sex_index-1], "birth")
        expire_date = stringify_date(line2[sex_index+1:sex_index+7], "expire")
    return Document(doc_type, country_code, first_name, last_name, doc_number, sex, birth_date, expire_date)

def parse_id_card(line1, line2, line3):
    doc_type = my_trim(line1[0:2])
    country_code = my_trim(line1[2:5])
    first_name, last_name = get_names_cin(line3)
    doc_number = get_cnie(line1)
    sex_index = find_closest_sex(line2, 7)
    sex, birth_date, expire_date = None, None, None
    if sex_index != -1:
        sex = line2[sex_index]
        birth_date = stringify_date(line2[sex_index-7:sex_index-1], "birth")
        expire_date = stringify_date(line2[sex_index+1:sex_index+7], "expire")
    return Document(doc_type, country_code, first_name, last_name, doc_number, sex, birth_date, expire_date)

def get_names(text):
    parts = text.split("<<")
    last_name = parts[0].replace('<', ' ').strip() if parts else ""
    first_name = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    return correct_name_ml(first_name), correct_name_ml(last_name)

def get_names_cin(text):
    parts = text.split("<<")
    if len(parts) >= 2:
        last_name = parts[0].replace('<', ' ').strip()
        first_name = parts[1].replace('<', ' ').strip()
    elif len(parts) == 1:
        last_name = parts[0].replace('<', ' ').strip()
        first_name = ""
    else:
        last_name = first_name = ""
    return correct_name_ml(first_name), correct_name_ml(last_name)

def stringify_date(text, date_type):
    if len(text) != 6:
        return "Invalid"
    year = int(text[:2])
    month = text[2:4]
    day = text[4:]
    current_year = datetime.datetime.now().year % 100
    if date_type == "expire":
        year += 2000
    elif date_type == "birth":
        year += 1900 if year > current_year else 2000
    return f"{day}/{month}/{year}"

def my_trim(text):
    return text.replace('<', ' ').strip()

def get_id_passport(line):
    return line[:9].replace('<', '').strip()

def find_closest_sex(line, index):
    i, j = index, index
    while True:
        if i >= len(line) and j < 0:
            return -1
        if i < len(line) and line[i] in 'FM':
            return i
        if j >= 0 and line[j] in 'FM':
            return j
        i += 1
        j -= 1

def get_cnie(text):
    parts = text.replace('<', ' ').strip().split()
    raw_candidate = ''.join(parts[1:]) if len(parts) > 1 else text

    index_1 = raw_candidate.find("1")
    if index_1 != -1:
        candidate = raw_candidate[index_1:]
        if candidate.startswith("1"):
            candidate = "I" + candidate[1:]

    index_u = raw_candidate.find("U")
    if index_u != -1:
        candidate = raw_candidate[index_u:]

    return candidate if 'candidate' in locals() else "INCONNU"


