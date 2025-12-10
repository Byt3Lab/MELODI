# Getting Started with MELODI

This guide will help you set up MELODI on your local machine.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- git (optional, for cloning)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gomsugaetant/MELODI.git
cd MELODI
```

### 2. Set up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode

To start the application in development mode:

```bash
python main.py
```

The application will be available at `http://localhost:5001` (or the configured port).

### Production

For production, use a WSGI server like Gunicorn (Linux) or Waitress (Windows).

**Linux:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

**Windows:**
```powershell
waitress-serve --listen=0.0.0.0:8000 wsgi:app
```

## Configuration

Configuration files are located in the `config/` directory. You can customize database settings, ports, and other options there.
