-- Create the database
CREATE DATABASE expense_manager;

-- Create application user with password
CREATE USER ems_user WITH ENCRYPTED PASSWORD 'your_password_here';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE expense_manager TO ems_user;

-- Make user the owner of the database
ALTER DATABASE expense_manager OWNER TO ems_user;
