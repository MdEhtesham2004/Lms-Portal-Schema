# Statement of Work (SOW)
## AI First Academy - Backend API Platform

**Version:** 2.0  
**Last Updated:** December 2024

---

## 1. Project Overview

The **AI First Academy** backend is a comprehensive RESTful API powering an online Learning Management System (LMS). It provides secure authentication, course management, payment processing, and certification services for three user roles: **Students**, **Instructors**, and **Administrators**.

---

## 2. Scope of Work

### 2.1. Authentication & Security Module

| Feature | Description |
|---------|-------------|
| **OTP-Based Registration** | Phone verification via Twilio before account creation. |
| **JWT Authentication** | Access and refresh token flow with token blacklisting on logout. |
| **Google OAuth 2.0** | Social login supporting both student and admin client types. |
| **Password Management** | Secure password reset with token-based email verification. |
| **Rate Limiting** | Flask-Limiter enforced limits (e.g., 5 registrations/hour, 10 logins/15 min). |
| **Brute-Force Protection** | `FailedLoginTracker` locks accounts after 5 failed attempts for 30 minutes. |
| **IP Blocking** | `IPBlocker` utility to block suspicious IPs temporarily. |
| **Input Validation** | Detection of SQL injection and XSS patterns in request data. |

### 2.2. User Management

| Feature | Description |
|---------|-------------|
| **Role-Based Access Control (RBAC)** | Decorators (`@admin_required`, `@instructor_required`) enforce permissions. |
| **Profile Management** | Update personal details, bio, and profile picture uploads. |
| **Student Dashboard** | Aggregated stats: enrolled courses, completed courses, certificates, payments. |
| **Admin User Management** | Search, filter, edit, deactivate users. Promote students to instructors. |

### 2.3. Course & Content Management

| Feature | Description |
|---------|-------------|
| **Hierarchical Structure** | `MasterCategory` → `SubCategory` → `Course` → `CourseModule` → `Lesson` → `LessonResource`. |
| **Course Lifecycle** | Statuses: `DRAFT`, `PUBLISHED`. Visibility controlled by `is_active` flag. |
| **Course Metadata** | Title, description, price, currency, difficulty, duration, learning outcomes. |
| **Prerequisites System** | Many-to-many relationship via `CoursePrerequisitesCourses` table. |
| **Lesson Resources** | Attached files (PDF, video, audio) with upload/download APIs. |
| **Thumbnail Management** | Instructor can upload/update course thumbnails. |
| **Mode of Conduct** | Supports `ONLINE` and `OFFLINE` course delivery. |

### 2.4. Enrollment & Progress Tracking

| Feature | Description |
|---------|-------------|
| **Enrollment System** | Unique constraint per user-course pair; supports re-enrollment. |
| **Lesson Progress** | Track `completed` status, `completed_at` timestamp, and `watch_time_seconds`. |
| **Course Completion** | Automatic calculation of `progress_percentage`; marks `completed_at` at 100%. |
| **Access Control** | Enrolled users access full content; previews available for non-enrolled users. |

### 2.5. Payment Processing

| Gateway | Features |
|---------|----------|
| **Razorpay** | Order creation, signature verification, webhook handling (`payment.captured`). |
| **Stripe** | Checkout session creation, webhook (`checkout.session.completed`, `checkout.session.expired`). |
| **Common Features** | Payment history, invoice generation, refund request workflow. |

### 2.6. Certification System

| Feature | Description |
|---------|-------------|
| **Automated Generation** | PDF certificates via `reportlab` upon course completion. |
| **Certificate Format** | Unique number: `AIFA-{course_id}-{user_id}-{uuid}`. |
| **Public Verification** | `/verify/{certificate_number}` endpoint for authenticity checks. |
| **Bulk Generation** | Admin can generate certificates for all completed enrollments in a course. |

### 2.7. Live Sessions

| Feature | Description |
|---------|-------------|
| **Scheduling** | Create sessions with title, description, scheduled time, duration. |
| **Meeting Integration** | Store `meeting_url`, `meeting_id`, `meeting_password` (Zoom/Google Meet). |
| **Access Control** | Only enrolled students, instructors, or admins can join. |
| **Join Window** | Sessions accessible 15 minutes before start until session end. |
| **Recordings** | Optional `recording_url` for post-session access. |
| **Notifications** | Email alerts sent to enrolled students on session creation. |

### 2.8. Notification System

| Feature | Description |
|---------|-------------|
| **In-App Notifications** | CRUD operations with read/unread status tracking. |
| **Targeted Notifications** | Admin can send to specific users or by role. |
| **Broadcast** | Mass notifications to all active users. |
| **Email Integration** | Optional email delivery via SendGrid/Flask-Mail. |
| **Settings** | Placeholder for user notification preferences. |

### 2.9. File Management

| Feature | Description |
|---------|-------------|
| **Upload Service** | Centralized `FileService` for saving, deleting, and serving files. |
| **Supported Types** | Images, PDFs, videos, audio, documents (txt, doc, docx, ppt, pptx). |
| **Upload Endpoints** | Lesson resources, course thumbnails, profile pictures. |
| **Security** | Extension validation, path traversal protection, null byte detection. |

### 2.10. Public API

| Feature | Description |
|---------|-------------|
| **Unauthenticated Access** | Browse master categories, subcategories, and courses without login. |
| **Course Search** | Filter by title, description, short_description. |
| **Content Restriction** | Video URLs hidden from non-enrolled users in public course responses. |

### 2.11. Admin Dashboard

| Feature | Description |
|---------|-------------|
| **Statistics** | Total users, courses, enrollments, revenue (all-time and monthly). |
| **Recent Activity** | Latest registrations, enrollments, payments. |
| **Analytics** | Revenue by month, enrollments by month, popular courses ranking. |
| **Course Moderation** | Update course status (publish/unpublish). |
| **Payment Overview** | Filter payments by status, user, or course. |

---

## 3. Technical Architecture

### 3.1. Technology Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Flask 3.x with Blueprint modularization |
| **Database** | PostgreSQL via SQLAlchemy ORM |
| **Migrations** | Flask-Migrate (Alembic) |
| **Authentication** | Flask-JWT-Extended |
| **Email** | Flask-Mail + SendGrid |
| **SMS** | Twilio Verify API |
| **Payments** | Stripe SDK, Razorpay SDK |
| **PDF Generation** | ReportLab |
| **Rate Limiting** | Flask-Limiter |
| **CORS** | Flask-CORS |

### 3.2. Project Structure

```
FlaskRest/
├── app.py              # Application factory, extensions, blueprint registration
├── main.py             # Entry point (runs dev server)
├── models.py           # SQLAlchemy models (User, Course, Enrollment, etc.)
├── auth.py             # Authentication helpers and decorators
├── config.py           # Configuration settings
├── routes/             # API endpoints organized by domain
│   ├── auth_routes.py
│   ├── user_routes.py
│   ├── course_routes.py
│   ├── admin_routes.py
│   ├── payment_routes.py
│   ├── certificate_routes.py
│   ├── live_session_routes.py
│   ├── notification_routes.py
│   ├── file_routes.py
│   ├── enrollments_routes.py
│   ├── public_routes.py
│   ├── master_routes.py
│   ├── subcategory_routes.py
│   ├── modules_routes.py
│   ├── lessons_routes.py
│   ├── lessons_resources_routes.py
│   ├── prerequisites.py
│   └── helper_routes.py
├── services/           # Business logic services
│   ├── email_service.py
│   ├── sms_service.py
│   ├── file_service.py
│   ├── certificate_service.py
│   ├── payment_service.py (Stripe)
│   └── razor_payment_service.py (Razorpay)
├── utils/              # Utility modules
│   ├── validators.py
│   ├── security.py
│   ├── decorators.py
│   ├── helpers.py
│   └── middleware.py
├── static/             # Static file storage
├── migrations/         # Database migration scripts
└── instance/           # Instance-specific config (SQLite dev DB)
```

### 3.3. API Base URL

All endpoints are prefixed with `/api/v1/`.

---

## 4. Environment Variables Required

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SESSION_SECRET` | Flask session secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` | SMTP configuration |
| `SENDGRID_API_KEY` | SendGrid email service |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE_SID` | Twilio SMS/OTP |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe payments |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | Razorpay payments |
| `GOOGLE_CLIENT_ID` | Google OAuth |
| `FRONTEND_URL_STUDENTS`, `FRONTEND_URL_ADMIN` | CORS origins |

---

## 5. Deliverables

1. **Source Code**: Complete Flask application with modular blueprints.
2. **Database Models**: 15+ SQLAlchemy models with relationships.
3. **REST API**: 80+ endpoints covering all functional modules.
4. **Security Layer**: Rate limiting, brute-force protection, input validation.
5. **Integration Services**: Email, SMS, Payments (Stripe + Razorpay).
6. **Documentation**: `AGENTS.md` (developer guide), `SOW.md` (this document).

---

## 6. Assumptions & Constraints

- **Hosting**: Designed for containerized deployment (Docker-ready with Gunicorn).
- **Frontend**: Separate React/Vue applications consume this API.
- **File Storage**: Local storage by default; can be extended to S3/cloud.
- **Security**: Secrets must be provided via environment variables; never committed.
- **Session Storage**: In-memory for failed login tracking (use Redis in production).
