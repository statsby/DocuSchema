# Contributing to Data Dict AI

Thank you for your interest in contributing to **Data Dict AI** – a tool that leverages large language models to generate comprehensive data dictionaries from your databases. We strive to maintain a world-class, modular, and optimized codebase, and your contributions help us reach that goal!

---

## Table of Contents

- [Contributing to Data Dict AI](#contributing-to-data-dict-ai)
  - [Table of Contents](#table-of-contents)
  - [Ways to Contribute](#ways-to-contribute)
  - [Identifying Suitable Issues](#identifying-suitable-issues)
  - [Seeking Assistance](#seeking-assistance)
  - [Pull Request Workflow](#pull-request-workflow)
  - [Setting Up Your Development Environment](#setting-up-your-development-environment)
  - [Adding Support for a New Database](#adding-support-for-a-new-database)
  - [Adding Support for a New LLM](#adding-support-for-a-new-llm)
  - [Commit Signing Process](#commit-signing-process)
  - [Pull Request Checklist](#pull-request-checklist)

---

## Ways to Contribute

We welcome contributions in many forms, including:
- Bug fixes and code improvements
- Enhancing documentation
- Reporting issues or suggesting features
- Providing feedback and testing
- **Adding support for a new database or LLM**

---

## Identifying Suitable Issues

To get started quickly:
- Look for issues labeled **"good first issue"** or **"help wanted"**.
- Comment on the issue to express your interest before starting work.

---

## Seeking Assistance

If you need help, please don’t hesitate to ask questions by opening an issue. We encourage engaging with the community!

---

## Pull Request Workflow

1. Fork the repository.
2. Create a new branch for your contribution.
3. Commit your changes with clear and meaningful messages.
4. Open a pull request (PR) and describe the purpose of your changes.
5. Engage with reviewers and address feedback.
6. Once approved, your PR will be merged.

---

## Setting Up Your Development Environment

Please refer to the [README](README.md) for detailed instructions on installing dependencies and setting up your development environment using Poetry. In short:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your_project.git
   cd your_project
   ```
2. **Install dependencies via Poetry:**
   ```bash
   poetry install
   ```
3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```
4. **Create your `.env` file:**  
   Add your database credentials, API keys, and other configuration variables (do not commit sensitive data).

---

## Adding Support for a New Database

If you want to extend support to a new database (e.g., Oracle, SQL Server):

1. **Create a New Database Class:**  
   - In the `app/database` folder, create a new file (e.g., `oracle.py`).
   - Inherit from the `BaseDB` abstract class and implement the `fetch_metadata()` method.

   Example:
   ```python
   from app.database.base_db import BaseDB
   from typing import List, Tuple, Any
   from common_utils.loggers import logger

   class OracleDB(BaseDB):
       def fetch_metadata(self, conn, schema_name: str) -> List[Tuple[Any, ...]]:
           try:
               with conn.cursor() as cursor:
                   cursor.execute("YOUR_ORACLE_METADATA_QUERY_HERE")
                   rows = cursor.fetchall()
               return rows
           except Exception as err:
               logger.error(f"Error fetching metadata for schema {schema_name}: {err}", exc_info=True)
               return []
   ```

2. **Update the Database Factory:**  
   - Modify `db_factory.py` to import and include your new database class:
   ```python
   from app.database.oracle import OracleDB  # new import

   def get_db_instance():
       if Config.DBMS == "oracle":
           return OracleDB()
       # Other conditions remain unchanged
   ```

3. **Add Configuration Variables:**  
   - Add the necessary environment variables to your `.env` and `.env.example` files.

4. **Write Tests (Optional but Encouraged):**  
   - As we currently have limited test coverage, adding unit tests for your new database support is highly appreciated.

---

## Adding Support for a New LLM

We currently support several LLM providers. OpenAI has been tested extensively; however, we have added a few more LLMs that haven’t been fully tested due to missing API keys. If you have access to the API keys for providers such as Hugging Face or Cohere, please help us test and enhance their integration.

1. **Implement the Integration:**  
   - Update `app/common_utils/llm_selector.py` to add helper methods for the new LLM.
   - Follow the pattern used for OpenAI: validate the API key, initialize the model, and implement robust error handling.

   Example:
   ```python
    # In app/common_utils/llm_selector.py

    from common_utils.loggers import logger
    from config.config import API_KEY  # Or a new API key variable specific to MyLLM if needed
    from your_new_llm_library import ChatMyLLM  # Replace with the actual import for the new LLM

    def _initialize_my_llm(self, model_id: str) -> Any:
        """
        Initialize and return an instance of the MyLLM model.
        
        Replace 'ChatMyLLM' with the appropriate class from the new provider's library.
        Ensure that the necessary API key (e.g., MY_LLM_API_KEY) is set in your environment or configuration.
        """
        # If the new provider uses its own API key, fetch it (e.g., using os.getenv("MY_LLM_API_KEY"))
        # For simplicity, we'll use API_KEY here.
        if not API_KEY:
            logger.error("MyLLM API key is missing. Update your .env file with the correct key.")
            raise ConfigurationError("MyLLM API key is missing.")

        logger.info(f"Initializing MyLLM model: '{model_id}'")
        return ChatMyLLM(model=model_id, api_key=API_KEY, temperature=0.0)

    # Then, within the get_llm_model() method of LLMSelector, add a condition:
    #
    # elif provider == "myllm":
    #     return self._initialize_my_llm(model_id)

   ```

2. **Testing:**  
   - While we currently lack extensive tests for these additional LLMs, your contributions to add tests (or even manual testing using your API keys) would be extremely valuable.
   - Use monkeypatching to simulate API responses where possible to keep tests fast and reliable.
Additional Note:
Contributors can also help test the application by installing Ollama locally and pulling local LLM models such as llama2 or llama3.


3. **Documentation:**  
   - Update both this CONTRIBUTING file and the README with any new configuration or usage instructions required for the additional LLM support.

---

## Commit Signing Process

All commits must be signed to ensure authenticity. Use the following command when committing:
```bash
git commit -S -m "Your commit message"
```

---

## Pull Request Checklist

Before submitting your pull request, please ensure that:
- [ ] Your code follows the project's style guide.
- [ ] Documentation is updated, if necessary.
- [ ] Any related issues are referenced in your PR description.
- [ ] Your changes do not break existing functionality.
- [ ] You have included tests (if applicable) or explained why tests are not provided.

---

Thank you for helping make **Data Dict AI** a world-class project! Your contributions are highly valued, and we look forward to collaborating with you.

Happy coding!
