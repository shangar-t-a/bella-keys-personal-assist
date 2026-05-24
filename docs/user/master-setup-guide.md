# 👑 Master Setup Guide: Bella Keys

This is the definitive guide for setting up Bella Keys from scratch. Since the application follows an **"Inside-Out"** architecture, you must prepare your host environment before launching the Docker services.

---

## 1. Infrastructure Setup (PostgreSQL)

Before running the app, you must initialize your local PostgreSQL instance with the required users and databases.

### Step 1: Create Databases & Users

Run the initialization script against your host PostgreSQL instance:

* **Script Location:** [scripts/database/init-db.sql](../../scripts/database/init-db.sql)

You can run this via `psql -f` or by copying the contents into your preferred SQL GUI (pgAdmin, DBeaver, etc.). This script creates the `expense_manager` (including `expense_manager_test` for running tests), `bella_chat_arize_data`, and `bella_chat_checkpoints` databases.

### Step 2: Configure Environment

In the `docker/` folder, ensure your `.env` file reflects the credentials set in the SQL script and points to your host:

```env
EMS_PG_DB_HOST=host.docker.internal
EMS_PG_DB_USER=ems_user
EMS_PG_DB_PASSWORD=ems_password
...
```

---

## 2. Prerequisites

* **Docker Desktop:** Installed and running.
* **Ollama (Optional):** Required for local-first AI models. Install at [ollama.com](https://ollama.com/).

---

## 3. Application Launch Flow

The unified runner script manages the backend lifecycle and launches the Electron UI.

1. **Clone & Enter:**

    ```bash
    git clone https://github.com/shangar-t-a/bella-keys-personal-assist.git
    cd bella-keys-personal-assist
    ```

2. **Run the Desktop Runner:**

    ```powershell
    .\scripts\run-desktop-app.bat
    ```

3. **Choose Your Profile:**

| Profile | Services Included | Resources (RAM) | Use Case |
| :--- | :--- | :--- | :--- |
| **Minimal** | Expense Manager | ~2GB | Basic financial tracking only. |
| **Standard** | EMS + Bella Chat | ~4GB | Full AI assistant + Finance. |
| **Enhanced** | All + Monitoring | ~6GB+ | Testing & AI Observability. |

---

## 4. Troubleshooting

* **Database Connectivity:** If containers fail to connect, ensure Windows Firewall allows port `5432`.
* **"No such service: postgres":** This is expected. It confirms that Postgres is running on your host, not inside Docker.
* **Docker DNS:** `host.docker.internal` requires Docker Desktop to be running (ideally with the WSL2 backend).
