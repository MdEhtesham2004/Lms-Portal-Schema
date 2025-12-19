import os
import logging
from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from config import Config
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta
from redis import Redis
from flask import request
import requests

load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
mail = Mail()


# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    # storage_uri="memory://",  # Will be updated in create_app
    # storage_uri=None,  # Will be updated in create_app
    storage_uri = Config.REDIS_URL,
    strategy="fixed-window",
    swallow_errors=True,  # Don't crash if Redis is down
    headers_enabled=True  # Show rate limit headers for debugging
)

# Talisman will be initialized in create_app
talisman = None

FRONTEND_URL_STUDENTS = os.environ.get("FRONTEND_URL_STUDENTS")
FRONTEND_URL_ADMIN = os.environ.get("FRONTEND_URL_ADMIN")
BASE_URL = "/api/v1/"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Example: 500 MB limit

    app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] =  os.environ.get("MAIL_PASSWORD")# APP Password only
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_DEFAULT_SENDER")
    
    # ============================================
    # SERVER-SIDE SESSION WITH REDIS
    # ============================================
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_KEY_PREFIX"] = "flask_session:"
    
    # Session cookie settings for CORS
    app.config["SESSION_COOKIE_NAME"] = "session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    
    # For ngrok or production (HTTPS)
    app.config["SESSION_COOKIE_SAMESITE"] = "None"  # Required for cross-origin
    app.config["SESSION_COOKIE_SECURE"] = True      # Required for HTTPS
    
    # Note: If testing locally without ngrok, set FLASK_ENV=development and use HTTP



    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    Session(app)
    
    # Initialize Flask-Limiter
    limiter.init_app(app)

    
    # Configure storage (Redis or memory)
    limiter._storage_uri = app.config['RATELIMIT_STORAGE_URL']
    # Temporarily disable rate limiting to confirm
    # limiter.enabled = False
    
    # Log configuration
    if app.config['RATELIMIT_ENABLED']:
        app.logger.info(f"✅ Rate limiting ENABLED with storage: {app.config['RATELIMIT_STORAGE_URL']}")
    else:
        app.logger.warning(f"⚠️  Rate limiting DISABLED (decorators will be ignored)")
        # Disable limiter if not enabled
        limiter.enabled = False
    
    
    # Initialize Talisman for security headers (only in production)
    # Initialize Talisman for security headers (only in production)
    if app.config['SECURITY_HEADERS_ENABLED']:
        global talisman
        talisman = Talisman(
            app,
            force_https=app.config['FORCE_HTTPS'],
            strict_transport_security=False,
            strict_transport_security_max_age=31536000,  # 1 year
            content_security_policy=app.config['CSP_POLICY'],
            content_security_policy_nonce_in=['script-src'],
            session_cookie_samesite='None',
            session_cookie_secure=True,
            referrer_policy='strict-origin-when-cross-origin',
            permissions_policy={  # Renamed from feature_policy as per newer Flask-Talisman/specs
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'"
            }
        )
        app.logger.info("Security headers enabled via Talisman")
    
       # Initialize security middleware
    from utils.middleware import init_middleware
    init_middleware(app)
    
    # Configure CORS
    # NOTE: CORS is now handled by middleware (utils/middleware.py -> handle_cors_headers)
    # This ensures proper handling of credentialed requests with specific origins
    # instead of wildcards which are not allowed with credentials: 'include'
    
    # CORS(app,
    #     supports_credentials=True,
    #     origins=[
    #         "http://localhost:5173",
    #         "http://localhost:5174",
    #         "http://127.0.0.1:3000",
    #         "https://aim-admin-portal.vercel.app",  # Production frontend
    #         FRONTEND_URL_STUDENTS,
    #         FRONTEND_URL_ADMIN,
    #         "https://aim-international.vercel.app"
    #     ],
    #     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    #     allow_headers=["Content-Type", "Authorization"]
    # )

    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.course_routes import course_bp
    from routes.admin_routes import admin_bp
    from routes.payment_routes import payment_bp
    from routes.file_routes import file_bp
    from routes.notification_routes import notification_bp
    from routes.certificate_routes import certificate_bp
    from routes.live_session_routes import live_session_bp
    from routes.helper_routes import helper_bp
    from routes.prerequisites import prereq_bp

    from routes.master_routes import master_bp
    from routes.subcategory_routes import subcategory_bp
    from routes.modules_routes import modules_bp
    from routes.lessons_routes import lessons_bp
    from routes.lessons_resources_routes import lessons_resource_bp
    from routes.enrollments_routes import enrollments_bp
    from routes.public_routes import public_bp
    from routes.contact_routes import contact_bp




    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')

    app.register_blueprint(master_bp, url_prefix='/api/v1/mastercategories')
    app.register_blueprint(subcategory_bp, url_prefix='/api/v1/subcategories')
    app.register_blueprint(course_bp, url_prefix='/api/v1/courses')
    app.register_blueprint(modules_bp, url_prefix='/api/v1/modules')
    app.register_blueprint(lessons_bp, url_prefix='/api/v1/lessons')
    app.register_blueprint(lessons_resource_bp, url_prefix='/api/v1/lesson-resources')
    app.register_blueprint(public_bp, url_prefix="/api/v1/public")
    app.register_blueprint(prereq_bp,url_prefix="/api/v1/prerequisites")
    
    
    app.register_blueprint(enrollments_bp, url_prefix='/api/v1/enrollments')
    
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(payment_bp, url_prefix='/api/v1/payments')
    app.register_blueprint(file_bp, url_prefix='/api/v1/files')
    app.register_blueprint(notification_bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(certificate_bp, url_prefix='/api/v1/certificates')
    app.register_blueprint(live_session_bp, url_prefix='/api/v1/live-sessions')
    app.register_blueprint(helper_bp,url_prefix='/api/v1/helper/')
    
    app.register_blueprint(contact_bp, url_prefix='/api/v1/contact')
    
    # Create tables
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
    
    # JWT token blacklist handling
    from models import TokenBlacklist
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        token_jti = jwt_payload['jti']
        token = TokenBlacklist.query.filter_by(jti=token_jti).first()
        return token is not None
        
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            "error": "Rate limit exceeded",
            "message": str(e.description),
            "retry_after": int(e.description.split("per")[1].strip().split(" ")[0]) if "per" in str(e.description) else 60
        }, 429
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'message': 'Aim Technologies API',
            'version': '1.0',
            'status': 'running',
            'endpoints': {
                'api': '/api/v1/',
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'courses': '/api/v1/courses',
                'admin': '/api/v1/admin',
                'payments': '/api/v1/payments',
                'files': '/api/v1/files',
                'notifications': '/api/v1/notifications',
                'certificates': '/api/v1/certificates',
                'live-sessions': '/api/v1/live-sessions'
            }
        }
    
    # API root endpoint
    @app.route('/api/v1/')
    def api_root():
        return {
            'message': 'Aim Technologies API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'courses': '/api/v1/courses',
                'admin': '/api/v1/admin',
                'payments': '/api/v1/payments',
                'files': '/api/v1/files',
                'notifications': '/api/v1/notifications',
                'certificates': '/api/v1/certificates',
                'live-sessions': '/api/v1/live-sessions'
            }
        }
    
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    PLACE_ID = os.environ.get("PLACE_ID")
    WEBSITE_URL = "https://aim-international.vercel.app/"  # change if needed

    @app.route("/api/google-reviews", methods=["POST"])
    def google_reviews():
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": PLACE_ID,
            "fields": "name,rating",
            "key": GOOGLE_API_KEY
        }

        response = requests.get(
            url,
            params=params,
            headers={
                "Referer": WEBSITE_URL
            },
            timeout=10
        )

        data = response.json()

        # reviews = data.get("result", {}).get("reviews", [])
        # return jsonify(reviews)
        return jsonify(data)

    # Route to serve files from the absolute path (Render Disk)
    from flask import send_from_directory
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        # Use simple string replacement to handle potential double-slashes or mismatches
        # between URL and config, but primarily trust UPLOAD_FOLDER
        upload_folder = app.config.get('UPLOAD_FOLDER', '/static/uploads')
        print(f"DEBUG: Serving URL {filename} from {upload_folder}") # Add debug logging here too
        return send_from_directory(upload_folder, filename)

    # Print all rules to confirm route registration
    print("DEBUG: Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint}")

    return app

