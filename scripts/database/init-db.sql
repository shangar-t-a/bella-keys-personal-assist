-- This script runs once when the PostgreSQL container is first initialized.
-- It creates the multiple databases and users required by the Bella Keys services.

-- 1. Expense Manager Service (EMS)
CREATE DATABASE expense_manager_dev;
CREATE USER ems_user WITH ENCRYPTED PASSWORD :'ems_pass';
GRANT ALL PRIVILEGES ON DATABASE expense_manager_dev TO ems_user;
ALTER DATABASE expense_manager_dev OWNER TO ems_user;

-- 1b. Expense Manager Service Tests (EMS Tests)
CREATE DATABASE expense_manager_test;
CREATE USER ems_test_user WITH ENCRYPTED PASSWORD :'ems_test_pass';
GRANT ALL PRIVILEGES ON DATABASE expense_manager_test TO ems_test_user;
ALTER DATABASE expense_manager_test OWNER TO ems_test_user;


-- 2. Bella Chat - Arize/Phoenix Observability
CREATE DATABASE bella_chat_arize_data;
CREATE USER bella_chat_user WITH ENCRYPTED PASSWORD :'bella_chat_pass';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_arize_data TO bella_chat_user;
ALTER DATABASE bella_chat_arize_data OWNER TO bella_chat_user;

-- 3. Bella Chat - LangGraph Checkpoints
CREATE DATABASE bella_chat_checkpoints;
-- Create USER done at step 2
-- CREATE USER bella_chat_user WITH ENCRYPTED PASSWORD :'bella_chat_pass';
GRANT ALL PRIVILEGES ON DATABASE bella_chat_checkpoints TO bella_chat_user;
ALTER DATABASE bella_chat_checkpoints OWNER TO bella_chat_user;