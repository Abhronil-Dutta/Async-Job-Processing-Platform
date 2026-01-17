# GEMINI.md

## Project Overview

This project is an Asynchronous Job Processing Platform. It is in the early stages of development.

The platform is designed to handle background jobs asynchronously. It consists of the following components:

*   **API:** A FastAPI-based web API for creating and managing jobs.
*   **Database:** A PostgreSQL database to store job information, such as job type, payload, status, and attempts. The schema is defined in `Joblib/models.py`.
*   **Message Broker:** A Redis instance is used as a message broker to manage job queues (e.g., pending and processing lists).
*   **Workers:** Worker processes that listen for jobs from the message broker, execute them based on job type, and update their status in the database. The worker includes a lease mechanism for long-running jobs.
*   **Monitoring:** A monitoring component (to be implemented) will track the health of workers and the status of jobs, handling timeouts and failures.

The overall architecture is based on the workflow diagram found in `Diagrams/Workflow_Iter_1.png`.

## Building and Running

The project is containerized using Docker and can be run with Docker Compose.

To build and run the project, execute the following command in the root directory:

```bash
docker-compose up
```

This command will start the following services:

*   `postgres`: The PostgreSQL database.
*   `api`: The FastAPI web application.

The API will be available at `http://localhost:8000`.

### Endpoints

*   `GET /health`: Returns the health status of the API.
*   `GET /db_check`: Checks the database connection.
*   `POST /jobs`: Creates a new job.

## Development Conventions

*   **Dependencies:** Python dependencies are managed in the `requirements.txt` file.
*   **Database:** The project uses SQLAlchemy to interact with the PostgreSQL database. The database connection is configured in `api/db.py` and the schema is defined in `Joblib/models.py`.
*   **TODO:** The core logic for the monitoring system is not yet implemented. The following file is currently empty and needs to be developed:
    *   `monitor/monitor.py`

## Key Files

*   `docker-compose.yml`: Defines the services, networks, and volumes for the Docker environment.
*   `requirements.txt`: Lists the Python dependencies for the project.
*   `api/app.py`: The main FastAPI application file, containing the API endpoints.
*   `api/db.py`: Configures the database connection.
*   `Joblib/models.py`: Defines the database schema for jobs.
*   `Diagrams/Workflow_Iter_1.png`: A diagram illustrating the job processing workflow.
*   `Readme.md`: The project's README file.