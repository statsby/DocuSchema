# Data Dictionary Generator

## Overview
This project automates the generation of a data dictionary for a specified database schema. It fetches metadata from the database, enhances it with AI-generated descriptions, and outputs the structured data into an Excel file.

## Features
- Connects to PostgreSQL or MySQL databases.
- Fetches schema and table metadata.
- Uses OpenAI's API to generate meaningful column descriptions.
- Outputs a well-structured Excel file containing the data dictionary.
- Logs all processes for traceability.

## Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Docker & Docker Compose
- LLM API Key
- Required Python packages (see `pyproject.toml`)
- Poetry

## Installation

### 1. Clone the Repository
```sh
git clone git@github.com:statsby/data_dictionary.git
cd data-dict-ai
```

### 2. Set Up Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```sh
poetry install
```

### 4. Configure Environment Variables
Create a `.env` file (or modify the existing one) with the following details:
```env
# Database Management System (Choose: "postgres" or "mysql")
DBMS=postgres

# PostgreSQL Configuration
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# MySQL Configuration
MYSQL_DATABASE=your_db
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost

# OpenAI API Key
API_KEY=your_openai_api_key

# Schema Name
SCHEMA_NAME=your_schema
```

## Running with Docker Compose
This project includes a `docker-compose.yml` file to set up MySQL and PostgreSQL containers.

### 1. Start Database Containers
```sh
docker-compose up -d
```
This will start MySQL and PostgreSQL containers in the background.

### 2. Stop Containers
```sh
docker-compose down
```

## Usage
Run the script to generate the data dictionary:
```sh
python main.py
```

### Expected Output
An Excel file named `<SCHEMA_NAME>_data_dictionary_(DBMS).xlsx` will be created in the `output/` directory.

## Code Structure
```
├── app/
│   ├── config/
│   │   ├── config.py       # Configuration settings
│   │   ├── db_config.py    # Database connection setup
│   ├── common_utils/
│   │   ├── loggers.py      # Logging configuration
│   ├── src/
│   │   ├── fetch_metadata.py  # Fetches table metadata
│   │   ├── generate_dd.py     # Generates data dictionary with OpenAI API
│   ├── main.py             # Main script to generate the data dictionary
│
├── docker-compose.yml      # Docker Compose configuration for databases
├── .env                    # Environment configuration file
├── pyproject.toml          # List of required dependencies
├── README.md               # Project documentation
```

## Logging
All logs are stored in `logs/` directory with appropriate error handling.

## Troubleshooting
### 1. Database Connection Issues
- Ensure that PostgreSQL/MySQL is running and accessible.
- Verify credentials in the `.env` file.
- If using Docker, ensure the containers are running (`docker ps`).

### 2. OpenAI API Errors
- Check if the OpenAI API key is valid and active.
- Ensure that the API key has sufficient quota.

### 3. Output File Not Generated
- Check the logs in `logs/` for errors.
- Ensure the database has tables under the specified schema.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

<!-- ## License
This project is licensed under the MIT License.

## Contact
For any questions or support, contact [your-email@example.com]. -->

