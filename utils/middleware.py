"""
Security middleware for Flask application.
Handles request ID tracking, security headers, and request logging.
"""
import os
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


def handle_cors_headers(response):
    """Ensure CORS headers are properly set for credentialed requests"""
    # Get the origin from the request
    origin = request.headers.get('Origin')
    
    # If no Origin header, it's likely a same-origin request or direct API call
    # No CORS headers needed
    if not origin:
        return response
    
    # List of allowed origins (should match app.py CORS config)
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "https://aim-admin-portal.vercel.app",
        "https://aim-international.vercel.app",
        os.environ.get("FRONTEND_URL_STUDENTS"),
        os.environ.get("FRONTEND_URL_ADMIN")
    ]
    
    # Filter out None values from environment variables
    allowed_origins = [o for o in allowed_origins if o]
    
    # If the origin is in our allowed list, set it explicitly
    # (cannot use wildcard '*' when credentials are included)
    if origin in allowed_origins:
        # FORCE set these headers (override any proxy/ngrok headers)
        # Remove any existing Access-Control-Allow-Origin first
        if 'Access-Control-Allow-Origin' in response.headers:
            del response.headers['Access-Control-Allow-Origin']
        
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Debug: Log CORS headers being set
        print(f"🔧 CORS Headers Set for {request.method} {request.path}")
        print(f"   Origin: {origin}")
        print(f"   CORS Header Value: {response.headers.get('Access-Control-Allow-Origin')}")
    else:
        print(f"⚠️  Origin NOT in allowed list: {origin}")
        print(f"   Allowed origins: {allowed_origins}")
    
    return response


def init_middleware(app):
    """Initialize all middleware"""
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        add_request_id()
        log_request()
        
        # Handle CORS preflight OPTIONS requests
        if request.method == 'OPTIONS':
            print("=" * 70)
            print("OPTIONS PREFLIGHT REQUEST RECEIVED")
            print("=" * 70)
            
            origin = request.headers.get('Origin')
            print(f"Origin: {origin}")
            print(f"Path: {request.path}")
            
            allowed_origins = [
                "http://localhost:5173",
                "http://localhost:5174",
                "http://127.0.0.1:3000",
                "https://aim-admin-portal.vercel.app",
                "https://aim-international.vercel.app",
                os.environ.get("FRONTEND_URL_STUDENTS"),
                os.environ.get("FRONTEND_URL_ADMIN")
            ]
            
            allowed_origins = [o for o in allowed_origins if o]
            
            if origin in allowed_origins:
                from flask import make_response
                response = make_response('', 200)
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight for 1 hour
                
                print(f"✅ OPTIONS Response Headers:")
                print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
                print(f"   Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials')}")
                print("=" * 70)
                
                return response
            else:
                print(f"❌ Origin NOT allowed: {origin}")
                print(f"   Allowed origins: {allowed_origins}")
                print("=" * 70)
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        response = log_response(response)
        response = add_security_headers(response)
        response = handle_cors_headers(response)
        return response
