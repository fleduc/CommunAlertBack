# CommunAlert Backend Application

PLEASE NOTE THAT THE PURPOSE OF THIS PROJECT IS TO BE USED FOR JOB INTERVIEWS THIS PROJECT IS NOT COMPLETE, AS IT IS JUST A PROOF OF CONCEPT AND COULD BE MODIFIED AND DEFINITELY IMPROVED IN THE FUTURE


CommunAlert is a full-stack application that provides a user interface for managing alerts and communications. This repository contains the backend code powered by Python FastAPI and a MySQL database, with additional support services such as phpMyAdmin for database management.

## Table of Contents

- [Project Overview](#project-overview)
- [Infrastructure](#infrastructure)
- [Plugins and Dependencies](#plugins-and-dependencies)
- [Cloning the Project](#cloning-the-project)
- [Installation and Setup](#installation-and-setup)
- [Running Database Migrations](#running-database-migrations)
- [Executing the Application](#executing-the-application)
- [Swagger Documentation](#swagger-documentation)

## Project Overview

CommunAlert is designed to:

- **Manage Alerts:** Create, view, and update alerts.
- **User Authentication:** Secure authentication using FastAPI and JWT.
- **Database Management:** Use MySQL as the primary datastore with migrations managed by Alembic.
- **API Documentation:** Auto-generated Swagger documentation for the API endpoints.

## Infrastructure

The backend is containerized using Docker and orchestrated with Docker Compose. The main components are:

- **Backend:** A FastAPI application running on Python 3.11 with uvicorn.
- **MySQL Database:** Containerized MySQL 8 instance.
- **phpMyAdmin:** Web-based MySQL administration tool.

### Key Configuration Files

- **Dockerfile:**  
  Sets up the Python environment, installs backend dependencies, copies the application code, exposes port 8000, and starts the application with uvicorn.

- **docker-compose.yml:**  
  Defines three services:
  - `backend`: Builds from the Dockerfile and serves the FastAPI app.
  - `mysql-db`: Runs a MySQL database.
  - `phpmyadmin`: Provides a web interface to manage the MySQL database.
  
- **requirements.txt:**  
  Lists the Python dependencies needed for the backend:
  - `fastapi~=0.115.8`
  - `uvicorn`
  - `sqlalchemy~=2.0.38`
  - `pymysql`
  - `python-dotenv~=1.0.1`
  - `alembic~=1.14.1`
  - `email-validator`
  - `pydantic[email]~=2.10.6`
  - `python-jose[cryptography]`
  - `passlib~=1.7.4`

## Plugins and Dependencies

### Runtime Dependencies

- **FastAPI:** High-performance web framework for building APIs.
- **uvicorn:** ASGI server for running FastAPI.
- **SQLAlchemy:** ORM for database interactions.
- **pymysql:** MySQL driver for Python.
- **python-dotenv:** Loads environment variables from a `.env` file.
- **alembic:** Database migrations tool.
- **email-validator:** For validating email addresses.
- **pydantic[email]:** Data validation and settings management.
- **python-jose:** For JWT creation and validation.
- **passlib:** For secure password hashing.

### Container and Orchestration

- **Docker:** Containerizes the backend application.
- **Docker Compose:** Orchestrates multi-container setup, including the backend, MySQL database, and phpMyAdmin.

## Cloning the Project

To get started, clone the repository with:

```bash
git clone https://github.com/your-username/communalert.git
cd communalert
```

## Installation and Setup
### Prepare Environment Variables:

Create a .env file in the root directory with the necessary environment variables (e.g., database credentials, secret keys, etc.).

### Build and Start the Containers:

Use Docker Compose to build and start all services:

```bash
docker-compose up --build -d
```
This command builds the backend image, starts the MySQL database, and launches phpMyAdmin on port 8080.



## Running Database Migrations:

Before executing the application, run the database migrations to set up the schema:

#### Execute Migrations Inside the Backend Container:
Once the containers are running, execute the following command to upgrade the database schema to the latest version:
```bash
docker-compose exec backend alembic upgrade head
```
This command uses Alembic to run all pending migrations.

## Executing the Application
With the containers running and migrations applied, the backend FastAPI application will be accessible at:
```bash
http://localhost:8000
```
The Swagger UI for API documentation can be found at:
```bash
http://localhost:8000/docs#
```
Additionally, phpMyAdmin is available at:
```bash
http://localhost:8080
```

## Swagger Documentation
The API is fully documented using Swagger. Visit http://localhost:8000/docs# in your browser to view and test the API endpoints interactively.