# InventoryHub

A full-stack inventory management system built with Next.js and Flask.

---

## Prerequisites

- Node.js 18+
- Python 3.11+
- MySQL

---

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `/backend`:

```env
DB_NAME=inventoryhub_db
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
JWT_SECRET_KEY=your_secret_key
JWT_TIMEOUT=15
```

Run the server:

```bash
python run.py
```

Backend runs at `http://localhost:5000`

---

## Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file in `/frontend`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Run the dev server:

```bash
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## Auth Endpoints

| Method | Endpoint             | Description       |
|--------|----------------------|-------------------|
| POST   | `/api/auth/register` | Register new user |
| POST   | `/api/auth/login`    | Login and get JWT |

---

## Pages

| Path               | Description   |
|--------------------|---------------|
| `/Auth/login`      | Login page    |
| `/Auth/register`   | Register page |
| `/staff/dashboard` | Dashboard     |
