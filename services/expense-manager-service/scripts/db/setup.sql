-- Expense Manager Service database setup
-- Creates the application database and user, then grants all privileges.

-- Create the database
CREATE DATABASE expense_manager_dev;

-- Create application user with password. Update 'your_password_here' with a secure password before running this script.
CREATE USER ems_user WITH ENCRYPTED PASSWORD 'your_password_here';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE expense_manager_dev TO ems_user;

-- Make user the owner of the database
ALTER DATABASE expense_manager_dev OWNER TO ems_user;

-- Create the test database and test user for running tests
CREATE DATABASE expense_manager_test;
CREATE USER ems_test_user WITH ENCRYPTED PASSWORD 'test123';
GRANT ALL PRIVILEGES ON DATABASE expense_manager_test TO ems_test_user;
ALTER DATABASE expense_manager_test OWNER TO ems_test_user;

