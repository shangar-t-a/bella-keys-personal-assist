-- This script runs once when the PostgreSQL container is first initialized.
-- It creates the multiple databases and users required by the Bella Keys services.

-- 1. Expense Manager Service (EMS)
CREATE DATABASE expense_manager;
CREATE USER ems_user WITH ENCRYPTED PASSWORD 'ems_password';
GRANT ALL PRIVILEGES ON DATABASE expense_manager TO ems_user;
ALTER DATABASE expense_manager OWNER TO ems_user;

-- 2. Bella Chat - Arize/Phoenix Observability
CREATE DATABASE bella_chat_arize_data;
CREATE USER arize_user WITH ENCRYPTED PASSWORD 'arize_password';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_arize_data TO arize_user;
ALTER DATABASE bella_chat_arize_data OWNER TO arize_user;

-- 3. Bella Chat - LangGraph Checkpoints
CREATE DATABASE bella_chat_checkpoints;
CREATE USER langgraph_user WITH ENCRYPTED PASSWORD 'langgraph_password';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_checkpoints TO langgraph_user;
ALTER DATABASE bella_chat_checkpoints OWNER TO langgraph_user;