import os
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from routes.chat import chat_bp
from routes.knowledge import knowledge_bp
from routes.agent import agent_bp
from routes.voice import voice_bp
from middleware.error_handler import handle_error
from middleware.rate_limiter import limiter

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

CORS(app, supports_credentials=True)

limiter.init_app(app)

app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
app.register_blueprint(agent_bp, url_prefix='/api/agent')
app.register_blueprint(voice_bp, url_prefix='/api/voice')

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
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'Veron AI Backend is running',
        'timestamp': '2024-01-01T00:00:00.000Z'
    })

@app.errorhandler(400)
def bad_request(error):
    return handle_error(error, 400)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return handle_error(error, 500)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Veron AI Backend server is running on port {port}")
    print(f"📡 Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    print(f"🔐 Environment: {os.getenv('NODE_ENV', 'development')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 