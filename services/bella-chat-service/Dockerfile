# Official Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY pyproject.toml uv.lock .python-version README.md ./
COPY py_dependencies ./py_dependencies

# Ensure the app directory exists
RUN mkdir -p ./app

# Copy the __init__.py file
COPY app/__init__.py ./app

# Install dependencies
RUN pip install uv
RUN uv sync --no-cache --no-dev

# Copy application code
COPY app ./app

# Expose the application port
EXPOSE 5000

# Start the application
CMD ["uv", "run", "python", "./app/main.py"]
