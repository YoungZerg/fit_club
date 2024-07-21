import psycopg2
from psycopg2 import OperationalError
import logging
from argon2 import PasswordHasher
from datetime import datetime
from argon2.exceptions import VerifyMismatchError

dbname = "fit_club"
user = "postgres"
password = "Str0ngP@ssword"
host = "192.168.1.150"
port = "5432"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='database_operations.log', filemode='a')

ph = PasswordHasher()

def verify_password(hash, password):
    try:
        return ph.verify(hash, password)
    except VerifyMismatchError:
        return False


def create_connection():
    try:
        connect = psycopg2.connect(
            dbname=dbname,
            user=user, 
            password=password,
            host=host, 
            port=port
        )
        logging.info("Successfully connected to DB")
        return connect
    except OperationalError as e:
        logging.error(f"An error occured while connecting: {e}")
        return None

def execute_query(query):
    connection = create_connection()
    if connection:
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    logging.info("Query executed successfully")
        except OperationalError as e:
            logging.error(f"An error occured during query execution: {e}")
        finally:
            connection.close()
            logging.info("PostgreSQL connection is closed")
        
def fetch_query(query):
    connection = create_connection()
    if connection:
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    logging.info("Query fetched successfully")
                    return result
        except OperationalError as e:
            logging.error(f"An error occured during query fetching: {e}")
            return None
        finally:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def add_new_user(email,
                 name,
                 hashed_password,
                 address,
                 birth_date, 
                 telephone,
                 postal_code,
                 sex) -> None:
    
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO customer (birth_date, tel_number, email, address, postal_code, password_hash, sex, name, profile_pic_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (birth_date, telephone, email, address, postal_code, hashed_password, sex, name, None))
                logging.info("Customer was succeffully added")
                connection.commit()
    except Exception as e:
        logging.error(f"An error occured during customer creation: {e}")
    finally:
        connection.close()
        logging.info("PostgreSQL connection is closed")

'''
def add_new_customer_cart(customer_id):
    try:
        connection = create_connection()
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO shopping_session (total, created_at, modified_at, customer) VALUES (%i, %s, %s, %i)
                """, (0, formatted_time, formatted_time, ))
    except Exception as e:
        logging.error(f"An error occured during cart creation: {e}")
    finally:
        connection.close()
        logging.info("PostgreSQL connection is closed")

def add_new_customer_membership(customer_id):
    return None
'''
