# Transaction and Wallet System

A robust backend API for managing user accounts, wallets, and transactions, built with FastAPI and SQLAlchemy. This system supports user registration, wallet creation, and secure transactions between wallets.

## Features

- **User Management**: Register and manage user accounts securely.
- **Wallet Operations**: Create wallets linked to user accounts.
- **Transactions**: Facilitate secure transfers between wallets.
- **Data Validation**: Ensure data integrity using Pydantic models.
- **Database Migrations**: Manage schema changes with Alembic.
- **Testing**: Comprehensive test suite to ensure reliability.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/saim2001/Transaction-and-wallet-system.git
   cd Transaction-and-wallet-system
Create a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Configure the database:

Set the DATABASE_URL in your environment variables or create a .env file in the root directory:

env
Copy
Edit
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
Run database migrations:

bash
Copy
Edit
alembic upgrade head
Start the application:

bash
Copy
Edit
uvicorn main:app --reload
The API will be available at:

cpp
Copy
Edit
http://127.0.0.1:8000
API Documentation
FastAPI provides interactive API docs:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Project Structure
graphql
Copy
Edit
├── alembic/                # Database migrations
├── config/                 # Configuration files
├── model/                  # SQLAlchemy models
├── repository/             # Database interaction logic
├── router/                 # API route definitions
├── schema/                 # Pydantic schemas
├── service/                # Business logic
├── tests/                  # Test cases
├── utils/                  # Utility functions
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
Running Tests
Make sure your virtual environment is activated and run:

bash
Copy
Edit
pytest
This will execute all tests in the tests/ directory.