import psycopg2
from psycopg2 import OperationalError
import logging
from argon2 import PasswordHasher
from datetime import datetime
from argon2.exceptions import VerifyMismatchError
import os

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



def user_profile_update(uid,
                        name, 
                        email,
                        telephone,
                        birth_date,
                        address,
                        postal_code,
                        sex,
                        profile_pic_path):

    previous_pfp_path = fetch_query("SELECT profile_pic_path FROM customer WHERE id = %i;" % uid)[0][0]

    if profile_pic_path is None:
        profile_pic_path = previous_pfp_path
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                update_query = """
                UPDATE customer SET name = %s, email = %s, tel_number = %s, birth_date = %s, address = %s, postal_code = %s, sex = %s, profile_pic_path = %s
                WHERE id = %s;
                """
                cursor.execute(update_query, (name, email, telephone, birth_date, address, postal_code, sex, profile_pic_path, uid))
    except OperationalError as e:
        logging.error(f"An error occured during updating customer: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")




def create_new_admin(username, email, hashed_password):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO admin(name, email, password_hash) VALUES (%s, %s, %s)", (username, email, hashed_password))
    except OperationalError as e:
        logging.error(f"An error occured during admin creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")

def create_new_equipment(name,
                      description,
                      price,
                      category,
                      equipment_pic_path):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_equipment = """
                    INSERT INTO equipment(name, description, price, equipment_pic_path, category)
                    VALUES(%s, %s, %s, %s, %s);
                """
                cursor.execute(create_equipment, (name, description, price, equipment_pic_path, category))
    except OperationalError as e:
        logging.error(f"An error occured during equipment creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def add_category(name, description):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_category = """
                    INSERT INTO category(name, description)
                    VALUES(%s, %s);
                """
                cursor.execute(create_category, (name, description))
    except OperationalError as e:
        logging.error(f"An error occured during category creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")

def add_class(name, description):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_class = """
                    INSERT INTO class(name, description)
                    VALUES(%s, %s);
                """
                cursor.execute(create_class, (name, description))
    except OperationalError as e:
        logging.error(f"An error occured during class creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def add_new_trainer(name,
                    email,
                    hashed_password,
                    tel_number,
                    birth_date,
                    sex):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_trainer_query = """
                INSERT INTO trainer(name, birth_date, sex, email, tel_number, password_hash, profile_pic_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(create_trainer_query, (name, birth_date, sex, email, tel_number, hashed_password, None))
    except OperationalError as e:
        logging.error(f"An error occured during trainer creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")

def trainer_profile_update(
                    trainer_id,
                    name,
                    email,
                    tel_number,
                    birth_date,
                    sex,
                    profile_pic_path):
    
    previous_pfp_query = "SELECT profile_pic_path FROM trainer WHERE id = %i;" % trainer_id
    previous_pfp = fetch_query(previous_pfp_query)[0][0]
    if profile_pic_path is None or len(profile_pic_path) == 0:
        profile_pic_path = previous_pfp

    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_trainer_query = """
                UPDATE trainer SET name = %s, birth_date = %s, sex = %s, email = %s, tel_number = %s, profile_pic_path = %s
                WHERE id = %s;
                """
                cursor.execute(create_trainer_query, (name, birth_date, sex, email, tel_number, profile_pic_path, trainer_id))
    except OperationalError as e:
        logging.error(f"An error occured during trainer creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def upload_new_certificate(cert_name, trainer_id):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_trainer_query = """
                INSERT INTO train_cert(cert_path, trainer)
                VALUES (%s, %s);
                """
                cursor.execute(create_trainer_query, (cert_name, trainer_id))
    except OperationalError as e:
        logging.error(f"An error occured during trainer creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def new_training_session(class_name,
                         trainer_name,
                         room_number,
                         start_time,
                         end_time):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_train_session_query = """
                INSERT INTO training_session(start_time, end_time, room_number, trainer, class)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(create_train_session_query, (start_time, end_time, room_number, trainer_name, class_name))
    except OperationalError as e:
        logging.error(f"An error occured during trainer creation: {e}")
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed")


def add_customer_to_class(customer_id, training_session_id):
    try:
        connection = create_connection()
        with connection:
            with connection.cursor() as cursor:
                create_cust_train_query = """
                INSERT INTO cust_train_session(training_session, customer)
                VALUES (%s, %s);
                """
                cursor.execute(create_cust_train_query, (training_session_id, customer_id))
    except OperationalError as e:
        logging.error(f"An error occured during trainer creation: {e}")
    finally:
        if connection:
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
