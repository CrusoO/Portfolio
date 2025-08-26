# 🚀 Robinson's Portfolio Backend

A comprehensive FastAPI backend for Robinson's portfolio website, featuring AI chat integration, user reviews, contact forms, canvas art storage, and blog/notes management.

## ✨ Features

- **🤖 AI Chat Assistant** - Interactive AI assistant "Cruso" with Groq/OpenAI integration
- **⭐ Review System** - User feedback and ratings with statistics
- **📧 Contact Forms** - Professional contact form handling
- **🎨 Canvas Art Storage** - Save and display digital artwork
- **📝 Blog/Notes Management** - Create and manage articles with categories
- **🔐 JWT Authentication** - Secure user authentication and authorization
- **📊 RESTful APIs** - Well-organized API endpoints with documentation
- **🗄️ Database Management** - SQLAlchemy ORM with Alembic migrations
- **🔒 Security Features** - Password hashing, CORS, input validation

## 🛠️ Tech Stack

- **Backend:** FastAPI 0.104.1
- **Database:** SQLAlchemy 2.0.25 (SQLite default, PostgreSQL/MySQL support)
- **Authentication:** JWT with python-jose and passlib
- **AI Integration:** Groq Mixtral-8x7B (primary) / OpenAI GPT-3.5-turbo (fallback)
- **Migrations:** Alembic 1.13.1
- **Server:** Uvicorn with auto-reload

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd CrusoPortfolio-Backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp environment.example .env

# Edit .env with your API keys:
# GROQ_API_KEY=gsk_your_groq_api_key_here
# ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
# SECRET_KEY=your-secure-jwt-secret
```

**Important:** Never commit your `.env` file with real API keys to GitHub!

### 5. Initialize Database

```bash
# Quick setup (if you ran scripts/setup.py, this is already done)
python scripts/init_db.py

# OR manual setup with Alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Run the Server

```bash
# Development
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main file
python app/main.py
```

🎉 Your API is now running at `http://localhost:8000`

### 🤖 AI Chat Features

Your backend includes "Cruso", an AI assistant powered by **Groq** for lightning-fast responses:

**Why Groq?**
- ⚡ **Ultra-fast inference** - 10x faster than traditional APIs
- 💰 **Cost-effective** - More affordable than alternatives
- 🧠 **Powerful models** - Uses Mixtral-8x7B for intelligent responses
- 🔄 **Automatic fallback** - Falls back to OpenAI or predefined responses if needed

**Chat Features:**
- Personalized responses using visitor's name
- Portfolio-focused conversations about your projects
- Technical discussions about your skills and experience
- Intelligent fallbacks for reliability

## 📖 API Documentation

Once running, visit:
- **Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **API Info:** `http://localhost:8000/`

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login

#### Chat System
- `POST /api/chat/message` - Send message to AI assistant
- `GET /api/chat/history` - Get chat history

#### Reviews
- `POST /api/reviews` - Submit review
- `GET /api/reviews` - Get reviews
- `GET /api/reviews/stats` - Get review statistics

#### Contact
- `POST /api/contact/submit` - Submit contact form
- `GET /api/contact` - Get contact submissions

#### Canvas Art
- `POST /api/canvas/save` - Save artwork
- `GET /api/canvas` - Get artworks
- `GET /api/canvas/{id}` - Get specific artwork

#### Notes/Blog
- `GET /api/notes` - Get published notes
- `POST /api/notes` - Create note (admin only)
- `PUT /api/notes/{id}` - Update note (admin only)

## 🔧 Configuration

### Environment Variables

```env
# Application
APP_NAME="Robinson's Portfolio Backend"
DEBUG=False

# Database
DATABASE_URL="sqlite:///./portfolio.db"

# Security
SECRET_KEY="your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration (optional - for enhanced chat responses)
GROQ_API_KEY="gsk-..."
OPENAI_API_KEY="sk-..."
AI_PROVIDER="groq"

# Server
HOST="0.0.0.0"
PORT=8000
```

### Database Configuration

#### SQLite (Default)
```env
DATABASE_URL="sqlite:///./portfolio.db"
```

#### PostgreSQL
```env
DATABASE_URL="postgresql://username:password@localhost/portfolio_db"
```

#### MySQL
```env
DATABASE_URL="mysql://username:password@localhost/portfolio_db"
```

## 🚀 Deployment

### Render.com (Recommended)

1. **Connect Repository:** Link your GitHub repository to Render
2. **Service Configuration:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables:** Add your production environment variables
4. **Deploy:** Render will automatically deploy your service

### Heroku

1. **Create Heroku App:**
   ```bash
   heroku create your-app-name
   ```

2. **Add Buildpack:**
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Set Environment Variables:**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DATABASE_URL="your-database-url"
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🗄️ Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade (if needed)
alembic downgrade -1
```

### Sample Data

Create an admin user:

```python
# Run this in Python shell or create a script
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

admin_user = User(
    username="admin",
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    is_admin=True
)

db.add(admin_user)
db.commit()
```

## 🔒 Security Features

- **Password Hashing:** Bcrypt with salt
- **JWT Tokens:** Secure authentication with expiration
- **CORS Protection:** Configurable cross-origin policies
- **Input Validation:** Pydantic schemas for all endpoints
- **SQL Injection Protection:** SQLAlchemy ORM parameterized queries

## 📊 Monitoring & Health

- **Health Check:** `GET /health`
- **API Status:** `GET /`
- **Database Status:** Automatic health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions or issues, please contact Robinson or create an issue in the repository.

---

**Built with ❤️ by Robinson**
