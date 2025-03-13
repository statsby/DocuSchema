# Data Dictionary Generator

## Overview
This project automates the generation of a data dictionary for a specified database schema. It fetches metadata from the database, enhances it with AI-generated descriptions, and outputs the structured data into an Excel file.

## Features
- Connects to PostgreSQL or MySQL databases.
- Fetches schema and table metadata.
- Uses OpenAI's API to generate meaningful column descriptions.
- Outputs a well-structured Excel file containing the data dictionary.
- Logs all processes for traceability.

## **Data Privacy Notice**

This tool uses AI services (such as OpenAI API) to generate meaningful column descriptions based on database metadata.  

**Please note:**
- When using OpenAI (or similar external APIs), **table schema and column names are sent to the API provider** for processing.
- These names may contain **sensitive information**, such as project names or personal data fields.
- **Review your schema** before using this tool with an external LLM provider.
- If privacy is a concern, consider using **local models** (e.g., Hugging Face, Ollama) instead of cloud-based APIs.

### **🔹 Using a Local Model for Privacy**
To avoid sending data to external servers, you can configure the tool to use a self-hosted LLM:
1. Install **Ollama** or a compatible local LLM provider.
2. Modify the `.env` file:
   ```env
   # Use a local AI model instead of OpenAI
   LLM_PROVIDER=ollama

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
**Important:** Replace all placeholder values (like `your_db`, `your_user`, etc.) with your actual credentials in the `.env` and `docker-compose.yml` files.

## Running with Docker Compose
This project includes a `docker-compose.yml` file to set up MySQL and PostgreSQL containers. **(For local testing purposes)**

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
│   ├── database/
│   │   ├── base_db.py      # Abstract base class for databases
│   │   ├── mysql.py        # MySQL database handler
│   │   ├── postgres.py     # PostgreSQL database handler
│   │   ├── db_factory.py   # Factory pattern for database instances
│   ├── src/
│   │   ├── metadata_extractor.py  # Fetches table metadata
│   │   ├── generate_data_dictionary.py  # Generates data dictionary with OpenAI API
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

