from flask import Blueprint, request, jsonify, current_app
from middleware.rate_limiter import limiter
from middleware.security_middleware import require_https, validate_api_key
import os
import json
from datetime import datetime, timedelta

security_bp = Blueprint('security', __name__)

@security_bp.route('/csp-report', methods=['POST'])
@limiter.limit("10 per minute")
def csp_report():
    """Handle Content Security Policy violation reports"""
    try:
        report_data = request.get_json()
        
        if report_data and 'csp-report' in report_data:
            csp_report = report_data['csp-report']
            
            # Log CSP violation
            current_app.logger.warning(f"CSP Violation: {json.dumps(csp_report)}")
            
            # Store in security log if enabled
            if os.getenv('SECURITY_LOGGING', 'false').lower() == 'true':
                log_security_event('csp_violation', {
                    'blocked_uri': csp_report.get('blocked-uri', ''),
                    'document_uri': csp_report.get('document-uri', ''),
                    'violated_directive': csp_report.get('violated-directive', ''),
                    'source_file': csp_report.get('source-file', ''),
                    'line_number': csp_report.get('line-number', ''),
                    'column_number': csp_report.get('column-number', ''),
                    'user_agent': request.headers.get('User-Agent', ''),
                    'ip_address': request.remote_addr,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return '', 204  # No content response for CSP reports
        
    except Exception as e:
        current_app.logger.error(f"Error processing CSP report: {str(e)}")
        return '', 400

@security_bp.route('/audit-log', methods=['GET'])
@require_https
@validate_api_key
@limiter.limit("5 per minute")
def get_audit_log():
    """Get security audit log (requires API key)"""
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        # Read security log file
        log_file = 'logs/security.log'
        if not os.path.exists(log_file):
            return jsonify({'events': [], 'total': 0})
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Parse and filter log entries
        events = []
        for line in reversed(lines[offset:offset + limit]):
            if line.strip():
                events.append({
                    'timestamp': line.split()[0] + ' ' + line.split()[1],
                    'level': line.split()[2].rstrip(':'),
                    'message': ' '.join(line.split()[3:]).strip()
                })
        
        return jsonify({
            'events': events,
            'total': len(lines),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Error reading audit log: {str(e)}")
        return jsonify({'error': 'Failed to read audit log'}), 500

@security_bp.route('/blocked-ips', methods=['GET'])
@require_https
@validate_api_key
@limiter.limit("5 per minute")
def get_blocked_ips():
    """Get list of currently blocked IPs"""
    try:
        # This would need to be implemented with proper persistence
        # For now, return empty list
        return jsonify({
            'blocked_ips': [],
            'message': 'IP blocking is handled by security middleware'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting blocked IPs: {str(e)}")
        return jsonify({'error': 'Failed to get blocked IPs'}), 500

@security_bp.route('/security-headers', methods=['GET'])
@limiter.limit("10 per minute")
def check_security_headers():
    """Check which security headers are enabled"""
    headers_status = {
        'csp_enabled': os.getenv('CSP_ENABLED', 'true').lower() == 'true',
        'secure_headers': os.getenv('SECURE_HEADERS', 'true').lower() == 'true',
        'force_https': os.getenv('FORCE_HTTPS', 'false').lower() == 'true',
        'secure_cookies': os.getenv('SECURE_COOKIES', 'false').lower() == 'true',
        'security_logging': os.getenv('SECURITY_LOGGING', 'false').lower() == 'true'
    }
    
    return jsonify({
        'security_headers': headers_status,
        'recommendations': get_security_recommendations(headers_status)
    })

@security_bp.route('/health', methods=['GET'])
@limiter.limit("20 per minute")
def security_health():
    """Security health check endpoint"""
    health_status = {
        'status': 'healthy',
        'security_features': {
            'https_available': request.is_secure,
            'rate_limiting': True,
            'security_headers': os.getenv('SECURE_HEADERS', 'true').lower() == 'true',
            'csp_enabled': os.getenv('CSP_ENABLED', 'true').lower() == 'true',
            'security_logging': os.getenv('SECURITY_LOGGING', 'false').lower() == 'true',
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(health_status)

@security_bp.route('/vulnerability-scan', methods=['POST'])
@require_https
@validate_api_key
@limiter.limit("1 per hour")
def basic_vulnerability_scan():
    """Basic security vulnerability check"""
    try:
        vulnerabilities = []
        
        # Check for weak configurations
        if os.getenv('SECRET_KEY') == 'dev-secret-key':
            vulnerabilities.append({
                'type': 'weak_secret_key',
                'severity': 'high',
                'description': 'Using default development secret key in production'
            })
        
        if os.getenv('DEBUG', 'false').lower() == 'true':
            vulnerabilities.append({
                'type': 'debug_enabled',
                'severity': 'high',
                'description': 'Debug mode is enabled'
            })
        
        if not os.getenv('FORCE_HTTPS', 'false').lower() == 'true':
            vulnerabilities.append({
                'type': 'http_allowed',
                'severity': 'medium',
                'description': 'HTTPS is not enforced'
            })
        
        if not os.getenv('RATE_LIMIT_MAX_REQUESTS'):
            vulnerabilities.append({
                'type': 'no_rate_limiting',
                'severity': 'medium',
                'description': 'Rate limiting not configured'
            })
        
        return jsonify({
            'scan_timestamp': datetime.utcnow().isoformat(),
            'vulnerabilities_found': len(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'status': 'secure' if len(vulnerabilities) == 0 else 'vulnerable'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error during vulnerability scan: {str(e)}")
        return jsonify({'error': 'Vulnerability scan failed'}), 500

def log_security_event(event_type, event_data):
    """Log security events to file"""
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        with open('logs/security_events.json', 'a') as f:
            event = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': event_data
            }
            f.write(json.dumps(event) + '\n')
            
    except Exception as e:
        current_app.logger.error(f"Error logging security event: {str(e)}")

def get_security_recommendations(headers_status):
    """Get security recommendations based on current configuration"""
    recommendations = []
    
    if not headers_status['force_https']:
        recommendations.append({
            'type': 'https',
            'message': 'Enable HTTPS enforcement by setting FORCE_HTTPS=true'
        })
    
    if not headers_status['secure_cookies']:
        recommendations.append({
            'type': 'cookies',
            'message': 'Enable secure cookies by setting SECURE_COOKIES=true'
        })
    
    if not headers_status['security_logging']:
        recommendations.append({
            'type': 'logging',
            'message': 'Enable security logging by setting SECURITY_LOGGING=true'
        })
    
    if not headers_status['csp_enabled']:
        recommendations.append({
            'type': 'csp',
            'message': 'Enable Content Security Policy by setting CSP_ENABLED=true'
        })
    
    return recommendations 