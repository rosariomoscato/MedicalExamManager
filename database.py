import psycopg2
import json
import os
import gettext
from datetime import datetime
from psycopg2 import pool

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.environ.get('PGDATABASE'),
    'user': os.environ.get('PGUSER'),
    'password': os.environ.get('PGPASSWORD'),
    'host': os.environ.get('PGHOST'),
    'port': os.environ.get('PGPORT')
}

def get_db_connection():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS examinations (
                id SERIAL PRIMARY KEY,
                patient_name TEXT NOT NULL,
                exam_date DATE NOT NULL,
                exam_type TEXT NOT NULL,
                result REAL NOT NULL,
                unit TEXT NOT NULL,
                reference_range TEXT
            )
            ''')
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while initializing database:", error)
    finally:
        if conn:
            conn.close()

def empty_examinations_table():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM examinations')
        conn.commit()
        print("Examinations table has been emptied.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error occurred while emptying examinations table: {error}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def load_json_files(folder_path):
    empty_examinations_table()
    print(f"Starting to load JSON files from folder: {folder_path}")

    conn = get_db_connection()
    if conn is None:
        return

    try:
        # Create the Esami directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        print(f"Files in the folder: {os.listdir(folder_path)}")

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                print(f"Processing file: {filename}")
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        print(f"Successfully loaded JSON data from file: {filename}")
                        patient_name = data.get('paziente') or data.get('nome_paziente')
                        exam_date = data['data']
                        for exam in data['esami']:
                            if 'sotto_esami' in exam:
                                for sub_exam in exam['sotto_esami']:
                                    insert_examination(conn, patient_name, exam_date, sub_exam)
                            else:
                                insert_examination(conn, patient_name, exam_date, exam)
                    print(f"Finished processing file: {filename}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON file {filename}: {str(e)}")
                    print(f"Error occurred at line {e.lineno}, column {e.colno}")
                    with open(file_path, 'r') as file:
                        problematic_line = file.readlines()[e.lineno - 1]
                    print(f"Problematic line: {problematic_line.strip()}")
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")

        conn.commit()
        print("Finished loading all JSON files")
        check_database_content()
    except (Exception, psycopg2.Error) as error:
        print(f"Error occurred while loading JSON files: {error}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def insert_examination(conn, patient_name, exam_date, exam):
    exam_type = exam.get('nome') or exam.get('tipo_di_esame')
    if not exam_type:
        print(f"Warning: Exam type not found for patient {patient_name} on {exam_date}. Skipping this exam.")
        print(f"Problematic exam data: {exam}")
        return
    
    # Convert date format to YYYY-MM-DD
    try:
        exam_date = datetime.strptime(exam_date, "%Y/%m/%d").strftime("%Y-%m-%d")
    except ValueError:
        try:
            exam_date = datetime.strptime(exam_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Warning: Invalid date format for exam date {exam_date}. Skipping this exam.")
            return
    
    result = exam.get('risultato')
    if result is not None and result != "":
        if isinstance(result, dict):
            # Handle the case where result is a dictionary
            for sub_type, sub_result in result.items():
                insert_sub_examination(conn, patient_name, exam_date, exam_type, sub_type, sub_result, exam)
        else:
            insert_sub_examination(conn, patient_name, exam_date, exam_type, None, result, exam)
    else:
        print(f"Warning: Empty or None result for exam {exam_type} of patient {patient_name} on {exam_date}. Skipping this exam.")

def insert_sub_examination(conn, patient_name, exam_date, exam_type, sub_type, result, exam):
    full_exam_type = f"{exam_type} - {sub_type}" if sub_type else exam_type
    try:
        result = float(result)
        unit = exam.get('unita_di_misura', '')
        reference_range = exam.get('valori_di_riferimento', '')
        with conn.cursor() as cursor:
            cursor.execute('''
            INSERT INTO examinations (patient_name, exam_date, exam_type, result, unit, reference_range)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (patient_name, exam_date, full_exam_type, result, unit, reference_range))
        print(f"Successfully inserted examination: {full_exam_type} for patient {patient_name} on {exam_date}")
    except ValueError:
        print(f"Skipping non-numeric result for {full_exam_type}: {result}")
    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting examination {full_exam_type}: {error}")
        print(f"Problematic data: patient_name={patient_name}, exam_date={exam_date}, result={result}, unit={exam.get('unita_di_misura', '')}, reference_range={exam.get('valori_di_riferimento', '')}")

def check_database_content():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            # Count total number of records
            cursor.execute("SELECT COUNT(*) FROM examinations")
            total_records = cursor.fetchone()[0]
            print(f"Total number of records in the examinations table: {total_records}")
            
            # Get a sample of 5 records
            cursor.execute("SELECT * FROM examinations LIMIT 5")
            sample_records = cursor.fetchall()
            print("Sample of 5 records from the examinations table:")
            for record in sample_records:
                print(record)

            print("\nChecking date formats:")
            cursor.execute("SELECT exam_date FROM examinations LIMIT 5")
            date_samples = cursor.fetchall()
            for date_sample in date_samples:
                print(f"Sample date from database: {date_sample[0]}")
                print(f"Date type: {type(date_sample[0])}")
    except (Exception, psycopg2.Error) as error:
        print(f"Error checking database content: {error}")
    finally:
        if conn:
            conn.close()
