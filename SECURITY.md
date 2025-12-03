# Flask Application Security Features

## Overview

This Flask application implements comprehensive security best practices including rate limiting, security headers, input validation, and authentication security.

## Security Features Implemented

### 1. Rate Limiting (Flask-Limiter)

**Package**: `Flask-Limiter>=3.5.0`

Rate limiting is applied to all endpoints to prevent abuse and DDoS attacks.

#### Configuration
- **Storage**: Redis (production) or in-memory (development)
- **Default Limits**: 200 requests per day, 50 per hour
- **Configurable via**: `REDIS_URL` environment variable

#### Endpoint-Specific Limits

**Authentication Endpoints:**
- `/register` - 5 requests per hour
- `/verify-otp` - 10 requests per hour
- `/resend-otp` - 3 requests per hour
- `/login` - 10 requests per 15 minutes
- `/google` - 20 requests per hour
- `/send-token` - 3 requests per hour
- `/reset-password` - 5 requests per hour

**Payment Endpoints:**
- `/create-order` - 10 requests per minute
- `/verify-payment` - 20 requests per minute
- `/create-checkout-session` - 10 requests per minute

**File Upload Endpoints:**
- `/upload` - 20 requests per hour
- `/download/<id>` - 100 requests per hour
- `/upload-course-thumbnail` - 20 requests per hour
- `/upload-profile-picture` - 10 requests per hour

**Public Endpoints:**
- General endpoints - 60 requests per minute
- Search/listing - 30 requests per minute

### 2. Security Headers (Flask-Talisman)

**Package**: `Flask-Talisman>=1.1.0`

Automatically adds security headers to all responses:

- **HSTS** (HTTP Strict Transport Security): Forces HTTPS connections
- **CSP** (Content Security Policy): Prevents XSS attacks
- **X-Frame-Options**: Prevents clickjacking (SAMEORIGIN)
- **X-Content-Type-Options**: Prevents MIME sniffing (nosniff)
- **X-XSS-Protection**: Enables browser XSS protection
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features

#### Content Security Policy

```python
CSP_POLICY = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", "https://checkout.razorpay.com", "https://accounts.google.com"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'font-src': ["'self'", "data:"],
    'connect-src': ["'self'", "https://api.razorpay.com"],
    'frame-src': ["'self'", "https://api.razorpay.com", "https://accounts.google.com"],
}
```

### 3. Failed Login Protection

**Location**: `utils/security.py`

Implements account lockout and IP blocking after failed login attempts.

#### Features:
- **Failed Attempt Tracking**: Tracks failed login attempts per email and IP
- **Account Lockout**: Locks account after 5 failed attempts (configurable)
- **Lockout Duration**: 30 minutes (configurable)
- **IP Blocking**: Blocks suspicious IPs
- **Automatic Reset**: Resets counter on successful login

#### Configuration:
```bash
MAX_LOGIN_ATTEMPTS=5        # Maximum failed attempts before lockout
LOCKOUT_DURATION=30         # Lockout duration in minutes
```

### 4. Input Validation & Sanitization

**Location**: `utils/validators.py`, `utils/security.py`

#### Validation Features:
- **Email Validation**: RFC-compliant email validation
- **Password Strength**: Enforces strong passwords (8+ chars, uppercase, lowercase, digit, special char)
- **SQL Injection Prevention**: Detects common SQL injection patterns
- **XSS Prevention**: Detects and blocks XSS attempts
- **File Upload Validation**: Validates file types, sizes, and names
- **Path Traversal Prevention**: Blocks directory traversal attempts

#### Suspicious Pattern Detection:
```python
# SQL Injection patterns detected
"' OR '1'='1", "'; DROP TABLE", "UNION SELECT", etc.

# XSS patterns detected
"<script>", "javascript:", "onerror=", "onload=", "<iframe>", etc.
```

### 5. Secure Session Management

**Configuration**:
```python
SESSION_COOKIE_SAMESITE = 'None'    # Required for cross-site
SESSION_COOKIE_SECURE = True        # HTTPS only
SESSION_COOKIE_HTTPONLY = True      # Prevents JavaScript access
```

### 6. Request Tracking & Logging

**Location**: `utils/middleware.py`

#### Features:
- **Request ID**: Unique ID for each request
- **Security Event Logging**: Logs all security-related events
- **Request/Response Logging**: Comprehensive logging with timing
- **Audit Trail**: Tracks sensitive operations

### 7. File Upload Security

**Location**: `utils/security.py` - `validate_file_upload_security()`

#### Protections:
- Extension whitelist validation
- Double extension detection (e.g., file.php.jpg)
- Null byte injection prevention
- Path traversal prevention
- File size limits
- MIME type validation

### 8. CORS Configuration

**Allowed Origins**:
- `http://localhost:5173` (React dev)
- `http://localhost:5174` (React dev)
- `http://127.0.0.1:3000`
- Production frontend URLs (from environment)

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

**Credentials**: Supported

## Environment Variables

### Required for Production

```bash
# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Rate Limiting
REDIS_URL=redis://localhost:6379/0
RATELIMIT_ENABLED=true

# Security Headers
SECURITY_HEADERS_ENABLED=true
FORCE_HTTPS=true

# Failed Login Protection
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=30

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Frontend URLs
FRONTEND_URL_STUDENTS=https://students.yourdomain.com
FRONTEND_URL_ADMIN=https://admin.yourdomain.com
```

### Optional

```bash
# Rate Limiting
RATELIMIT_DEFAULT="200 per day, 50 per hour"

# Upload Configuration
UPLOAD_FOLDER=/path/to/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up Redis** (recommended for production):
```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
# Windows: Download from https://redis.io/download
# Linux: sudo apt-get install redis-server
# Mac: brew install redis
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**:
```bash
python main.py
```

## Testing Rate Limits

### Test Login Rate Limit
```bash
# Make 11 rapid requests (limit is 10 per 15 minutes)
for i in {1..11}; do
  curl -X POST http://localhost:5000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
  echo ""
done
```

Expected: First 10 succeed (with 401), 11th returns 429 (Too Many Requests)

### Test Account Lockout
```bash
# Make 6 failed login attempts with same email
for i in {1..6}; do
  curl -X POST http://localhost:5000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrongpassword"}'
  echo ""
done
```

Expected: After 5 attempts, account is locked for 30 minutes

## Security Headers Verification

```bash
# Check security headers
curl -I https://your-api.com/api/v1/

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: ...
# Referrer-Policy: strict-origin-when-cross-origin
```

## Monitoring & Logs

### Security Events
All security events are logged to `security.log` with the following information:
- Timestamp
- Event type (FAILED_LOGIN, ACCOUNT_LOCKED, IP_BLOCKED, etc.)
- IP address
- User agent
- Additional details

### Log Locations
- **Application logs**: Console output
- **Security logs**: Logged via Python logging module
- **Request logs**: Includes request ID, duration, status code

## Best Practices

1. **Always use HTTPS in production** - Set `FORCE_HTTPS=true`
2. **Use Redis for rate limiting** - In-memory storage doesn't work across multiple instances
3. **Rotate secrets regularly** - Update `SECRET_KEY` and `JWT_SECRET_KEY` periodically
4. **Monitor security logs** - Set up alerts for suspicious activity
5. **Keep dependencies updated** - Regularly update security packages
6. **Use strong passwords** - Enforce password policy on all accounts
7. **Enable 2FA** - Consider implementing two-factor authentication
8. **Regular security audits** - Review and test security measures periodically

## Troubleshooting

### Rate Limit Not Working
- Check if `RATELIMIT_ENABLED=true` in environment
- Verify Redis connection if using Redis storage
- Check logs for rate limiter initialization

### Security Headers Not Applied
- Verify `SECURITY_HEADERS_ENABLED=true`
- Check if Talisman is initialized in app.py
- Some headers may conflict with CORS - adjust CSP as needed

### Account Lockout Issues
- Check `MAX_LOGIN_ATTEMPTS` and `LOCKOUT_DURATION` settings
- Failed attempts are stored in memory - will reset on server restart
- For production, consider using Redis for persistent storage

## Security Checklist

- [x] Rate limiting enabled on all endpoints
- [x] Security headers configured
- [x] HTTPS enforced in production
- [x] Strong password policy enforced
- [x] Failed login tracking implemented
- [x] Account lockout mechanism active
- [x] Input validation on all endpoints
- [x] SQL injection prevention
- [x] XSS prevention
- [x] File upload security
- [x] CORS properly configured
- [x] Secure session cookies
- [x] Request logging enabled
- [x] Security event logging active

## Additional Security Recommendations

1. **Database Security**:
   - Use parameterized queries (already implemented via SQLAlchemy)
   - Encrypt sensitive data at rest
   - Regular database backups

2. **API Security**:
   - Consider implementing API versioning
   - Add request signing for sensitive operations
   - Implement webhook signature verification

3. **Infrastructure**:
   - Use a Web Application Firewall (WAF)
   - Implement DDoS protection at infrastructure level
   - Regular security scanning and penetration testing

4. **Compliance**:
   - GDPR compliance for user data
   - PCI DSS compliance for payment data
   - Regular security audits

## Support

For security issues or questions, please contact the development team.

**Never disclose security vulnerabilities publicly.**
