# 📖 User Setup & Launch Workflow

This guide covers everything you need to know to get Bella Keys running on your local machine or server.

## 1. Prerequisites

Before starting, ensure you have the following installed:

* **Docker Desktop:** [Download](https://www.docker.com/products/docker-desktop/). Must be running.
* **PostgreSQL:** [Download](https://www.postgresql.org/). Ensure it is running on your host machine.
* **Git:** To clone the repository.

---

## 2. Standard Launch (Desktop App)

The primary way to use Bella Keys is via the unified runner script:

1. **Clone & Enter:**

    ```bash
    git clone https://github.com/shangar-t-a/bella-keys-personal-assist.git
    cd bella-keys-personal-assist
    ```

2. **Run the Desktop Runner:**

    ```powershell
    .\scripts\run-desktop-app.bat
    ```

3. **Select Profile:**
    * **Minimal:** Expense tracking only.
    * **Standard:** Full AI Chat + Expense tracking.

---

## 3. Tiered Data Management Model

This project uses a hybrid data model to give you full control over your information.

### Level 1: Fully External (PostgreSQL)

The **Postgres** database is managed entirely by you on your host PC.

* **Action:** You must manually create the `expense_manager`, `bella_chat_arize_data`, and `bella_chat_checkpoints` databases in your local Postgres.
* **Networking:** The containers connect to your host via `host.docker.internal:5432`.

### Level 2: Host-Bound Storage (Qdrant)

The **Qdrant** AI engine runs in Docker, but its memory is stored in your project's `.db/qdrant` folder.

* **Action:** None. Docker handles the engine, and the files stay on your disk.

---

## 4. Troubleshooting

* **"No such service: postgres":** Ignore this message. It simply means the database is external to Docker.
* **Connection Error:** Verify that your Windows Firewall allows Docker to talk to your local Postgres port (5432).
