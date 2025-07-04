import os
import ssl
from flask import Flask, jsonify, send_from_directory, send_file, request
from flask_cors import CORS
from flask_talisman import Talisman
from dotenv import load_dotenv
from routes.chat import chat_bp
from routes.knowledge import knowledge_bp
from routes.agent import agent_bp
from routes.voice import voice_bp
from routes.security import security_bp
from middleware.error_handler import handle_error
from middleware.rate_limiter import limiter
from middleware.security_middleware import SecurityMiddleware
import logging
from logging.handlers import RotatingFileHandler
import secrets

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

# Security Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['FORCE_HTTPS'] = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
app.config['SECURE_COOKIES'] = os.getenv('SECURE_COOKIES', 'false').lower() == 'true'

# Enhanced CORS configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
cors_credentials = os.getenv('CORS_CREDENTIALS', 'true').lower() == 'true'

CORS(app, 
     origins=allowed_origins,
     supports_credentials=cors_credentials,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])

# Security Headers with Talisman
csp_policy = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "blob:"],
    'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
    'font-src': ["'self'", "fonts.gstatic.com"],
    'img-src': ["'self'", "data:", "blob:"],
    'media-src': ["'self'", "blob:"],
    'connect-src': ["'self'", "wss:", "https:"],
    'worker-src': ["'self'", "blob:"],
    'frame-ancestors': ["'none'"],
    'form-action': ["'self'"],
    'base-uri': ["'self'"],
    'object-src': ["'none'"]
}

if os.getenv('CSP_ENABLED', 'true').lower() == 'true':
    Talisman(app, 
             force_https=app.config['FORCE_HTTPS'],
             strict_transport_security=True,
             content_security_policy=csp_policy,
             referrer_policy='strict-origin-when-cross-origin',
             feature_policy={
                 'microphone': ['self'],
                 'camera': ['none'],
                 'geolocation': ['none'],
                 'payment': ['none']
             })

# Initialize security middleware
security_middleware = SecurityMiddleware()
app.before_request(security_middleware.before_request)
app.after_request(security_middleware.after_request)

# Enhanced rate limiting
limiter.init_app(app)

# Security logging
if os.getenv('SECURITY_LOGGING', 'false').lower() == 'true':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler(
        'logs/security.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
app.register_blueprint(agent_bp, url_prefix='/api/agent')
app.register_blueprint(voice_bp, url_prefix='/api/voice')
app.register_blueprint(security_bp, url_prefix='/api/security')

@app.route('/')
def serve_react_app():
    return send_file('../frontend/build/index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API route not found'}), 404
    
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_file('../frontend/build/index.html')

@app.route('/api/health')
@limiter.limit("10 per minute")
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'English Agent Backend is running securely',
        'timestamp': '2024-01-01T00:00:00.000Z',
        'security': {
            'https_enabled': app.config['FORCE_HTTPS'],
            'csp_enabled': os.getenv('CSP_ENABLED', 'true').lower() == 'true',
            'rate_limiting': True
        }
    })

@app.route('/api/security/info')
@limiter.limit("5 per minute")
def security_info():
    return jsonify({
        'security_features': {
            'https_enforced': app.config['FORCE_HTTPS'],
            'secure_cookies': app.config['SECURE_COOKIES'],
            'csp_enabled': os.getenv('CSP_ENABLED', 'true').lower() == 'true',
            'rate_limiting': True,
            'cors_configured': True,
            'security_headers': True
        },
        'allowed_origins': allowed_origins,
        'rate_limits': {
            'general': os.getenv('RATE_LIMIT_MAX_REQUESTS', '100'),
            'window': os.getenv('RATE_LIMIT_WINDOW_MS', '900000')
        }
    })

# Error handlers with security logging
@app.errorhandler(400)
def bad_request(error):
    app.logger.warning(f'Bad request from {request.remote_addr}: {error}')
    return handle_error(error, 400)

@app.errorhandler(404)
def not_found(error):
    app.logger.info(f'404 error from {request.remote_addr}: {request.url}')
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    app.logger.warning(f'Rate limit exceeded from {request.remote_addr}')
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Internal error from {request.remote_addr}: {error}')
    return handle_error(error, 500)

def create_ssl_context():
    """Create SSL context for HTTPS"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    
    # Development certificates
    cert_path = os.getenv('SSL_CERT_PATH', 'certs/dev/cert.pem')
    key_path = os.getenv('SSL_KEY_PATH', 'certs/dev/key.pem')
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context.load_cert_chain(cert_path, key_path)
        return context
    
    return None

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    use_https = os.getenv('USE_HTTPS', 'false').lower() == 'true'
    
    print(f"🔒 English Agent Secure Backend starting...")
    print(f"🚀 Server running on port {port}")
    print(f"📡 Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    print(f"🔐 Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"🛡️ HTTPS: {'Enabled' if use_https else 'Disabled'}")
    print(f"🔥 Rate Limiting: Enabled")
    print(f"📜 CSP: {'Enabled' if os.getenv('CSP_ENABLED', 'true').lower() == 'true' else 'Disabled'}")
    
    if use_https:
        ssl_context = create_ssl_context()
        if ssl_context:
            print(f"🔐 HTTPS certificates loaded successfully")
            app.run(host='0.0.0.0', port=port, debug=debug, ssl_context=ssl_context)
        else:
            print(f"❌ HTTPS certificates not found. Run security-setup.sh first!")
            print(f"🔄 Falling back to HTTP...")
            app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host='0.0.0.0', port=port, debug=debug) 