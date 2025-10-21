# Environment Variables

## Overview

This document outlines the environment variables used in the Expense Manager application. These variables are essential for configuring the application and ensuring it runs smoothly in different environments (development, testing, production).

Note:

1. Environment variables should be defined in a `.env` file at the root of the project.
2. You must use the configs in vite.config.js to access these variables in the application.

## Environment Variable List

1. `HOST`
   - Host address for the frontend application.
   - Default: `localhost`

2. `PORT`
   - Port number for the frontend application.
   - Default: `3000`

3. `NEXT_PUBLIC_EMS_API_URL`
   - Base URL for the API endpoints.
   - Default: `https://localhost:8000`

Sample `.env` file:

```plaintext
HOST=localhost
PORT=3000
NEXT_PUBLIC_EMS_API_URL=http://localhost:8000
```
