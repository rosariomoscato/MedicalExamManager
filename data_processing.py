import sqlite3
import pandas as pd
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def get_patient_data(patient_name, exam_type, start_date, end_date):
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT exam_date, result, unit, reference_range
    FROM examinations
    WHERE patient_name = ? AND exam_type = ? AND exam_date BETWEEN ? AND ?
    ORDER BY exam_date
    '''
    df = pd.read_sql_query(query, conn, params=(patient_name, exam_type, start_date, end_date))
    conn.close()
    return df

def get_exam_types():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT exam_type FROM examinations')
    exam_types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return exam_types

def get_aggregated_data():
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT exam_type, AVG(result) as avg_result, COUNT(*) as exam_count
    FROM examinations
    GROUP BY exam_type
    ORDER BY exam_count DESC
    LIMIT 10
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
