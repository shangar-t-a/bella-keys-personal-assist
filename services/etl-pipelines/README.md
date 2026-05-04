# ETL Pipelines for Bella Chat Application

This directory contains the ETL (Extract, Transform, Load) pipelines used to build the knowledge base for the Bella Chatbot.

## Hybrid Architecture

Following the project-wide **Hybrid "Inside-Out" Architecture**, these pipelines are designed to be run in Docker but interact with data storage (Qdrant) running on the host machine.

### Key Configuration

* **Qdrant URL:** Defaults to `http://host.docker.internal:6333`.
* **Data Source:** Usually extracts from the `keys-personal-assist` GitHub repository.

To run the pipelines locally, ensure your Qdrant instance is running on the host and mapped to port `6333`.
