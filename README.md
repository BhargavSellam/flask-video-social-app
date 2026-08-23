# Flask Video Social App

A YouTube-style social video MVP built with Flask.

## Features

- User registration and login
- Upload videos with title and description
- Local file storage for development
- Azure Blob Storage support for production
- Video playback
- Video views
- Likes / unlike
- Comments
- Delete your own comments
- Search
- User profile/channel pages
- Delete your own videos
- Responsive Bootstrap interface
- SQLite locally
- PostgreSQL-ready for Azure

## 1. Create virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install packages

```bash
pip install -r requirements.txt
```

## 3. Create .env

Copy `.env.example` to `.env`.

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

## 4. Create database

```bash
flask --app run.py db init
flask --app run.py db migrate -m "Initial migration"
flask --app run.py db upgrade
```

If migrations already exist, only run:

```bash
flask --app run.py db upgrade
```

## 5. Run

```bash
python run.py
```

Open:

http://127.0.0.1:5000

## Azure Blob Storage

Create a Storage Account and a blob container called `videos`.

Update `.env`:

```env
USE_AZURE_STORAGE=true
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=videos
```

## Azure PostgreSQL

Set:

```env
DATABASE_URL=postgresql://username:password@server:5432/database
```

For Azure PostgreSQL, SSL may be required. A typical connection string can include:

```env
DATABASE_URL=postgresql://username:password@server:5432/database?sslmode=require
```

## Azure App Service Startup Command

```bash
gunicorn --bind=0.0.0.0 --timeout 600 run:app
```

## Production recommendations

For a real large-scale video platform:

- use direct-to-Blob uploads with SAS URLs
- validate MIME/file signatures
- transcode uploads with FFmpeg
- generate thumbnails automatically
- use HLS/DASH adaptive streaming
- use Azure CDN/Front Door
- add rate limiting and moderation
- use managed identity instead of permanent storage keys
