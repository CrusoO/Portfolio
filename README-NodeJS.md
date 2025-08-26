# 🚀 Robinson's Portfolio Backend (Node.js + Audio System)

A complete Node.js/Express backend for Robinson's portfolio website with advanced audio caching, ElevenLabs TTS integration, and comprehensive portfolio management features.

## ✨ Key Features

- **🎤 Audio Caching System** - Advanced caching with ElevenLabs TTS integration
- **🔊 Custom Audio Management** - Upload and manage custom audio files for notes
- **📝 Notes/Blog Management** - Complete CRUD operations with audio integration
- **👤 User Authentication** - JWT-based auth with admin roles
- **⭐ Review System** - User feedback and ratings management
- **📧 Contact Forms** - Professional contact form handling
- **🗄️ PostgreSQL Database** - Robust database with migrations and seeding
- **🔐 Security Features** - Rate limiting, CORS, input validation, password hashing
- **📊 Admin Dashboard APIs** - Complete admin management endpoints
- **☁️ Cloud Ready** - Configured for Render.com deployment

## 🛠️ Tech Stack

- **Backend:** Node.js + Express.js
- **Database:** PostgreSQL with connection pooling
- **Authentication:** JWT + bcryptjs
- **File Upload:** Multer with validation
- **Audio Processing:** ElevenLabs TTS API integration
- **Security:** Helmet, CORS, Rate limiting
- **Deployment:** Render.com ready with Docker support

## 📋 Complete API Endpoints

### 🔐 Authentication
```
POST /api/auth/login          - User login
POST /api/auth/register       - Register new user (admin only)
```

### 🎵 Audio Management
```
GET    /api/audio/cache/:textHash            - Check cached audio
POST   /api/audio/cache                      - Cache new audio
GET    /api/audio/cache/stats                - Get cache statistics (admin)
DELETE /api/audio/cache/cleanup              - Cleanup old cache (admin)
POST   /api/audio/custom                     - Upload custom audio (admin)
GET    /api/audio/custom/note/:noteId        - Get audio for note
GET    /api/audio/custom                     - List all custom audio (admin)
POST   /api/audio/custom/search              - Search custom audio
PATCH  /api/audio/custom/:id/toggle          - Toggle audio status (admin)
DELETE /api/audio/custom/:id                 - Delete custom audio (admin)
```

### 📝 Notes Management
```
GET    /api/notes                - Get published notes
GET    /api/notes/:id            - Get single note with audio
POST   /api/notes                - Create note (admin)
PUT    /api/notes/:id            - Update note (admin)
DELETE /api/notes/:id            - Delete note (admin)
```

### 📞 Contact & Reviews
```
POST   /api/contact              - Submit contact form
GET    /api/contact              - Get submissions (admin)
POST   /api/reviews              - Submit review
GET    /api/reviews              - Get approved reviews
PATCH  /api/reviews/:id/approve  - Approve/reject review (admin)
```

### 🏥 Health & Monitoring
```
GET    /api/health               - Health check endpoint
```

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd CrusoPortfolio-Backend
npm install
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values:
# - Database credentials (PostgreSQL)
# - JWT secret key
# - ElevenLabs API key
# - Other configuration
```

### 3. Database Setup
```bash
# Run database migration
npm run migrate

# Add sample data
npm run seed
```

### 4. Start Development Server
```bash
npm run dev
# Server will start on http://localhost:3000
```

## 📊 Database Schema

The database includes 6 main tables:

- **users** - User accounts with role-based access
- **notes** - Blog posts/notes with publishing status
- **audio_cache** - TTS audio caching with MD5 hashing
- **custom_audio** - Custom uploaded audio files for notes
- **reviews** - User reviews with approval workflow
- **contact_submissions** - Contact form submissions

## 🎤 Audio System Features

### Audio Caching
- **Smart Caching:** MD5 hash-based lookup for duplicate text
- **ElevenLabs Integration:** Seamless TTS generation and caching
- **File Management:** Automatic cleanup of old cache entries
- **Statistics:** Cache usage analytics and monitoring

### Custom Audio
- **File Upload:** Support for MP3, WAV, M4A, OGG, WebM formats
- **Note Integration:** Link custom audio to specific notes
- **Search Functionality:** Search by title, description, or text content
- **Admin Management:** Toggle active status, bulk management

## 🔧 Configuration Options

### Environment Variables
```env
# Server
NODE_ENV=production
PORT=3000
FRONTEND_URL=https://your-frontend.com

# Database (PostgreSQL)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=portfolio_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password

# Security
JWT_SECRET=your-secure-jwt-secret-min-32-chars

# ElevenLabs API
ELEVENLABS_API_KEY=sk_your_api_key_here

# File Storage
AUDIO_STORAGE_PATH=./storage/audio
MAX_FILE_SIZE_MB=10
```

## ☁️ Render.com Deployment

### Automatic Deployment
1. **Connect Repository:** Link your GitHub repo to Render
2. **Use render.yaml:** Pre-configured deployment settings
3. **Environment Variables:** Set in Render dashboard
4. **PostgreSQL Database:** Auto-provisioned with render.yaml

### Manual Deployment Steps
1. Create new Web Service on Render
2. Connect your repository
3. Build Command: `npm install`
4. Start Command: `npm start`
5. Add environment variables
6. Create PostgreSQL database
7. Deploy!

### Environment Setup

1. **Copy the environment template:**
   ```bash
   cp environment.example .env
   ```

2. **Add your API keys to .env:**
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
   SECRET_KEY=your-secure-jwt-secret
   ```

### Environment Variables for Render
```
NODE_ENV=production
JWT_SECRET=<generate-secure-key>
GROQ_API_KEY=<your-groq-api-key>
ELEVENLABS_API_KEY=<your-elevenlabs-api-key>
FRONTEND_URL=<your-frontend-domain>
AUDIO_STORAGE_PATH=/tmp/storage/audio
```

## 🗄️ Database Management

### Migration
```bash
npm run migrate    # Run database schema setup
```

### Seeding
```bash
npm run seed      # Add sample data
```

### Cache Cleanup
```bash
npm run clean-cache        # Clean 30+ day old cache
npm run clean-cache 7      # Clean 7+ day old cache
```

## 📈 Admin Features

### User Management
- Create admin users
- Role-based access control
- Activity tracking

### Content Management  
- CRUD operations for notes
- Publish/unpublish content
- Tag and category management

### Audio Management
- Upload custom audio files
- Cache management and cleanup
- Usage statistics and monitoring

### Review Moderation
- Approve/reject user reviews
- Admin notes and feedback
- Bulk moderation tools

## 🔒 Security Features

- **JWT Authentication** with secure token generation
- **Password Hashing** using bcryptjs with salt
- **Rate Limiting** to prevent abuse
- **Input Validation** for all endpoints
- **CORS Protection** with configurable origins
- **File Upload Security** with type and size validation
- **SQL Injection Protection** via parameterized queries

## 📊 Monitoring & Health

### Health Check
```bash
curl http://localhost:3000/api/health
```

### Cache Statistics
- Total cached files and size
- Usage patterns and trends
- Cleanup recommendations

### Database Statistics
- Connection pool status
- Query performance
- Storage usage

## 🚀 Production Considerations

### File Storage
- **Development:** Local filesystem
- **Production:** Consider AWS S3 or similar cloud storage
- **Backup:** Regular audio file backups recommended

### Database
- **Connection Pooling:** Configured for high performance
- **Indexing:** Optimized indexes for common queries
- **Backup:** Regular PostgreSQL backups essential

### Scaling
- **Horizontal Scaling:** Stateless design allows multiple instances
- **Load Balancing:** Compatible with standard load balancers
- **CDN Integration:** Audio files can be served via CDN

## 🛠️ Development

### Code Structure
```
├── server.js              # Main application file
├── database_schema.sql    # Complete database schema
├── package.json          # Dependencies and scripts
├── .env.example         # Environment template
├── storage/audio/       # Audio file storage
├── scripts/            # Database and utility scripts
│   ├── migrate.js     # Database migration
│   ├── seed.js        # Sample data seeding
│   └── clean-cache.js # Cache cleanup
└── logs/              # Application logs
```

### Key Scripts
- `npm start` - Production server
- `npm run dev` - Development with auto-reload
- `npm run migrate` - Database setup
- `npm run seed` - Add sample data
- `npm run clean-cache` - Cache maintenance

## 📞 Support & Documentation

### API Documentation
- **Health Check:** `GET /api/health`
- **Interactive Docs:** Available when server is running
- **Postman Collection:** Can be generated from endpoints

### Troubleshooting
1. **Database Connection Issues:** Check PostgreSQL credentials
2. **File Upload Errors:** Verify storage directory permissions
3. **Audio Cache Issues:** Check ElevenLabs API key and quotas
4. **Authentication Problems:** Verify JWT secret configuration

---

## 🎯 Ready for Production!

Your Node.js backend is now fully configured with:
- ✅ Complete audio caching and management system
- ✅ ElevenLabs TTS integration ready
- ✅ PostgreSQL database with full schema
- ✅ Render.com deployment configuration
- ✅ Admin dashboard functionality
- ✅ Security and performance optimizations

**Next Steps:**
1. Update your database credentials in `.env`
2. Set your ElevenLabs API key
3. Deploy to Render.com using the provided configuration
4. Run migrations and seeding on your production database
5. Configure your frontend to use the new API endpoints

**Built with ❤️ by Robinson**
