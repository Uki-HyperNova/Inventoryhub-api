# InventoryHub API

Flask REST API for inventory management, connected to MySQL via SQLAlchemy.

## Tech Stack

- Flask 3
- Flask-SQLAlchemy + PyMySQL
- Flask-Migrate (Alembic)
- Flask-JWT-Extended
- Flask-CORS
- MySQL

## Setup

### 1. Create virtual environment

```bash
cd Inventoryhub-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and update values:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost/inventoryhub_db
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
FLASK_APP=run:app
```

### 3. Create MySQL database

```sql
CREATE DATABASE IF NOT EXISTS inventoryhub_db;
```

### 4. Run migrations

```bash
flask db init        # first time only
flask db migrate -m "Initial schema"
flask db upgrade
```

### 5. Start server

```bash
python run.py
```

API base URL: `http://localhost:5000/api`

## Database Schema

| Table | Description |
|-------|-------------|
| `users` | Staff accounts (hashed passwords) |
| `products` | Inventory items with SKU, price, quantity, low stock threshold |
| `sales` | Sale records with auto-generated invoice numbers |
| `sale_items` | Line items linked to sales and products |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Register staff account |
| POST | `/api/auth/login` | No | Login and receive JWT |
| GET | `/api/auth/me` | Yes | Get current user |
| GET | `/api/products` | Yes | List all products |
| POST | `/api/products` | Yes | Create product |
| GET | `/api/products/:id` | Yes | Get single product |
| PUT | `/api/products/:id` | Yes | Update product |
| DELETE | `/api/products/:id` | Yes | Delete product |
| POST | `/api/sales` | Yes | Record sale (reduces stock) |
| GET | `/api/sales` | Yes | List sales history |
| GET | `/api/dashboard` | Yes | Dashboard analytics |

## Response Format

All endpoints return consistent JSON:

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

## Testing

See [API_TESTING.md](./API_TESTING.md) for Thunder Client collection and test cases.

Import from `thunder-client/`:
- `Inventory_Management_System_API.json`
- `thunderEnvironment.json`

## Business Rules

- SKU must be unique
- Price and quantity cannot be negative
- Sales reduce product stock atomically
- Sales blocked when stock is insufficient
- Low stock: `quantity <= low_stock_threshold`
- Passwords hashed with Werkzeug before storage
