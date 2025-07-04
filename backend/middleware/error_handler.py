import os
from flask import jsonify

def handle_error(error, status_code=500):
    is_development = os.getenv('NODE_ENV', 'development') == 'development'
    
    error_response = {
        'success': False,
        'error': str(error) if is_development else 'An error occurred'
    }
    
    if is_development:
        error_response['details'] = str(error)
    
    return jsonify(error_response), status_code

def handle_validation_error(errors):
    return jsonify({
        'success': False,
        'error': 'Validation failed',
        'details': errors
    }), 400 