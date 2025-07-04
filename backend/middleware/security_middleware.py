import os
import time
from flask import request, jsonify, current_app
from functools import wraps
import re
import hashlib
from collections import defaultdict, deque

class SecurityMiddleware:
    def __init__(self):
        self.request_counts = defaultdict(lambda: deque())
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'SELECT.*FROM',
            r'UNION.*SELECT',
            r'DROP.*TABLE',
            r'INSERT.*INTO',
            r'UPDATE.*SET',
            r'DELETE.*FROM',
            r'\.\./',
            r'etc/passwd',
            r'proc/self',
            r'cmd\.exe',
            r'powershell',
            r'bash',
            r'eval\(',
            r'exec\(',
            r'system\(',
        ]
        self.max_requests_per_ip = int(os.getenv('MAX_REQUESTS_PER_IP', '100'))
        self.time_window = int(os.getenv('TIME_WINDOW_SECONDS', '3600'))
        
    def is_suspicious_request(self, data):
        """Check if request contains suspicious patterns"""
        if not data:
            return False
            
        data_str = str(data).lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        return False
    
    def track_ip_requests(self, ip):
        """Track requests per IP and detect abuse"""
        current_time = time.time()
        
        # Clean old entries
        while (self.request_counts[ip] and 
               current_time - self.request_counts[ip][0] > self.time_window):
            self.request_counts[ip].popleft()
        
        # Add current request
        self.request_counts[ip].append(current_time)
        
        # Check if IP should be blocked
        if len(self.request_counts[ip]) > self.max_requests_per_ip:
            self.blocked_ips.add(ip)
            return False
        
        return True
    
    def validate_file_upload(self, file):
        """Validate uploaded files for security"""
        if not file:
            return True, None
            
        allowed_types = os.getenv('ALLOWED_FILE_TYPES', 'pdf,doc,docx,txt,png,jpg,jpeg').split(',')
        max_size = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))
        
        # Check file extension
        if '.' not in file.filename:
            return False, "File must have an extension"
            
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_types:
            return False, f"File type .{ext} not allowed"
        
        # Check file size (this is a basic check, actual size is checked by Flask)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset position
        
        if size > max_size:
            return False, f"File too large. Maximum size: {max_size} bytes"
        
        # Check for suspicious file content (basic check)
        file.seek(0)
        chunk = file.read(1024)
        file.seek(0)
        
        if self.is_suspicious_request(chunk):
            return False, "File contains suspicious content"
        
        return True, None
    
    def generate_csp_nonce(self):
        """Generate nonce for Content Security Policy"""
        return hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    
    def before_request(self):
        """Process request before handling"""
        client_ip = self.get_client_ip()
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            current_app.logger.warning(f"Blocked request from {client_ip}")
            return jsonify({
                'error': 'Access denied. Too many requests.',
                'code': 'IP_BLOCKED'
            }), 429
        
        # Track IP requests
        if not self.track_ip_requests(client_ip):
            current_app.logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'code': 'RATE_LIMIT'
            }), 429
        
        # Validate request data for suspicious content
        if request.is_json:
            try:
                data = request.get_json()
                if self.is_suspicious_request(data):
                    current_app.logger.warning(f"Suspicious request from {client_ip}: {request.url}")
                    return jsonify({
                        'error': 'Request contains suspicious content',
                        'code': 'SUSPICIOUS_CONTENT'
                    }), 400
            except:
                pass
        
        # Validate form data
        if request.form:
            for key, value in request.form.items():
                if self.is_suspicious_request(value):
                    current_app.logger.warning(f"Suspicious form data from {client_ip}")
                    return jsonify({
                        'error': 'Form contains suspicious content',
                        'code': 'SUSPICIOUS_CONTENT'
                    }), 400
        
        # Validate file uploads
        if request.files:
            for key, file in request.files.items():
                is_valid, error_msg = self.validate_file_upload(file)
                if not is_valid:
                    current_app.logger.warning(f"Invalid file upload from {client_ip}: {error_msg}")
                    return jsonify({
                        'error': error_msg,
                        'code': 'INVALID_FILE'
                    }), 400
        
        # Log security-relevant requests
        if os.getenv('SECURITY_LOGGING', 'false').lower() == 'true':
            if any(pattern in request.url.lower() for pattern in ['/admin', '/api', '/upload']):
                current_app.logger.info(f"Security request: {client_ip} -> {request.method} {request.url}")
    
    def after_request(self, response):
        """Process response after handling"""
        # Add security headers
        if os.getenv('SECURE_HEADERS', 'true').lower() == 'true':
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = (
                'microphone=(self), camera=(), geolocation=(), '
                'payment=(), usb=(), magnetometer=(), gyroscope=()'
            )
            
            # HSTS (if HTTPS is enabled)
            if request.is_secure or os.getenv('FORCE_HTTPS', 'false').lower() == 'true':
                response.headers['Strict-Transport-Security'] = (
                    'max-age=31536000; includeSubDomains; preload'
                )
            
            # Secure cookies
            if os.getenv('SECURE_COOKIES', 'false').lower() == 'true':
                response.headers['Set-Cookie'] = response.headers.get('Set-Cookie', '') + '; Secure; SameSite=Strict'
        
        return response
    
    def get_client_ip(self):
        """Get real client IP, considering proxies"""
        # Check for forwarded headers (be careful with these in production)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr

def require_https(f):
    """Decorator to require HTTPS for specific routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and os.getenv('FORCE_HTTPS', 'false').lower() == 'true':
            return jsonify({
                'error': 'HTTPS required',
                'code': 'HTTPS_REQUIRED'
            }), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(f):
    """Decorator to validate API key for sensitive endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = os.getenv('API_KEY')
        
        if expected_key and api_key != expected_key:
            current_app.logger.warning(f"Invalid API key from {request.remote_addr}")
            return jsonify({
                'error': 'Invalid API key',
                'code': 'INVALID_API_KEY'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function 