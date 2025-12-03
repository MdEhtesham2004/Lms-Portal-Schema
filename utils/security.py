"""
Security utilities for the Flask application.
Includes failed login tracking, IP blocking, and security event logging.
"""
import time
import hashlib
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, current_app
from typing import Optional, Dict, Any

# Configure logger
security_logger = logging.getLogger('security')

# In-memory storage for failed attempts (use Redis in production)
failed_login_attempts = defaultdict(list)
blocked_ips = {}
security_events = []


class SecurityMonitor:
    """Monitor and track security events"""
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], severity: str = 'INFO'):
        """Log a security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'details': details,
            'severity': severity,
            'ip': request.remote_addr if request else 'N/A',
            'user_agent': request.headers.get('User-Agent') if request else 'N/A'
        }
        
        security_events.append(event)
        
        # Keep only last 1000 events in memory
        if len(security_events) > 1000:
            security_events.pop(0)
        
        # Log to file
        log_method = getattr(security_logger, severity.lower(), security_logger.info)
        log_method(f"Security Event: {event_type} - {details}")
        
        return event
    
    @staticmethod
    def get_recent_events(limit: int = 100) -> list:
        """Get recent security events"""
        return security_events[-limit:]


class FailedLoginTracker:
    """Track failed login attempts and implement account lockout"""
    
    @staticmethod
    def get_identifier(email: str = None, ip: str = None) -> str:
        """Get unique identifier for tracking"""
        if email:
            return f"email:{email.lower()}"
        if ip:
            return f"ip:{ip}"
        return f"ip:{request.remote_addr}"
    
    @staticmethod
    def record_failed_attempt(email: str = None, ip: str = None):
        """Record a failed login attempt"""
        identifier = FailedLoginTracker.get_identifier(email, ip)
        current_time = time.time()
        
        # Add failed attempt
        failed_login_attempts[identifier].append(current_time)
        
        # Clean old attempts (older than 1 hour)
        failed_login_attempts[identifier] = [
            t for t in failed_login_attempts[identifier]
            if current_time - t < 3600
        ]
        
        # Log security event
        SecurityMonitor.log_security_event(
            'FAILED_LOGIN',
            {
                'identifier': identifier,
                'attempt_count': len(failed_login_attempts[identifier])
            },
            'WARNING'
        )
        
        # Check if should block
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        if len(failed_login_attempts[identifier]) >= max_attempts:
            FailedLoginTracker.block_identifier(identifier)
    
    @staticmethod
    def block_identifier(identifier: str):
        """Block an identifier (email or IP)"""
        lockout_duration = current_app.config.get('LOCKOUT_DURATION', 30)  # minutes
        blocked_until = time.time() + (lockout_duration * 60)
        blocked_ips[identifier] = blocked_until
        
        SecurityMonitor.log_security_event(
            'ACCOUNT_LOCKED',
            {
                'identifier': identifier,
                'blocked_until': datetime.fromtimestamp(blocked_until).isoformat(),
                'duration_minutes': lockout_duration
            },
            'CRITICAL'
        )
    
    @staticmethod
    def is_blocked(email: str = None, ip: str = None) -> tuple[bool, Optional[int]]:
        """
        Check if identifier is blocked.
        Returns (is_blocked, seconds_remaining)
        """
        identifier = FailedLoginTracker.get_identifier(email, ip)
        
        if identifier in blocked_ips:
            blocked_until = blocked_ips[identifier]
            current_time = time.time()
            
            if current_time < blocked_until:
                seconds_remaining = int(blocked_until - current_time)
                return True, seconds_remaining
            else:
                # Unblock if time has passed
                del blocked_ips[identifier]
                failed_login_attempts[identifier] = []
        
        return False, None
    
    @staticmethod
    def reset_attempts(email: str = None, ip: str = None):
        """Reset failed attempts for an identifier"""
        identifier = FailedLoginTracker.get_identifier(email, ip)
        if identifier in failed_login_attempts:
            failed_login_attempts[identifier] = []
        
        SecurityMonitor.log_security_event(
            'LOGIN_SUCCESS',
            {'identifier': identifier},
            'INFO'
        )
    
    @staticmethod
    def get_attempt_count(email: str = None, ip: str = None) -> int:
        """Get number of failed attempts"""
        identifier = FailedLoginTracker.get_identifier(email, ip)
        current_time = time.time()
        
        # Clean old attempts
        if identifier in failed_login_attempts:
            failed_login_attempts[identifier] = [
                t for t in failed_login_attempts[identifier]
                if current_time - t < 3600
            ]
            return len(failed_login_attempts[identifier])
        
        return 0


class IPBlocker:
    """IP-based blocking for suspicious activity"""
    
    @staticmethod
    def block_ip(ip: str, duration_minutes: int = 60, reason: str = "Suspicious activity"):
        """Block an IP address"""
        blocked_until = time.time() + (duration_minutes * 60)
        blocked_ips[f"ip:{ip}"] = blocked_until
        
        SecurityMonitor.log_security_event(
            'IP_BLOCKED',
            {
                'ip': ip,
                'reason': reason,
                'duration_minutes': duration_minutes,
                'blocked_until': datetime.fromtimestamp(blocked_until).isoformat()
            },
            'CRITICAL'
        )
    
    @staticmethod
    def is_ip_blocked(ip: str = None) -> tuple[bool, Optional[int]]:
        """Check if IP is blocked"""
        if ip is None:
            ip = request.remote_addr
        
        identifier = f"ip:{ip}"
        
        if identifier in blocked_ips:
            blocked_until = blocked_ips[identifier]
            current_time = time.time()
            
            if current_time < blocked_until:
                seconds_remaining = int(blocked_until - current_time)
                return True, seconds_remaining
            else:
                del blocked_ips[identifier]
        
        return False, None
    
    @staticmethod
    def unblock_ip(ip: str):
        """Unblock an IP address"""
        identifier = f"ip:{ip}"
        if identifier in blocked_ips:
            del blocked_ips[identifier]
            
            SecurityMonitor.log_security_event(
                'IP_UNBLOCKED',
                {'ip': ip},
                'INFO'
            )


def get_request_fingerprint() -> str:
    """Generate a fingerprint for the current request"""
    components = [
        request.remote_addr,
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        request.headers.get('Accept-Encoding', '')
    ]
    
    fingerprint_string = '|'.join(components)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()


def detect_suspicious_patterns(data: dict) -> list:
    """Detect suspicious patterns in request data"""
    suspicious_patterns = []
    
    # SQL injection patterns
    sql_patterns = [
        "' OR '1'='1",
        "'; DROP TABLE",
        "UNION SELECT",
        "' OR 1=1--",
        "admin'--",
        "' OR 'a'='a"
    ]
    
    # XSS patterns
    xss_patterns = [
        "<script>",
        "javascript:",
        "onerror=",
        "onload=",
        "<iframe"
    ]
    
    for key, value in data.items():
        if isinstance(value, str):
            value_upper = value.upper()
            
            # Check SQL injection
            for pattern in sql_patterns:
                if pattern.upper() in value_upper:
                    suspicious_patterns.append({
                        'type': 'SQL_INJECTION',
                        'field': key,
                        'pattern': pattern
                    })
            
            # Check XSS
            for pattern in xss_patterns:
                if pattern.lower() in value.lower():
                    suspicious_patterns.append({
                        'type': 'XSS',
                        'field': key,
                        'pattern': pattern
                    })
    
    if suspicious_patterns:
        SecurityMonitor.log_security_event(
            'SUSPICIOUS_PATTERN_DETECTED',
            {
                'patterns': suspicious_patterns,
                'request_path': request.path
            },
            'CRITICAL'
        )
    
    return suspicious_patterns


def validate_file_upload_security(file, allowed_extensions: set, max_size_mb: int = 10) -> tuple[bool, Optional[str]]:
    """
    Validate file upload for security.
    Returns (is_valid, error_message)
    """
    if not file or file.filename == '':
        return False, "No file provided"
    
    # Check extension
    if '.' not in file.filename:
        return False, "File has no extension"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        SecurityMonitor.log_security_event(
            'INVALID_FILE_UPLOAD',
            {
                'filename': file.filename,
                'extension': ext,
                'allowed': list(allowed_extensions)
            },
            'WARNING'
        )
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check for double extensions (e.g., file.php.jpg)
    if file.filename.count('.') > 1:
        SecurityMonitor.log_security_event(
            'SUSPICIOUS_FILE_UPLOAD',
            {
                'filename': file.filename,
                'reason': 'Multiple extensions detected'
            },
            'WARNING'
        )
    
    # Check file size if available
    if hasattr(file, 'content_length') and file.content_length:
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.content_length > max_size_bytes:
            return False, f"File size exceeds maximum of {max_size_mb}MB"
    
    # Check for null bytes in filename (directory traversal attempt)
    if '\x00' in file.filename:
        SecurityMonitor.log_security_event(
            'FILE_UPLOAD_ATTACK',
            {
                'filename': file.filename,
                'attack_type': 'Null byte injection'
            },
            'CRITICAL'
        )
        return False, "Invalid filename"
    
    # Check for path traversal
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        SecurityMonitor.log_security_event(
            'FILE_UPLOAD_ATTACK',
            {
                'filename': file.filename,
                'attack_type': 'Path traversal attempt'
            },
            'CRITICAL'
        )
        return False, "Invalid filename"
    
    return True, None
