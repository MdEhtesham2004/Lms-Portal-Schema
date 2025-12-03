"""
Security middleware for Flask application.
Handles request ID tracking, security headers, and request logging.
"""
import uuid
import logging
from flask import request, g
from datetime import datetime

logger = logging.getLogger(__name__)


def add_request_id():
    """Add unique request ID to each request"""
    g.request_id = str(uuid.uuid4())
    g.request_start_time = datetime.utcnow()


def log_request():
    """Log incoming requests with security context"""
    if request.endpoint:
        logger.info(
            f"Request: {request.method} {request.path} | "
            f"IP: {request.remote_addr} | "
            f"User-Agent: {request.headers.get('User-Agent', 'N/A')} | "
            f"Request-ID: {getattr(g, 'request_id', 'N/A')}"
        )


def log_response(response):
    """Log response with timing information"""
    if hasattr(g, 'request_start_time'):
        duration = (datetime.utcnow() - g.request_start_time).total_seconds()
        logger.info(
            f"Response: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"Request-ID: {getattr(g, 'request_id', 'N/A')}"
        )
    
    # Add request ID to response headers
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    
    return response


def add_security_headers(response):
    """Add security headers to response"""
    # Only add if not already set by Talisman
    if 'X-Content-Type-Options' not in response.headers:
        response.headers['X-Content-Type-Options'] = 'nosniff'
    
    if 'X-Frame-Options' not in response.headers:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    if 'X-XSS-Protection' not in response.headers:
        response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy
    if 'Referrer-Policy' not in response.headers:
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy (formerly Feature Policy)
    if 'Permissions-Policy' not in response.headers:
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


def init_middleware(app):
    """Initialize all middleware"""
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        add_request_id()
        log_request()
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        response = log_response(response)
        response = add_security_headers(response)
        return response
