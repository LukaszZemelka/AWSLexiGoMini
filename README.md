# LexiGo - English Word Learning App

A web-based application for learning English vocabulary with Polish translations, built with Flask and PostgreSQL.

## Features

- 🔐 **Google OAuth Authentication** - Secure login with Google account
- 📚 **Word Cards** - Learn words with translations and example sentences
- ✍️ **Personal Notes** - Add your own notes for each word (user-specific)
- ⌨️ **Keyboard Navigation** - Use arrow keys to navigate between words
- 👤 **User Profiles** - Each user has their own personalized experience
- 💾 **PostgreSQL Database** - Reliable data storage

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Authentication**: Google OAuth 2.0 (via Authlib)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Gunicorn WSGI server
- **Deployment**: AWS EC2 (Ubuntu 24.04)

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL
- Google Cloud Console account (for OAuth credentials)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/LukaszZemelka/AWSLexiGoMini.git
   cd AWSLexiGoMini
   ```

2. Install dependencies:
   ```bash
   pip3 install flask authlib psycopg2-binary requests
   ```

3. Set up PostgreSQL database:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE lexigo;
   CREATE USER myuser;
   GRANT ALL PRIVILEGES ON DATABASE lexigo TO myuser;
   \c lexigo
   
   # Run the schema from database_schema.sql
   ```

4. Configure Google OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `http://your-domain.com:5000/login/callback`
   - Copy Client ID and Client Secret

5. Create `.env` file:
   ```bash
   cp .env.template .env
   # Edit .env and add your Google OAuth credentials
   ```

6. Run the application:
   ```bash
   python3 app.py
   ```

7. Access at `http://localhost:5000`

## Database Schema

### words table
- `id` - Primary key
- `word` - English word
- `polish_translation` - Polish translation
- `example_sentence_1/2/3` - Example sentences
- `created_at` - Timestamp

### user_notes table
- `id` - Primary key
- `user_email` - User identifier
- `word_id` - Foreign key to words
- `notes` - User's personal notes
- `created_at` / `updated_at` - Timestamps

## API Endpoints

- `GET /` - Main application (requires login)
- `GET /login` - Login page
- `GET /login/google` - Initiate Google OAuth
- `GET /login/callback` - OAuth callback
- `GET /logout` - Logout
- `GET /api/user` - Get current user info
- `GET /api/words` - Get all words
- `GET /api/notes/<word_id>` - Get note for word
- `POST /api/notes/<word_id>` - Save note for word

## Database Access

To connect to the PostgreSQL database from your local pgAdmin 4 client, see the detailed guide:

📖 **[DATABASE_ACCESS.md](DATABASE_ACCESS.md)** - Complete guide for connecting pgAdmin 4 to EC2 database

Supports:
- SSH tunneling (recommended)
- Direct connection setup
- Troubleshooting tips
- Useful SQL queries


## Deployment

See `GOOGLE_OAUTH_SETUP.md` for detailed deployment instructions on AWS EC2.

## License

MIT License

## Author

Łukasz Zemelka
