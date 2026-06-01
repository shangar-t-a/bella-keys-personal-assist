-- This script runs once when the production environment is initialized.
-- It creates the databases and users required by the production Bella Keys services.

-- 1. Expense Manager Service (EMS)
CREATE DATABASE expense_manager;
CREATE USER ems_user WITH ENCRYPTED PASSWORD :'ems_pass';
GRANT ALL PRIVILEGES ON DATABASE expense_manager TO ems_user;
ALTER DATABASE expense_manager OWNER TO ems_user;

-- 2. Bella Chat - Arize/Phoenix Observability
CREATE DATABASE bella_chat_arize_data;
CREATE USER arize_user WITH ENCRYPTED PASSWORD :'arize_pass';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_arize_data TO arize_user;
ALTER DATABASE bella_chat_arize_data OWNER TO arize_user;

-- 3. Bella Chat - LangGraph Checkpoints
CREATE DATABASE bella_chat_checkpoints;
CREATE USER langgraph_user WITH ENCRYPTED PASSWORD :'langgraph_pass';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_checkpoints TO langgraph_user;
ALTER DATABASE bella_chat_checkpoints OWNER TO langgraph_user;

-- 4. Auth Service
CREATE DATABASE auth_service;
CREATE USER auth_user WITH ENCRYPTED PASSWORD :'auth_pass';
GRANT ALL PRIVILEGES ON DATABASE auth_service TO auth_user;
ALTER DATABASE auth_service OWNER TO auth_user;
