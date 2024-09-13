import sqlite3
import json
import os
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def init_db():
    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS examinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        exam_date DATE NOT NULL,
        exam_type TEXT NOT NULL,
        result REAL NOT NULL,
        unit TEXT NOT NULL,
        reference_range TEXT
    )
    ''')
    conn.commit()
    conn.close()

def load_json_files(folder_path):
    # Create the Esami directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                data = json.load(file)
                patient_name = data.get('paziente') or data.get('nome_paziente')
                exam_date = data['data']
                for exam in data['esami']:
                    if 'sotto_esami' in exam:
                        for sub_exam in exam['sotto_esami']:
                            insert_examination(cursor, patient_name, exam_date, sub_exam)
                    else:
                        insert_examination(cursor, patient_name, exam_date, exam)

    conn.commit()
    conn.close()

def insert_examination(cursor, patient_name, exam_date, exam):
    exam_type = exam['nome'] if 'nome' in exam else exam['tipo_di_esame']
    result = exam.get('risultato')
    if result is not None and result != "":
        try:
            result = float(result)
            unit = exam.get('unita_di_misura', '')
            reference_range = exam.get('valori_di_riferimento', '')
            cursor.execute('''
            INSERT INTO examinations (patient_name, exam_date, exam_type, result, unit, reference_range)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_name, exam_date, exam_type, result, unit, reference_range))
        except ValueError:
            print(f"Skipping non-numeric result for {exam_type}: {result}")
