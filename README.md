# Transaction and Wallet System 💳

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/saim2001/Transaction-and-wallet-system)

## Features ✨

- **Wallet Operations**: Balance tracking, credit deductions, transaction history
- **Transaction Processing**: Credit/budget purchases with validation
- **Project Integration**: Credit reservation system with price calculations
- **Secure API**: JWT authentication and role-based access

## Quick Start 🚀


### 1. Clone repository
```bash
git clone https://github.com/saim2001/Transaction-and-wallet-system.git
cd Transaction-and-wallet-system
```

### 2. Setup environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure .env (copy from .env.example)

### 5. Run migrations
```bash
alembic upgrade head
```

### 6. Start server
```bash
uvicorn app.main:app --reload
```

## Testing 🧪
### Run all tests
```bash
pytest -v
```

## Project Structure 🏗️

app/
├── core/            # Configs and security
├── models/          # SQLAlchemy models
├── repositories/    # Database operations
├── routes/          # API endpoints
├── schemas/         # Pydantic models
├── services/        # Business logic
└── main.py          # App initialization