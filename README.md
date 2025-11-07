# Tinko Recovery Platform

A comprehensive recovery and authentication platform built with FastAPI (backend) and Next.js (frontend).

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** or **yarn**
- **PostgreSQL** database (we recommend [Neon](https://neon.tech))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git
   cd STEALTH-TINKO
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   
   # Windows (Git Bash)
   source .venv/Scripts/activate
   
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd tinko-console
   npm install
   cd ..
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

   **Required variables:**
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Random secret for encryption
   - `JWT_SECRET`: Secret for JWT tokens

6. **Run the application**
   ```bash
   bash start-all.sh
   ```

   The application will start:
   - **Backend**: http://127.0.0.1:8010
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://127.0.0.1:8010/docs

## 📋 Features

- **User Authentication**: Email + Password with OTP verification
- **Session Management**: Secure HttpOnly cookies with JWT
- **Rate Limiting**: Protection against brute force attacks
- **Recovery System**: Comprehensive recovery workflows
- **Analytics Dashboard**: Track and monitor activities
- **Responsive UI**: Modern Next.js frontend with Tailwind CSS

## 🛠️ Development

### Backend (FastAPI)

```bash
# Run backend only
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

# Run tests
pytest

# Check code quality
black app/
flake8 app/
```

### Frontend (Next.js)

```bash
cd tinko-console

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

## 📁 Project Structure

```
.
├── app/                      # Backend application
│   ├── routers/             # API routes
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth_schemas.py      # Authentication schemas
│   ├── main.py              # FastAPI application
│   └── services/            # Business logic
│
├── tinko-console/           # Frontend application
│   ├── app/                 # Next.js app directory
│   │   ├── auth/           # Authentication pages
│   │   ├── api/            # API routes
│   │   └── dashboard/      # Dashboard pages
│   ├── lib/                # Utility functions
│   │   ├── api.ts          # API client
│   │   ├── auth0.ts        # Auth0 helpers
│   │   ├── session.ts      # Session management
│   │   └── rate-limit.ts   # Rate limiting
│   └── components/         # React components
│
├── migrations/              # Database migrations
├── tests/                   # Backend tests
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── start-all.sh           # Startup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Essential variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `JWT_SECRET`: JWT signing secret
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

**Optional variables:**
- `OTP_DEV_ECHO=true`: Display OTP in terminal (development only)
- `SMTP_HOST`: Email server host
- `SMTP_PORT`: Email server port
- `AUTH0_*`: Auth0 configuration (if using Auth0)

### Database Setup

1. Create a PostgreSQL database (we recommend [Neon](https://neon.tech))
2. Set `DATABASE_URL` in `.env`
3. Run migrations:
   ```bash
   # Migrations run automatically on startup
   # Or manually with Alembic:
   alembic upgrade head
   ```

## 🧪 Testing

### Run Startup Tests
```bash
bash test-startup.sh
```

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Tests
```bash
cd tinko-console

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

## 📚 API Documentation

Once the backend is running, access the interactive API documentation at:
- **Swagger UI**: http://127.0.0.1:8010/docs
- **ReDoc**: http://127.0.0.1:8010/redoc

## 🔐 Authentication Flow

1. **Registration**
   - User submits email, password, and details
   - System generates 6-digit OTP
   - OTP sent via email (or displayed in terminal if `OTP_DEV_ECHO=true`)
   
2. **OTP Verification**
   - User enters OTP code
   - System verifies and activates account
   
3. **Login**
   - User submits credentials
   - System returns JWT access token
   
4. **Authenticated Requests**
   - Include token in `Authorization: Bearer <token>` header

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**
   - Solution: Activate virtual environment and install dependencies
   ```bash
   source .venv/Scripts/activate  # Windows Git Bash
   pip install -r requirements.txt
   ```

2. **"Port already in use"**
   - Solution: Kill existing process or change port
   ```bash
   # Windows
   netstat -ano | findstr :8010
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -ti:8010 | xargs kill -9
   ```

3. **"Cannot connect to database"**
   - Solution: Verify `DATABASE_URL` in `.env`
   - Ensure database server is running and accessible

4. **Frontend build errors**
   - Solution: Delete `.next` folder and rebuild
   ```bash
   cd tinko-console
   rm -rf .next node_modules
   npm install
   npm run dev
   ```

For detailed troubleshooting, see [SETUP_VERIFICATION.md](./SETUP_VERIFICATION.md)

## 📝 Documentation

- [Setup Verification Guide](./SETUP_VERIFICATION.md) - Complete setup verification steps
- [OTP Testing Guide](./OTP_TESTING_GUIDE.md) - How to test OTP functionality
- [TypeScript Fixes](./TYPESCRIPT_FIXES.md) - Recent TypeScript improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🔗 Links

- **Repository**: https://github.com/stealthorga-crypto/STEALTH-TINKO
- **Issues**: https://github.com/stealthorga-crypto/STEALTH-TINKO/issues

## 👥 Support

If you encounter any issues:
1. Check the [Setup Verification Guide](./SETUP_VERIFICATION.md)
2. Review the [Troubleshooting](#-troubleshooting) section
3. Run `bash test-startup.sh` to diagnose setup issues
4. Open an issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)

---

**Happy coding! 🚀**
