import requests
import psycopg2
import os
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv('AIRFLOW_VAR_DB_HOST', 'postgres')
DB_NAME = 'stock_data'
DB_USER = 'stock_user'
DB_PASSWORD = 'stock_password'
STOCK_API_KEY = os.getenv('AIRFLOW_VAR_STOCK_API_KEY')
STOCK_SYMBOL = 'AAPL'

def create_table_if_not_exists():
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()
        logging.info("Successfully connected to the PostgreSQL database.")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_data (
            symbol VARCHAR(10) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            volume INT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            PRIMARY KEY (symbol, timestamp)
        );
        """
        cur.execute(create_table_sql)
        conn.commit()
        logging.info("Table 'stock_data' checked/created successfully.")
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error creating table: {error}")
    finally:
        if conn is not None:
            conn.close()

def insert_stock_data(symbol, price, volume):
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()
        logging.info("Database connection for insertion successful.")
        insert_sql = """
        INSERT INTO stock_data (symbol, price, volume, timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (symbol, timestamp) DO NOTHING;
        """
        cur.execute(insert_sql, (symbol, price, volume, datetime.now()))
        conn.commit()
        logging.info(f"Successfully inserted data for {symbol}.")
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error inserting data into table: {error}")
    finally:
        if conn is not None:
            conn.close()

def fetch_and_store_stock_data():
    logging.info("Starting data fetching and storage process...")
    if not STOCK_API_KEY:
        logging.error("STOCK_API_KEY is not set. Please check your environment variables.")
        return
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={STOCK_SYMBOL}&apikey={STOCK_API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        logging.info("Successfully fetched data from API.")
        stock_info = data.get('Global Quote', {})
        if not stock_info:
            logging.error("Could not find 'Global Quote' in API response. Please check the stock symbol and API key.")
            logging.debug(f"Received data: {data}")
            return
        price = stock_info.get('05. price')
        volume = stock_info.get('06. volume')
        if price is None or volume is None:
            logging.warning("Missing 'price' or 'volume' in API response. Skipping insertion.")
            logging.debug(f"Received data: {data}")
            return
        try:
            price = float(price)
            volume = int(volume)
        except (ValueError, TypeError) as e:
            logging.error(f"Failed to convert data types: {e}. Raw data: price={price}, volume={volume}")
            return
        insert_stock_data(STOCK_SYMBOL, price, volume)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from API: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"Failed to parse API response: {e}")

if __name__ == "__main__":
    create_table_if_not_exists()
    fetch_and_store_stock_data()