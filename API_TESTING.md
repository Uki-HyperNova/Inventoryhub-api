# API Testing with Thunder Client

This guide covers testing all InventoryHub Flask APIs using the **Thunder Client** VS Code extension.

## Prerequisites

1. MySQL running with the database configured in `.env`
2. Flask backend running at `http://localhost:5000`
3. [Thunder Client](https://marketplace.visualstudio.com/items?Name=RapidAPI.thunder-client) installed in VS Code

## Database Setup

```bash
cd Inventoryhub-api

# Create MySQL database (if not exists)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS inventoryhub_db;"

# Initialize migrations (first time only)
flask db init
flask db migrate -m "Initial schema"
flask db upgrade

# Start server
python run.py
```

## Import Thunder Client Collection

1. Open VS Code in the project root
2. Open Thunder Client sidebar
3. Click **Menu (⋮)** → **Import**
4. Import these files from `Inventoryhub-api/thunder-client/`:
   - `Inventory_Management_System_API.json` (collection)
   - `thunderEnvironment.json` (environment)
5. Select the **Local** environment

## Test Flow (Recommended Order)

### 1. Auth

| Request | Method | Endpoint | Auth Required |
|---------|--------|----------|---------------|
| Register | POST | `/auth/register` | No |
| Login | POST | `/auth/login` | No |
| Get Current User | GET | `/auth/me` | Yes |

**Register body:**
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "12345678"
}
```

**Login body:**
```json
{
  "email": "test@example.com",
  "password": "12345678"
}
```

After **Login**, copy `data.access_token` from the response into the `token` environment variable, or let the Login request auto-set it.

### 2. Products (requires JWT)

| Request | Method | Endpoint |
|---------|--------|----------|
| Create Product | POST | `/products` |
| Get All Products | GET | `/products` |
| Get Single Product | GET | `/products/1` |
| Update Product | PUT | `/products/1` |
| Delete Product | DELETE | `/products/1` |

**Create product body:**
```json
{
  "name": "Milk",
  "sku": "MLK001",
  "price": 50,
  "quantity": 10,
  "category": "Dairy",
  "low_stock_threshold": 3
}
```

### 3. Sales (requires JWT)

| Request | Method | Endpoint |
|---------|--------|----------|
| Create Sale | POST | `/sales` |
| Get Sales | GET | `/sales` |

**Create sale body:**
```json
{
  "items": [
    { "product_id": 1, "quantity": 2 }
  ]
}
```

Verify product stock decreased after creating a sale.

### 4. Dashboard (requires JWT)

| Request | Method | Endpoint |
|---------|--------|----------|
| Get Dashboard | GET | `/dashboard` |

Returns total revenue, products, units sold, low stock count, charts, and recent sales.

## Auth Header

All protected routes require:

```
Authorization: Bearer <JWT_TOKEN>
```

The collection uses `{{token}}` from the Local environment.

## Expected Response Format

**Success:**
```json
{
  "success": true,
  "message": "Operation successful.",
  "data": {}
}
```

**Error:**
```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {}
}
```

## Common Issues

| Issue | Fix |
|-------|-----|
| 503 Database unreachable | Start MySQL and verify `DATABASE_URL` in `.env` |
| 401 Unauthorized | Run Login and set the `token` variable |
| 409 SKU already exists | Use a unique SKU when creating products |
| 400 Insufficient stock | Reduce sale quantity or increase product stock |
