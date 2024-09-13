import pandas as pd
import gettext
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
from database import get_db_connection

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def get_patient_data(patient_name, start_date, end_date):
    # Log the function call with input parameters
    print(f"get_patient_data called with: patient_name={patient_name}, start_date={start_date}, end_date={end_date}")
    print(f"Input date formats - start_date: {type(start_date)} {start_date}, end_date: {type(end_date)} {end_date}")
    
    # Convert date objects to string format for database query
    start_date_db = start_date.strftime("%Y-%m-%d")
    end_date_db = end_date.strftime("%Y-%m-%d")
    print(f"Converted date formats for DB query - start_date: {start_date_db}, end_date: {end_date_db}")
    
    # Establish database connection
    conn = get_db_connection()
    if conn is None:
        print("Failed to establish database connection")
        return []

    # Prepare SQL query
    query = '''
    SELECT DISTINCT exam_type
    FROM examinations
    WHERE patient_name = %s AND exam_date BETWEEN %s AND %s
    ORDER BY exam_type
    '''
    print(f"Executing query with parameters: patient_name={patient_name}, start_date={start_date_db}, end_date={end_date_db}")
    
    try:
        # Execute the query and fetch results
        with conn.cursor() as cursor:
            cursor.execute(query, (patient_name, start_date_db, end_date_db))
            raw_results = cursor.fetchall()
        
        # Log query results
        print(f"Query results: {raw_results}")
        print(f"Number of unique exam types: {len(raw_results)}")
        
        # Check if any results were returned
        if not raw_results:
            print(f"No results found for patient: {patient_name}, start_date: {start_date_db}, end_date: {end_date_db}")
            return []
        
        # Convert raw results to list of exam types
        exam_types = [result[0] for result in raw_results]
        
        print(f"Returning exam types: {exam_types}")
        return exam_types
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        conn.close()

def get_exam_details(patient_name, start_date, end_date, exam_type):
    # Log the function call with input parameters
    print(f"get_exam_details called with: patient_name={patient_name}, start_date={start_date}, end_date={end_date}, exam_type={exam_type}")
    
    # Convert date objects to string format for database query
    start_date_db = start_date.strftime("%Y-%m-%d")
    end_date_db = end_date.strftime("%Y-%m-%d")
    
    # Establish database connection
    conn = get_db_connection()
    if conn is None:
        print("Failed to establish database connection")
        return pd.DataFrame()

    # Prepare SQL query
    query = '''
    SELECT exam_date, result, unit, reference_range
    FROM examinations
    WHERE patient_name = %s AND exam_date BETWEEN %s AND %s AND exam_type = %s
    ORDER BY exam_date
    '''
    
    try:
        # Execute the query and fetch results
        with conn.cursor() as cursor:
            cursor.execute(query, (patient_name, start_date_db, end_date_db, exam_type))
            raw_results = cursor.fetchall()
        
        # Log query results
        print(f"Query results: {raw_results}")
        print(f"Number of rows returned: {len(raw_results)}")
        
        # Check if any results were returned
        if not raw_results:
            print(f"No results found for patient: {patient_name}, exam_type: {exam_type}")
            return pd.DataFrame()
        
        # Convert raw results to pandas DataFrame
        df = pd.DataFrame(raw_results, columns=['exam_date', 'result', 'unit', 'reference_range'])
        
        print(f"Returning DataFrame with shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_aggregated_data():
    # ... (rest of the file remains unchanged)
