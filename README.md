# FastBase

A modern, production-ready boilerplate for building web applications with FastAPI, Supabase, and HTMX.

## Overview

FastBase is a full-stack application boilerplate that provides a solid foundation for building CRUD applications with real-time capabilities. It features a clean architecture with API endpoints and a dynamic web interface.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Supabase** - PostgreSQL database with REST API and real-time capabilities
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment

### Frontend
- **HTMX** - Dynamic HTML without writing JavaScript
- **Jinja2** - Server-side templating engine
- **CSS3** - Modern styling with gradients and animations

### Development Tools
- **UV** - Fast Python package manager and project manager
- **Python 3.11+** - Modern Python with type hints

## Libraries Used

```toml
fastapi>=0.123.8          # Web framework
uvicorn>=0.38.0           # ASGI server
pydantic-settings>=2.12.0 # Configuration management
supabase>=2.25.0          # Supabase client
email-validator>=2.3.0    # Email validation
jinja2>=3.1.6             # Template engine
python-multipart>=0.0.20  # Form data parsing
python-dotenv>=1.2.1      # Environment variable loading
```

## Prerequisites

- Python 3.11 or higher
- [UV package manager](https://docs.astral.sh/uv/) installed
- A Supabase account (free tier available at [supabase.com](https://supabase.com))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/clk11/fastbase.git
cd fastbase
```

### 2. Install Dependencies

FastBase uses UV for dependency management. Install all required packages:

```bash
uv sync
```

This will create a virtual environment and install all dependencies listed in `pyproject.toml`.

## Configuration

### 1. Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### 2. Get Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project (or create a new one)
3. Click on **"Connect"** button at the top of the page
4. Copy the following values found at **App frameworks** tab:
   - **Project URL** (SUPABASE_URL)
   - **API Key (anon/public)** (SUPABASE_KEY)

### 3. Update .env File

Edit the `.env` file with your Supabase credentials:

```bash
# Application Settings
APP_NAME=FastBase
DEBUG=True

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

## Database Setup

### 1. Access SQL Editor

1. In your Supabase Dashboard, look at the **left sidebar**
2. Click on **"SQL Editor"**
3. Paste your table creation query there that you can find below 👇

### 2. Create Users Table

Copy and paste the following SQL into the editor and click **"Run"**:

```sql
-- Create users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (development mode)
-- WARNING: In production, replace this with proper authentication policies
CREATE POLICY "Allow all operations on users"
ON users FOR ALL
USING (true)
WITH CHECK (true);
```

### 3. Verify Table Creation

After running the SQL:
1. Go to **"Table Editor"** in the left sidebar
2. You should see the `users` table with columns: `id`, `name`, `email`, `created_at`

## Running the Application

### Development Mode (with auto-reload)

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## Accessing the Application

### Web Interface (HTMX UI)

Open your browser and navigate to:

```
http://localhost:8000
```

**Features:**
- Test database connection
- Add new users with form validation
- View all users in real-time
- Automatic duplicate email detection
- Responsive design with modern UI

### API Endpoints

**Connection Test:**
```bash
GET /api/test-connection
```

**List Users (with pagination):**
```bash
GET /api/users?skip=0&limit=100
```

**Create User:**
```bash
POST /api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Health Check:**
```bash
GET /health
```
