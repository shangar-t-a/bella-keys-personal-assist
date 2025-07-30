# Environment Variables

## Overview

This document outlines the environment variables used in the Expense Manager application. These variables are essential for configuring the application and ensuring it runs smoothly in different environments (development, testing, production).

Note:

1. Environment variables should be defined in a `.env` file at the root of the project.
2. You must use the configs in vite.config.js to access these variables in the application.

## Environment Variable List

1. `VITE_APP_HOST`
   - Host address for the frontend application.
   - Default: `localhost`

2. `VITE_APP_PORT`
   - Port number for the frontend application.
   - Default: `3000`

3. `VITE_API_BASE_URL`
   - Base URL for the API endpoints.
   - Default: `https://localhost:8000`

Sample `.env` file:

```plaintext
VITE_APP_HOST=192.168.1.7
VITE_APP_PORT=3000
VITE_BACKEND_BASE_URL=http://192.168.1.7:8000
```
