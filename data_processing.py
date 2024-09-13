import sqlite3
import pandas as pd
import gettext
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

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

def predict_future_value(patient_name, exam_type, prediction_date):
    # Get historical data for the patient and exam type
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT exam_date, result
    FROM examinations
    WHERE patient_name = ? AND exam_type = ?
    ORDER BY exam_date
    '''
    df = pd.read_sql_query(query, conn, params=(patient_name, exam_type))
    conn.close()

    if len(df) < 2:
        return None, _("Dati insufficienti per la previsione")

    # Convert dates to numerical values (days since the first exam)
    df['days'] = (pd.to_datetime(df['exam_date']) - pd.to_datetime(df['exam_date'].min())).dt.days
    X = df[['days']]
    y = df['result']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Calculate the prediction date in days
    prediction_days = (pd.to_datetime(prediction_date) - pd.to_datetime(df['exam_date'].min())).days

    # Make the prediction
    predicted_value = model.predict([[prediction_days]])[0]

    # Calculate the model's accuracy
    accuracy = model.score(X_test, y_test)

    return predicted_value, accuracy

def get_patient_names():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT patient_name FROM examinations')
    patient_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return patient_names
