# AI First Academy - Backend API Platform

A comprehensive RESTful API powering an online Learning Management System (LMS) with advanced security, payment processing, and certification capabilities.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Security Features](#security-features)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

AI First Academy Backend API is a production-ready learning management system supporting three user roles (Students, Instructors, and Administrators) with enterprise-grade features:

- **Advanced Authentication**: OTP-based registration, JWT tokens, Google OAuth 2.0
- **Security First**: Rate limiting, brute-force protection, IP blocking, input validation
- **Payment Integration**: Dual gateway support (Razorpay & Stripe) with webhook handling
- **Automated Certification**: PDF generation with public verification system
- **Live Sessions**: Integrated virtual classroom scheduling with Zoom/Google Meet
- **Rich Content Management**: Hierarchical course structure with progress tracking
- **Real-time Notifications**: In-app and email notifications system
- **Admin Analytics**: Comprehensive dashboard with revenue and user insights

## ✨ Features

### 🔐 Authentication & Security

- **OTP-Based Registration**: Phone verification via Twilio before account creation
- **JWT Authentication**: Access and refresh token flow with token blacklisting on logout
- **Google OAuth 2.0**: Social login supporting both student and admin client types
- **Password Management**: Secure reset with token-based email verification
- **Rate Limiting**: Enforced limits (5 registrations/hour, 10 logins/15 min)
- **Brute-Force Protection**: Account lockout after 5 failed attempts for 30 minutes
- **IP Blocking**: Temporary blocking of suspicious IP addresses
- **Input Validation**: SQL injection and XSS pattern detection

### 👥 User Management

- **Role-Based Access Control (RBAC)**: Decorators enforce permissions (`@admin_required`, `@instructor_required`)
- **Profile Management**: Update personal details, bio, and profile picture uploads
- **Student Dashboard**: Enrolled courses, completed courses, certificates, payment history
- **Admin User Management**: Search, filter, edit, deactivate users, promote to instructors

### 📚 Course & Content Management

- **Hierarchical Structure**: Master Category → Sub Category → Course → Module → Lesson → Resources
- **Course Lifecycle**: Draft and Published states with visibility control
- **Rich Metadata**: Title, description, price, currency, difficulty, duration, learning outcomes
- **Prerequisites System**: Enforce course dependencies before enrollment
- **Lesson Resources**: Attach PDF, video, audio files with upload/download APIs
- **Thumbnail Management**: Upload and update course cover images
- **Mode of Conduct**: Support for ONLINE and OFFLINE course delivery

### 📊 Enrollment & Progress Tracking

- **Smart Enrollment**: Unique constraint per user-course pair with re-enrollment support
- **Lesson Progress**: Track completion status, timestamps, and watch time
- **Course Completion**: Automatic progress calculation; marks completion at 100%
- **Access Control**: Full content for enrolled users; preview mode for guests

### 💳 Payment Processing

**Razorpay Integration:**
- Order creation and signature verification
- Webhook handling for `payment.captured` events
- Transaction history and invoice generation

**Stripe Integration:**
- Checkout session creation
- Webhook handling for `checkout.session.completed` and `checkout.session.expired`
- Refund request workflow

### 🏆 Certification System

- **Automated Generation**: PDF certificates via ReportLab upon course completion
- **Unique Format**: Certificate number format `AIFA-{course_id}-{user_id}-{uuid}`
- **Public Verification**: `/verify/{certificate_number}` endpoint for authenticity checks
- **Bulk Generation**: Admin can generate certificates for all completed enrollments

### 🎥 Live Sessions

- **Session Scheduling**: Create sessions with title, description, time, and duration
- **Meeting Integration**: Store meeting URLs, IDs, and passwords (Zoom/Google Meet)
- **Access Control**: Only enrolled students, instructors, or admins can join
- **Join Window**: Accessible 15 minutes before start until session end
- **Recording Storage**: Optional recording URL for post-session access
- **Email Notifications**: Automated alerts to enrolled students

### 🔔 Notification System

- **In-App Notifications**: CRUD operations with read/unread status tracking
- **Targeted Notifications**: Send to specific users or by role
- **Broadcast Messages**: Mass notifications to all active users
- **Email Integration**: Optional delivery via SendGrid/Flask-Mail
- **User Preferences**: Customizable notification settings

### 📁 File Management

- **Centralized Service**: `FileService` for saving, deleting, and serving files
- **Supported Types**: Images, PDFs, videos, audio, documents (txt, doc, docx, ppt, pptx)
- **Upload Endpoints**: Lesson resources, course thumbnails, profile pictures
- **Security**: Extension validation, path traversal protection, null byte detection

### 🌐 Public API

- **Unauthenticated Access**: Browse categories, subcategories, and courses without login
- **Course Search**: Filter by title, description, and short description
- **Content Restriction**: Video URLs hidden from non-enrolled users

### 📈 Admin Dashboard

- **Statistics**: Total users, courses, enrollments, revenue (all-time and monthly)
- **Recent Activity**: Latest registrations, enrollments, payments
- **Analytics**: Revenue by month, enrollments by month, popular courses ranking
- **Course Moderation**: Update course status (publish/unpublish)
- **Payment Overview**: Filter payments by status, user, or course

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Flask 3.x with Blueprint modularization |
| **Database** | PostgreSQL with SQLAlchemy ORM |
| **Migrations** | Flask-Migrate (Alembic) |
| **Authentication** | Flask-JWT-Extended |
| **Email** | Flask-Mail + SendGrid |
| **SMS** | Twilio Verify API |
| **Payments** | Stripe SDK, Razorpay SDK |
| **PDF Generation** | ReportLab |
| **Rate Limiting** | Flask-Limiter |
| **CORS** | Flask-CORS |
| **OAuth** | Google OAuth 2.0 |

## 📦 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (for rate limiting and caching)
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)
- Active accounts for:
  - Twilio (SMS/OTP)
  - SendGrid (Email)
  - Stripe (Payments)
  - Razorpay (Payments)
  - Google Cloud (OAuth)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-first-academy-backend.git
cd ai-first-academy-backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create Environment File

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SESSION_SECRET=your-session-secret-key-here
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_academy

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Redis Configuration (for rate limiting)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Flask-Mail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@aifirstacademy.com

# SendGrid Configuration
SENDGRID_API_KEY=your-sendgrid-api-key

# Twilio Configuration (SMS/OTP)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_VERIFY_SERVICE_SID=your-twilio-verify-service-sid

# Stripe Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-razorpay-webhook-secret

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Frontend URLs (for CORS)
FRONTEND_URL_STUDENTS=http://localhost:3000
FRONTEND_URL_ADMIN=http://localhost:3001

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=52428800  # 50MB

# Security Configuration
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1
```

### 2. Generate Secret Keys

```python
# Run this in Python console to generate secure keys
import secrets

print("SESSION_SECRET:", secrets.token_hex(32))
print("JWT_SECRET_KEY:", secrets.token_hex(32))
```

### 3. External Service Setup

**Twilio Setup:**
1. Create account at https://www.twilio.com
2. Get Account SID and Auth Token from Console
3. Create a Verify Service and get Service SID

**SendGrid Setup:**
1. Create account at https://sendgrid.com
2. Generate API Key from Settings → API Keys

**Stripe Setup:**
1. Create account at https://stripe.com
2. Get Secret Key from Developers → API Keys
3. Set up webhook endpoint and get Webhook Secret

**Razorpay Setup:**
1. Create account at https://razorpay.com
2. Get Key ID and Key Secret from Settings → API Keys
3. Set up webhook and get Webhook Secret

**Google OAuth Setup:**
1. Go to Google Cloud Console
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URIs

## 🗄️ Database Setup

### 1. Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_academy;

# Create user (optional)
CREATE USER ai_academy_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE ai_academy TO ai_academy_user;

# Exit
\q
```

### 2. Initialize and Run Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial database schema"

# Apply migrations to database
flask db upgrade
```

### 3. Create Admin User (Optional)

```python
# Run Python shell
flask shell

# Create admin user
from models import User, db
from werkzeug.security import generate_password_hash

admin = User(
    email='admin@aifirstacademy.com',
    phone_number='+1234567890',
    first_name='Admin',
    last_name='User',
    role='admin',
    is_active=True,
    is_email_verified=True,
    is_phone_verified=True
)
admin.set_password('Admin@123')
db.session.add(admin)
db.session.commit()
print(f"Admin user created with ID: {admin.id}")
```

## 🏃 Running the Application

### Development Server

```bash
# Make sure virtual environment is activated
python main.py

# Or using Flask CLI
flask run

# With specific host and port
flask run --host=0.0.0.0 --port=5000
```

The API will be available at `http://localhost:5000/api/v1`

### Production Server

```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# With more workers for better performance
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - app:app
```

## 📚 API Documentation

### Base URL
```
Development: http://localhost:5000/api/v1
Production: https://your-domain.com/api/v1
```

### Authentication Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/auth/register/send-otp` | Send OTP to phone | 5/hour |
| POST | `/auth/register/verify-otp` | Verify OTP and create account | 5/hour |
| POST | `/auth/login` | User login with email/password | 10/15min |
| POST | `/auth/google` | Google OAuth login | 10/15min |
| POST | `/auth/refresh` | Refresh JWT access token | 20/hour |
| POST | `/auth/logout` | Logout and blacklist token | - |
| POST | `/auth/password-reset/request` | Request password reset | 3/hour |
| POST | `/auth/password-reset/verify` | Reset password with token | 5/hour |
| GET | `/auth/profile` | Get current user profile | - |
| PUT | `/auth/profile` | Update user profile | - |
| POST | `/auth/profile/picture` | Upload profile picture | - |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/dashboard` | Get student dashboard stats |
| GET | `/users/enrolled-courses` | List enrolled courses |
| GET | `/users/completed-courses` | List completed courses |
| GET | `/users/certificates` | List earned certificates |

### Course Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses` | List all published courses |
| POST | `/courses` | Create new course (Instructor) |
| GET | `/courses/{id}` | Get course details |
| PUT | `/courses/{id}` | Update course (Instructor) |
| DELETE | `/courses/{id}` | Delete course (Instructor/Admin) |
| POST | `/courses/{id}/thumbnail` | Upload course thumbnail |
| GET | `/courses/{id}/modules` | Get course modules |
| POST | `/courses/{id}/modules` | Create module |
| GET | `/courses/{id}/prerequisites` | Get course prerequisites |
| POST | `/courses/{id}/prerequisites` | Add prerequisites |

### Enrollment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollments` | Enroll in course (after payment) |
| GET | `/enrollments/{id}` | Get enrollment details |
| GET | `/enrollments/{id}/progress` | Get course progress |
| POST | `/enrollments/{id}/lessons/{lesson_id}/complete` | Mark lesson complete |

### Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/razorpay/create-order` | Create Razorpay order |
| POST | `/payments/razorpay/verify` | Verify Razorpay payment |
| POST | `/payments/razorpay/webhook` | Razorpay webhook handler |
| POST | `/payments/stripe/create-checkout` | Create Stripe checkout session |
| POST | `/payments/stripe/webhook` | Stripe webhook handler |
| GET | `/payments/history` | Get payment history |
| POST | `/payments/{id}/refund-request` | Request refund |

### Certificate Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/certificates` | List user certificates |
| GET | `/certificates/{id}` | Get certificate details |
| GET | `/certificates/{id}/download` | Download PDF certificate |
| GET | `/certificates/verify/{certificate_number}` | Verify certificate authenticity |
| POST | `/certificates/generate/{enrollment_id}` | Generate certificate (Admin) |
| POST | `/certificates/bulk-generate/{course_id}` | Bulk generate for course (Admin) |

### Live Session Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/live-sessions` | List upcoming sessions |
| POST | `/live-sessions` | Create session (Instructor) |
| GET | `/live-sessions/{id}` | Get session details |
| PUT | `/live-sessions/{id}` | Update session (Instructor) |
| DELETE | `/live-sessions/{id}` | Cancel session (Instructor) |
| GET | `/live-sessions/{id}/join` | Get meeting URL (Enrolled only) |
| POST | `/live-sessions/{id}/recording` | Add recording URL (Instructor) |

### Notification Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List user notifications |
| GET | `/notifications/unread-count` | Get unread count |
| PUT | `/notifications/{id}/read` | Mark as read |
| PUT | `/notifications/read-all` | Mark all as read |
| DELETE | `/notifications/{id}` | Delete notification |
| POST | `/notifications/send` | Send notification (Admin) |
| POST | `/notifications/broadcast` | Broadcast to all (Admin) |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard` | Get dashboard statistics |
| GET | `/admin/analytics/revenue` | Revenue analytics by month |
| GET | `/admin/analytics/enrollments` | Enrollment analytics by month |
| GET | `/admin/analytics/popular-courses` | Most popular courses |
| GET | `/admin/users` | List all users with filters |
| GET | `/admin/users/{id}` | Get user details |
| PUT | `/admin/users/{id}` | Update user |
| POST | `/admin/users/{id}/promote` | Promote to instructor |
| PUT | `/admin/users/{id}/deactivate` | Deactivate user |
| GET | `/admin/courses/pending` | List courses pending review |
| PUT | `/admin/courses/{id}/publish` | Publish course |
| GET | `/admin/payments` | List all payments |

### Public API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/public/categories` | List master categories |
| GET | `/public/categories/{id}/subcategories` | List subcategories |
| GET | `/public/subcategories/{id}/courses` | List courses in subcategory |
| GET | `/public/courses/{id}` | Get public course details |
| GET | `/public/courses/search` | Search courses |

For detailed request/response examples and authentication requirements, see the complete [API Documentation](./API_DOCUMENTATION.md).

## 📁 Project Structure

```
FlaskRest/
├── app.py                          # Application factory, extensions, blueprint registration
├── main.py                         # Entry point (runs development server)
├── config.py                       # Configuration settings
├── models.py                       # SQLAlchemy models (15+ tables)
├── auth.py                         # Authentication helpers and decorators
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not in repo)
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── AGENTS.md                      # Developer onboarding guide
│
├── routes/                        # API endpoints organized by domain
│   ├── __init__.py
│   ├── auth_routes.py            # Authentication & authorization
│   ├── user_routes.py            # User profile and dashboard
│   ├── course_routes.py          # Course CRUD operations
│   ├── admin_routes.py           # Admin dashboard and management
│   ├── payment_routes.py         # Payment gateway integration
│   ├── certificate_routes.py    # Certificate generation and verification
│   ├── live_session_routes.py   # Live session management
│   ├── notification_routes.py   # Notification system
│   ├── file_routes.py            # File upload/download
│   ├── enrollments_routes.py    # Enrollment and progress
│   ├── public_routes.py          # Public API endpoints
│   ├── master_routes.py          # Master categories
│   ├── subcategory_routes.py    # Subcategories
│   ├── modules_routes.py         # Course modules
│   ├── lessons_routes.py         # Lessons
│   ├── lessons_resources_routes.py # Lesson resources
│   ├── prerequisites.py          # Course prerequisites
│   └── helper_routes.py          # Utility endpoints
│
├── services/                      # Business logic services
│   ├── __init__.py
│   ├── email_service.py          # Email sending via SendGrid/Flask-Mail
│   ├── sms_service.py            # SMS/OTP via Twilio
│   ├── file_service.py           # File upload/storage management
│   ├── certificate_service.py   # PDF certificate generation
│   ├── payment_service.py        # Stripe payment processing
│   └── razor_payment_service.py  # Razorpay payment processing
│
├── utils/                         # Utility modules
│   ├── __init__.py
│   ├── validators.py             # Input validation functions
│   ├── security.py               # Security utilities (IP blocking, etc.)
│   ├── decorators.py             # Custom decorators (rate limiting, auth)
│   ├── helpers.py                # Helper functions
│   └── middleware.py             # Request/response middleware
│
├── static/                        # Static file storage
│   └── uploads/                  # Uploaded files
│       ├── thumbnails/
│       ├── resources/
│       ├── profiles/
│       └── certificates/
│
├── migrations/                    # Database migration scripts
│   ├── versions/
│   └── alembic.ini
│
├── instance/                      # Instance-specific files
│   └── dev.db                    # SQLite for development (optional)
│
└── tests/                         # Unit and integration tests
    ├── __init__.py
    ├── test_auth.py
    ├── test_courses.py
    ├── test_payments.py
    ├── test_enrollments.py
    └── test_certificates.py
```

## 🔒 Security Features

### Implemented Security Measures

| Feature | Implementation |
|---------|----------------|
| **Rate Limiting** | Flask-Limiter with Redis backend |
| **Brute-Force Protection** | `FailedLoginTracker` with 30-min lockout |
| **IP Blocking** | `IPBlocker` utility for suspicious IPs |
| **Input Validation** | SQL injection and XSS pattern detection |
| **Password Security** | Werkzeug PBKDF2 SHA256 hashing |
| **JWT Security** | Token blacklisting on logout |
| **CORS Protection** | Configured for specific frontend origins |
| **File Upload Security** | Extension validation, path traversal protection |
| **SQL Injection Prevention** | SQLAlchemy ORM with parameterized queries |
| **HTTPS Enforcement** | Flask-Talisman in production |
| **Secure Headers** | X-Content-Type-Options, X-Frame-Options, CSP |

### Security Best Practices

```python
# All passwords are hashed
user.set_password('plain_password')

# JWT tokens expire and can be blacklisted
access_token = create_access_token(identity=user.id)

# Rate limiting on sensitive endpoints
@limiter.limit("5 per hour")
def register():
    pass

# Role-based access control
@admin_required
def admin_dashboard():
    pass

# Input validation
if detect_sql_injection(user_input) or detect_xss(user_input):
    return {"error": "Invalid input"}, 400

# File upload validation
allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
if not file.filename.lower().endswith(tuple(allowed_extensions)):
    return {"error": "Invalid file type"}, 400
```

## 🧪 Testing

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_register_success
```

## 🚀 Deployment

### Docker Deployment

**1. Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directories
RUN mkdir -p static/uploads/{thumbnails,resources,profiles,certificates}

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

**2. Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./static:/app/static

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: ai_academy
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**3. Deploy:**

```bash
docker-compose up -d
docker-compose exec web flask db upgrade
```

### Render Deployment

**1. Create `render.yaml`:**

```yaml
services:
  - type: web
    name: ai-academy-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: ai-academy-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: ai-academy-redis
          type: redis
          property: connectionString

databases:
  - name: ai-academy-db
    databaseName: ai_academy
    user: ai_academy_user

  - name: ai-academy-redis
    type: redis
```

**2. Environment Variables:**

Add all environment variables from `.env` in Render Dashboard under Environment tab.

**3. Deploy:**

Connect your GitHub repository and Render will auto-deploy on push.

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create ai-academy-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SESSION_SECRET=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret
heroku config:set SENDGRID_API_KEY=your-sendgrid-key
# ... set all other variables

# Deploy
git push heroku main

# Run migrations
heroku run flask db upgrade

# View logs
heroku logs --tail
```

## 📊 Monitoring & Logging

```python
# Application logs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"User {user.id} logged in")
logger.warning(f"Failed login attempt for {email}")
logger.error(f"Payment processing failed: {error}")
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write docstrings for all functions
- Add type hints where applicable
- Write unit tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Support & Contact

- **Developer**: Your Name
- **Email**: your-email@example.com
- **Project Link**: https://github.com/yourusername/ai-first-academy-backend
- **Documentation**: https://docs.aifirstacademy.com

## 🙏 Acknowledgments

- Flask and SQLAlchemy communities
- Twilio for OTP services
- SendGrid for email delivery
- Stripe and Razorpay for payment processing
- ReportLab for PDF generation

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Razorpay API Documentation](https://razorpay.com/docs/api/)
- [Twilio Verify API](https://www.twilio.com/docs/verify/api)

---

**Version:** 2.0  
**Last Updated:** December 2024

For detailed developer onboarding and contribution guidelines, please refer to [AGENTS.md](./AGENTS.md)



# API Documentation

This document provides a comprehensive reference for the API endpoints available in the application.

## Base URL
All API endpoints are prefixed with `/api/v1` unless otherwise noted.

## Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/register` | Register a new user (Student/Instructor). | No | 5/min |
| `POST` | `/login` | Login user and return JWT tokens. | No | 5/min |
| `POST` | `/logout` | Logout user and blacklist refresh token. | Yes | - |
| `POST` | `/refresh` | Refresh access token using refresh token. | Yes (Refresh) | - |
| `POST` | `/forgot-password` | Send password reset link to email. | No | - |
| `POST` | `/reset-password/<token>` | Reset password using token. | No | 5/min |
| `POST` | `/change-password` | Change password for logged-in user. | Yes | - |
| `POST` | `/google` | Google OAuth login/registration. | No | 5/min |
| `POST` | `/send-token` | Send OTP for verification. | No | 3/min |
| `POST` | `/verify-otp` | Verify OTP. | No | 5/min |

### Request/Response Details

**POST /register**
*   **Body:** `{ "email": "user@example.com", "password": "password123", "first_name": "John", "last_name": "Doe", "role": "student" }`
*   **Response:** `201 Created` - `{ "message": "User created successfully", "user": {...} }`

**POST /login**
*   **Body:** `{ "email": "user@example.com", "password": "password123" }`
*   **Response:** `200 OK` - `{ "access_token": "...", "refresh_token": "...", "user": {...} }`

---

## User Management (`/users`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/profile` | Get current user's profile. | Yes |
| `PUT` | `/profile` | Update current user's profile. | Yes |
| `GET` | `/my-courses` | Get courses the user is enrolled in. | Yes |
| `GET` | `/my-teaching-courses` | Get courses taught by the user (Instructor). | Yes (Instructor) |

### Request/Response Details

**GET /profile**
*   **Response:** `200 OK` - `{ "user": { "id": 1, "email": "...", ... } }`

**PUT /profile**
*   **Body:** `{ "first_name": "Jane", "bio": "..." }`
*   **Response:** `200 OK` - `{ "message": "Profile updated", "user": {...} }`

---

## Public Routes (`/public`)

| Method | Endpoint | Description | Rate Limit |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-courses` | Get all published courses with filters. | 30/min |
| `GET` | `/get-courses/<id>` | Get details of a specific course. | 30/min |
| `GET` | `/get-categories` | Get all master categories. | 30/min |
| `GET` | `/get-subcategories` | Get all subcategories. | 30/min |
| `POST` | `/search` | Search courses by query. | 20/min |

### Request/Response Details

**GET /get-courses**
*   **Query Params:** `page`, `per_page`, `category_id`, `subcategory_id`, `search`
*   **Response:** `200 OK` - `{ "courses": [...], "pagination": {...} }`

---

## Courses (`/courses`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-courses` | Create a new course. | Yes (Instructor) |
| `GET` | `/get-courses` | Get all courses (Instructor view). | Yes (Instructor) |
| `GET` | `/get-courses/<id>` | Get specific course details. | Yes (Instructor) |
| `PUT` | `/update-courses/<id>` | Update a course. | Yes (Instructor) |
| `DELETE` | `/delete-courses/<id>` | Delete a course. | Yes (Instructor) |

### Request/Response Details

**POST /create-courses**
*   **Body:** `{ "title": "Python 101", "description": "...", "price": 49.99, "subcategory_id": 1 }`
*   **Response:** `201 Created` - `{ "message": "Course created", "course": {...} }`

---

## Master Categories (`/master-categories`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-mastercategories` | Create a master category. | Yes (Admin) |
| `POST` | `/get-mastercategories` | Get all master categories. | Yes (Admin) |
| `POST` | `/get-mastercategories/<id>` | Get a specific master category. | Yes (Admin) |
| `PUT` | `/update-mastercategories/<id>` | Update a master category. | Yes (Admin) |
| `DELETE` | `/delete-mastercategories/<id>` | Delete a master category. | Yes (Admin) |

---

## Subcategories (`/subcategories`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-subcategories` | Create a subcategory. | Yes (Admin) |
| `POST` | `/get-subcategories` | Get all subcategories. | Yes (Admin) |
| `POST` | `/get-subcategories/<id>` | Get a specific subcategory. | Yes (Admin) |
| `PUT` | `/update-subcategories/<id>` | Update a subcategory. | Yes (Admin) |
| `DELETE` | `/delete-subcategories/<id>` | Delete a subcategory. | Yes (Admin) |

---

## Modules (`/modules`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-modules/<course_id>` | Create a module for a course. | Yes (Instructor) |
| `POST` | `/get-modules` | Get all modules. | Yes (Instructor) |
| `POST` | `/get-modules/<id>` | Get a specific module. | Yes (Instructor) |
| `PUT` | `/update-modules/<id>` | Update a module. | Yes (Instructor) |
| `DELETE` | `/delete-modules/<id>` | Delete a module. | Yes (Instructor) |

---

## Lessons (`/lessons`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-lessons/<module_id>` | Create a lesson for a module. | Yes (Instructor) |
| `POST` | `/get-lessons` | Get all lessons. | Yes (Instructor) |
| `POST` | `/get-lessons/<id>` | Get a specific lesson. | Yes (Instructor) |
| `PUT` | `/update-lessons/<id>` | Update a lesson. | Yes (Instructor) |
| `DELETE` | `/delete-lessons/<id>` | Delete a lesson. | Yes (Instructor) |

---

## Lesson Resources (`/lesson-resources`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-lesson-resources/<lesson_id>` | Upload a resource for a lesson. | Yes (Instructor) |
| `POST` | `/get-lesson-resources` | Get all resources. | Yes |
| `POST` | `/get-lesson-resources/<id>` | Get a specific resource. | Yes |
| `PUT` | `/update-lesson-resources/<id>` | Update a resource. | Yes (Instructor) |
| `DELETE` | `/delete-lesson-resources/<id>` | Delete a resource. | Yes (Instructor) |

---

## Prerequisites (`/prerequisites`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-prerequisites/<course_id>` | Add prerequisites to a course. | Yes (Instructor/Admin) |
| `GET` | `/get-prerequisites/<course_id>` | Get prerequisites for a course. | No |
| `PUT` | `/update-prerequisites/<course_id>` | Update prerequisites. | Yes (Instructor/Admin) |
| `DELETE` | `/delete-prerequisites/<course_id>/<prereq_id>` | Remove a prerequisite. | Yes (Instructor/Admin) |

---

## Enrollments (`/enrollments`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-enrollments/<course_id>` | Enroll in a course (Free/Paid). | Yes |
| `GET` | `/get-enrollments` | Get current user's enrollments. | Yes |
| `GET` | `/get-enrollments/<course_id>/progress` | Get course progress. | Yes |
| `GET` | `/get-enrollments/<course_id>/lessons/<lesson_id>/progress` | Update lesson progress. | Yes |

---

## Payments (`/payments`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/create-order` | Create a Razorpay order. | Yes | 10/min |
| `POST` | `/verify-payment` | Verify Razorpay payment. | Yes | 20/min |
| `POST` | `/create-checkout-session` | Create Stripe checkout session. | Yes | 10/min |
| `GET` | `/history` | Get payment history. | Yes | - |
| `GET` | `/<id>` | Get payment details. | Yes | - |
| `POST` | `/<id>/refund` | Request a refund. | Yes | - |

---

## Files (`/files`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/upload` | Upload lesson resource file. | Yes (Instructor) | 20/hour |
| `GET` | `/download/<id>` | Download lesson resource. | Yes (Enrolled) | 100/hour |
| `POST` | `/upload-course-thumbnail` | Upload course thumbnail. | Yes (Instructor) | 20/hour |
| `POST` | `/upload-profile-picture` | Upload profile picture. | Yes | 10/hour |

---

## Notifications (`/notifications`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-notifications` | Get user notifications. | Yes |
| `PUT` | `/<id>/read` | Mark notification as read. | Yes |
| `PUT` | `/mark-all-read` | Mark all as read. | Yes |
| `DELETE` | `/<id>` | Delete notification. | Yes |
| `POST` | `/send` | Send notification to specific users. | Yes (Admin) |
| `POST` | `/broadcast` | Broadcast notification to all users. | Yes (Admin) |

---

## Certificates (`/certificates`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-certificate` | Get user's certificates. | Yes |
| `POST` | `/generate/<course_id>` | Generate certificate for completed course. | Yes |
| `GET` | `/download/<id>` | Download certificate PDF. | Yes |
| `GET` | `/verify/<number>` | Verify certificate validity. | No |

---

## Live Sessions (`/live-sessions`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-live-sessions` | Get live sessions. | Yes |
| `POST` | `/create-live-sessions` | Create a live session. | Yes (Instructor) |
| `GET` | `/get-live-sessions/<id>` | Get session details. | Yes |
| `PUT` | `/update-live-sessions/<id>` | Update session. | Yes (Instructor) |
| `DELETE` | `/delete-live-sessions/<id>` | Delete session. | Yes (Instructor) |
| `GET` | `/get-live-courses/upcoming` | Get upcoming sessions. | Yes |
| `GET` | `/join-live-sessions/<id>/join` | Join a live session. | Yes |

---

## Contact (`/contact`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/contact-forms` | Submit a contact form. | No |
| `GET` | `/contact-forms` | Get all contact forms. | No (Should be Admin) |
| `GET` | `/contact-forms/<id>` | Get specific contact form. | No (Should be Admin) |
| `PUT` | `/contact-forms/<id>` | Update contact form. | No (Should be Admin) |
| `DELETE` | `/contact-forms/<id>` | Delete contact form. | No (Should be Admin) |

### Request/Response Details

**POST /contact-forms**
*   **Body:** `{ "name": "John", "email": "john@example.com", "message": "Hello", "phone_number": "1234567890" }`
*   **Response:** `201 Created` - `{ "id": 1, "name": "John", ... }`

---

## Admin (`/admin`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard` | Get admin dashboard stats. | Yes (Admin) |
| `GET` | `/users` | Get all users. | Yes (Admin) |
| `PUT` | `/users/<id>` | Update user details. | Yes (Admin) |
| `DELETE` | `/users/<id>` | Deactivate user. | Yes (Admin) |
| `GET` | `/courses` | Get all courses. | Yes (Admin) |
| `PUT` | `/courses/<id>/status` | Update course status (publish/draft). | Yes (Admin) |
| `GET` | `/payments` | Get all payments. | Yes (Admin) |
| `GET` | `/analytics` | Get revenue and enrollment analytics. | Yes (Admin) |
