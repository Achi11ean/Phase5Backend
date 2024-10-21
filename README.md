# PRISM

## Backend for Event Management App

## Introduction

This repository contains the backend for the **PRISM App**, a platform designed to manage artists, attendees, events, tours, and venues. The backend is built using Python's Flask framework and serves as the RESTful API to interact with the frontend.

The backend manages user authentication, CRUD operations for managing various entities (artists, attendees, events, tours, venues), and database persistence using SQLAlchemy.

## Technologies and Tools

- **Flask**: A lightweight WSGI web application framework for Python.
- **SQLAlchemy**: The ORM used for interacting with the SQLite database.
- **Flask-CORS**: Middleware to handle Cross-Origin Resource Sharing (CORS), making the API accessible from different domains.
- **SQLite**: Database to store user data, including artists, attendees, events, and more.
- **bcrypt**: A password hashing utility for securely storing passwords.
- **Pipenv**: Python dependency manager used to create a virtual environment and manage dependencies.

## Project Structure

```bash
.
├── app.py                 # Main application file
├── Pipfile                # Pipenv file specifying project dependencies
├── Pipfile.lock           # Lock file for project dependencies
├── main.db                # SQLite database storing all backend data
├── migrations/            # Directory for Alembic database migrations
│   └── b3229da68a76_add_profile_completed.py  # Migration file
└── README.md              # Project documentation
```

## API Endpoints

### Authentication Routes

- **POST** `/signup`: Sign up a new user. Requires `username`, `password`, and `user_type`.
- **POST** `/signin`: Sign in an existing user. Requires `username` and `password`.
- **POST** `/signout`: Sign out the current user.

### Entity Management

- **GET** `/artists`: Get a list of all artists.
- **POST** `/artists`: Create a new artist.
- **GET** `/attendees`: Get a list of all attendees.
- **POST** `/attendees`: Create a new attendee.
- **GET** `/events`: Get a list of all events.
- **POST** `/events`: Create a new event.
- **GET** `/tours`: Get a list of all tours.
- **POST** `/tours`: Create a new tour.
- **GET** `/venues`: Get a list of all venues.
- **POST** `/venues`: Create a new venue.

## Setup Instructions

### Prerequisites

- **Python 3.x**
- **Pipenv**: Python package and environment manager

### Running the Backend Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/music-event-backend.git
   cd Phase4Project
   ```

2. Install dependencies using Pipenv:

   ```bash
   pipenv install
   ```

3. Activate the Pipenv environment:

   ```bash
   pipenv shell
   ```

4. Initialize the database:

   ```bash
   flask db upgrade
   ```

5. Run the development server:

   ```bash
   flask run --port=5001
   ```

   The backend API will now be accessible at `http://127.0.0.1:5001`.

### Running Migrations

If changes to the database schema are made, Alembic migrations can be run as follows:

```bash
flask db upgrade
```

### Environment Variables

You can define environment variables in a `.env` file. The project uses the following variables:

- `SECRET_KEY`: Used by Flask to encrypt session data.
- `DATABASE_URL`: The path to the SQLite database.

## Future Updates

- **OAuth Authentication**: Add Google and Facebook OAuth for easier user registration.
- **Logging**: Implement advanced logging for API requests and error handling.
- **Rate Limiting**: Protect API endpoints by implementing rate-limiting for users.
- **Unit Testing**: Add unit tests for all API endpoints and backend logic.
- **Pagination**: Implement pagination for entity lists (artists, attendees, events, etc.).
