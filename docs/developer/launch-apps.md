# Launching Bella Applications

Bella is my (Shangar's) personal management suite, which currently includes an Expense Management Application and
ChatBot.

- [Launching Bella Applications](#launching-bella-applications)
  - [List of Applications](#list-of-applications)
  - [Launching Applications](#launching-applications)
    - [Expense Management Application](#expense-management-application)
      - [Run using Docker (One Command)](#run-using-docker-one-command)
      - [Run Expense Manager Service Independently](#run-expense-manager-service-independently)
    - [Bella ChatBot Application](#bella-chatbot-application)

## List of Applications

1. Expense Management Application
   1. Backend Service: Expense Manager Service (FastAPI)
   2. Frontend Application: Bella Expense Manager (Next.js)
2. Bella ChatBot Application (FastAPI)
   1. Backend Service: Bella ChatBot Service (FastAPI)
3. ETL Pipeline:
   1. GitHub Repo Scraper
      1. ETL to scrap and load data from github repo to qdrant database.

## Launching Applications

### Expense Management Application

#### Run using Docker (One Command)

1. Navigate to the root directory of the project. Create a `.env` file in the root directory. Refer to the
   `.env.example` file for the required environment variables and their descriptions.

2. Expense Manager Service is Containerized using Docker. To launch the service, navigate to the root directory of
   the project and run:

   ```bash
   docker-compose up -d
   ```

   This command will start both the Expense Manager Service and the Bella Expense Manager frontend application.

#### Run Expense Manager Service Independently

1. Navigate to the `expense-manager-service` directory:

   ```bash
   cd expense-manager-service
   ```

2. Create a `.env` file in the `expense-manager-service` directory. Refer to the `.env.example` file for the required
   environment variables and their descriptions.

3. The Expense Manager Service has a standalone `docker-compose.yaml` file. To launch the service, run:

   ```bash
   docker-compose up -d
   ```

### Bella ChatBot Application

1. Bella Chat Bot is not ready for containerization yet. To launch the Bella ChatBot service, navigate to the
   `bella-chatbot-service` directory:

   ```bash
   cd services/bella-chatbot-service
   ```

2. Create a `.env` file in the `bella-chatbot-service` directory. Refer to the `.env.example` file for the required
   environment variables and their descriptions.

3. To launch the Bella ChatBot service, run:

   ```bash
   uv run python .app/main.py
   ```

4. The Bella ChatBot depends on a Qdrant database. Ensure that you have a running instance of Qdrant before starting
   the service. Qdrant can be run using Docker Compose:

   ```bash
   docker-compose up -d
   ```
