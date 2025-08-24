# Airflow Stock Data Pipeline

This project is an automated data pipeline built with Apache Airflow to fetch real-time stock data for a specific symbol (AAPL) and store it in a PostgreSQL database.

## Project Structure

* `Dockerfile`: Defines the custom Airflow image, which includes necessary Python dependencies.
* [cite_start]`requirements.txt`: Lists the Python libraries required, including `requests` to make API calls and `psycopg2-binary` for PostgreSQL database connectivity[cite: 1].
* `docker-compose.yml`: Orchestrates the services for the project, including the PostgreSQL database and the Airflow components (webserver, scheduler, and a one-time initializer).
* `dags/stock_data_dag.py`: The main Airflow DAG file that defines the pipeline's workflow. It schedules two tasks: creating the database table and then fetching/storing the stock data.
* `dags/stock_api_script.py`: A Python script containing the core logic for the data pipeline. It handles connecting to the PostgreSQL database, creating a table if it doesn't exist, fetching data from the Alpha Vantage API, and inserting the data into the database.

## How the Pipeline Works

The pipeline is defined in `stock_data_dag.py` and consists of two main tasks:

1.  **`create_stock_table`**: This task runs the `create_table_if_not_exists` function from `stock_api_script.py` to ensure the `stock_data` table exists in the PostgreSQL database. This task runs first to prepare the database for incoming data.
2.  **`fetch_and_store_data`**: This task runs the `fetch_and_store_stock_data` function, which performs the following steps:
    * It uses the `requests` library to call the Alpha Vantage API for the specified stock symbol (AAPL).
    * It extracts the price and volume data from the API response.
    * It then connects to the PostgreSQL database using `psycopg2` and inserts the fetched data into the `stock_data` table.

The DAG is scheduled to run every hour, ensuring the stock data is refreshed regularly.

## Getting Started

### Prerequisites

* Docker and Docker Compose installed on your system.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd <your_project_directory>
    ```

2.  **Set up the environment variables:**
    * This project uses environment variables to manage sensitive data like API keys and secret keys.
    * Rename the `Stock-data.env` file to `.env`.
    * Open the newly renamed `.env` file and replace the placeholder values with your own keys:
      * [cite_start]**`AIRFLOW_VAR_FERNET_KEY`**: You can generate this by running the command `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`[cite: 2].
      * [cite_start]**`AIRFLOW__WEBSERVER__SECRET_KEY`**: This should be a random string[cite: 3].
      * **`AIRFLOW_VAR_STOCK_API_KEY`**: Obtain a free API key from the Alpha Vantage website.

3.  **Run the services:**
    This command will build the Docker image and start all the services defined in `docker-compose.yml` (Postgres, Airflow webserver, scheduler, and initializer).
    ```bash
    docker compose up -d --build
    docker compose up -d
    ```

4.  **Access the Airflow UI:**
    * The Airflow webserver will be accessible at `http://localhost:8082`.
    * Log in with the default credentials: `username: airflow`, `password: airflow`.

5.  **Monitor the DAG:**
    * Once logged in, you should see the `stock_data_pipeline` DAG listed.
    * You can manually trigger the DAG or wait for its scheduled hourly run to see it in action.

## Database Connection Details

* **Database:** `stock_data`
* **User:** `stock_user`
* **Password:** `stock_password`
* **Host:** `postgres` (internal Docker network name)
* **Port:** `5434` (mapped to `5432` inside the container)

The `stock_api_script.py` connects to the database using these environment variables, which are set in the `docker-compose.yml` file.

Contact 
Email:deepakr0320@gmail.com
