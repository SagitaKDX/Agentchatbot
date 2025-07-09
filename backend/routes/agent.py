import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from services.bedrock_agent_service import get_bedrock_agent_service
from services.file_processor import file_processor
from middleware.error_handler import handle_error, handle_validation_error

agent_bp = Blueprint('agent', __name__)

class AgentMessageSchema(Schema):
    message = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 5000)
    session_id = fields.Str(missing=None)

class SessionSchema(Schema):
    session_id = fields.Str(required=True)

@agent_bp.route('/chat', methods=['POST'])
def agent_chat():
    try:
        schema = AgentMessageSchema()
        data = schema.load(request.json)
        
        message = data['message']
        session_id = data.get('session_id')

        # Get relevant context from uploaded files
        file_context = file_processor.get_context_for_agent(message)
        
        # Enhance the message with file context if available
        enhanced_message = message
        if file_context:
            enhanced_message = f"""Context from uploaded files:
{file_context}

User Question: {message}

Please answer the user's question using the context from the uploaded files when relevant."""

        response = get_bedrock_agent_service().invoke_agent(enhanced_message, session_id)

        return jsonify({
            'success': True,
            'data': {
                'message': response['response'],
                'session_id': response['session_id'],
                'timestamp': response['timestamp'],
                'trace_info': response.get('trace_info', []),
                'used_file_context': bool(file_context),
                'context_files_count': len(file_processor.get_all_processed_files())
            }
        })

    except ValidationError as e:
        return handle_validation_error(e.messages)
    except Exception as e:
        print(f"Agent chat error: {e}")
        return handle_error('Failed to get response from agent. Please try again.', 500)

@agent_bp.route('/session/new', methods=['POST'])
def create_session():
    try:
        session_id = get_bedrock_agent_service().create_new_session()
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'message': 'New session created successfully'
            }
        })

    except Exception as e:
        print(f"Session creation error: {e}")
        return handle_error('Failed to create new session. Please try again.', 500)

@agent_bp.route('/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    try:
        session_info = get_bedrock_agent_service().get_session_info(session_id)
        
        if session_info is None:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'session_info': {
                    'last_used': session_info['last_used'].isoformat(),
                    'message_count': session_info['message_count'],
                    'created_at': session_info.get('created_at', '').isoformat() if session_info.get('created_at') else None
                }
            }
        })

    except Exception as e:
        print(f"Session info error: {e}")
        return handle_error('Failed to get session information. Please try again.', 500)

@agent_bp.route('/sessions', methods=['GET'])
def list_active_sessions():
    try:
        active_sessions = get_bedrock_agent_service().list_active_sessions()
        
        formatted_sessions = {}
        for session_id, session_data in active_sessions.items():
            formatted_sessions[session_id] = {
                'last_used': session_data['last_used'].isoformat(),
                'message_count': session_data['message_count'],
                'created_at': session_data.get('created_at', '').isoformat() if session_data.get('created_at') else None
            }
        
        return jsonify({
            'success': True,
            'data': {
                'active_sessions': formatted_sessions,
                'count': len(formatted_sessions)
            }
        })

    except Exception as e:
        print(f"List sessions error: {e}")
        return handle_error('Failed to list active sessions. Please try again.', 500)

@agent_bp.route('/sessions/cleanup', methods=['POST'])
def cleanup_sessions():
    try:
        cleaned_count = get_bedrock_agent_service().cleanup_old_sessions()
        
        return jsonify({
            'success': True,
            'data': {
                'cleaned_sessions': cleaned_count,
                'message': f'Cleaned up {cleaned_count} old sessions'
            }
        })

    except Exception as e:
        print(f"Session cleanup error: {e}")
        return handle_error('Failed to cleanup sessions. Please try again.', 500)

@agent_bp.route('/health', methods=['GET'])
def agent_health():
    try:
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'bedrock-agent',
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Agent health check error: {e}")
        return handle_error('Agent service health check failed', 500)

@agent_bp.route('/system-prompt', methods=['GET'])
def get_system_prompt():
    try:
        current_prompt = get_bedrock_agent_service().get_system_prompt()
        return jsonify({
            'success': True,
            'data': {
                'system_prompt': current_prompt,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Get system prompt error: {e}")
        return handle_error('Failed to get system prompt', 500)

@agent_bp.route('/system-prompt', methods=['PUT'])
def update_system_prompt():
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return handle_error('System prompt is required', 400)
        
        new_prompt = data['prompt']
        if not isinstance(new_prompt, str) or not new_prompt.strip():
            return handle_error('System prompt must be a non-empty string', 400)
        
        get_bedrock_agent_service().update_system_prompt(new_prompt)
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'System prompt updated successfully',
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Update system prompt error: {e}")
        return handle_error('Failed to update system prompt', 500)

@agent_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return handle_error('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return handle_error('No file selected', 400)
        
        # Check file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'md'}
        if '.' not in file.filename:
            return handle_error('File must have an extension', 400)
            
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in allowed_extensions:
            return handle_error('File type not supported. Please upload PDF, DOC, DOCX, TXT, or MD files.', 400)
        
        # Check file size (10MB limit)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return handle_error('File too large. Maximum size is 10MB.', 400)
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Process the file to extract text and create index
        processed_file = file_processor.process_file(unique_filename, filename)
        
        response_data = {
            'filename': filename,
            'filepath': unique_filename,
            'size': file_size,
            'uploaded_at': datetime.now().isoformat(),
            'message': 'File uploaded and processed successfully'
        }
        
        # Add processing results if successful
        if 'error' not in processed_file:
            response_data.update({
                'file_id': processed_file['id'],
                'text_extracted': processed_file['text_length'] > 0,
                'word_count': processed_file['word_count'],
                'keywords': processed_file['keywords'][:5],  # First 5 keywords
                'summary_preview': processed_file['summary'][:200] + "..." if len(processed_file['summary']) > 200 else processed_file['summary']
            })
        else:
            response_data['processing_error'] = processed_file['error']
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        print(f"File upload error: {e}")
        return handle_error('Failed to upload file. Please try again.', 500)

@agent_bp.route('/files', methods=['GET'])
def list_files():
    try:
        files = file_processor.get_all_processed_files()
        
        # Clean up file data for response (remove full text)
        cleaned_files = []
        for file_data in files:
            if 'error' not in file_data:
                cleaned_file = {
                    'id': file_data['id'],
                    'original_filename': file_data['original_filename'],
                    'file_size': file_data['file_size'],
                    'file_type': file_data['file_type'],
                    'processed_at': file_data['processed_at'],
                    'word_count': file_data['word_count'],
                    'text_length': file_data['text_length'],
                    'keywords': file_data['keywords'][:10],  # First 10 keywords
                    'summary': file_data['summary'][:300] + "..." if len(file_data['summary']) > 300 else file_data['summary']
                }
                cleaned_files.append(cleaned_file)
        
        return jsonify({
            'success': True,
            'data': {
                'files': cleaned_files,
                'total_files': len(cleaned_files),
                'total_size': sum(f['file_size'] for f in cleaned_files),
                'total_words': sum(f['word_count'] for f in cleaned_files)
            }
        })
        
    except Exception as e:
        print(f"List files error: {e}")
        return handle_error('Failed to list files. Please try again.', 500)

@agent_bp.route('/files/<file_id>', methods=['GET'])
def get_file_details(file_id):
    try:
        file_data = file_processor.get_file_by_id(file_id)
        
        if not file_data:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        if 'error' in file_data:
            return jsonify({
                'success': False,
                'error': f"File processing error: {file_data['error']}"
            }), 400
        
        # Return full file data including extracted text
        return jsonify({
            'success': True,
            'data': {
                'file': file_data
            }
        })
        
    except Exception as e:
        print(f"Get file details error: {e}")
        return handle_error('Failed to get file details. Please try again.', 500)

@agent_bp.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        success = file_processor.delete_file(file_id)
        
        if success:
            return jsonify({
                'success': True,
                'data': {
                    'message': 'File deleted successfully',
                    'file_id': file_id
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'File not found or could not be deleted'
            }), 404
        
    except Exception as e:
        print(f"Delete file error: {e}")
        return handle_error('Failed to delete file. Please try again.', 500)

@agent_bp.route('/files/search', methods=['POST'])
def search_files():
    try:
        data = request.json
        if not data or 'keywords' not in data:
            return handle_error('Keywords are required for search', 400)
        
        keywords = data['keywords']
        if not isinstance(keywords, list) or not keywords:
            return handle_error('Keywords must be a non-empty list', 400)
        
        matching_files = file_processor.get_files_by_keywords(keywords)
        
        # Clean up file data for response
        cleaned_files = []
        for file_data in matching_files:
            if 'error' not in file_data:
                cleaned_file = {
                    'id': file_data['id'],
                    'original_filename': file_data['original_filename'],
                    'file_size': file_data['file_size'],
                    'file_type': file_data['file_type'],
                    'processed_at': file_data['processed_at'],
                    'word_count': file_data['word_count'],
                    'keywords': file_data['keywords'],
                    'summary': file_data['summary'],
                    'relevance_score': sum(1 for keyword in keywords if keyword.lower() in file_data['extracted_text'].lower())
                }
                cleaned_files.append(cleaned_file)
        
        # Sort by relevance score
        cleaned_files.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'files': cleaned_files,
                'search_keywords': keywords,
                'results_count': len(cleaned_files)
            }
        })
        
    except Exception as e:
        print(f"Search files error: {e}")
        return handle_error('Failed to search files. Please try again.', 500)

@agent_bp.route('/files/stats', methods=['GET'])
def get_file_stats():
    try:
        files = file_processor.get_all_processed_files()
        
        # Calculate statistics
        total_files = len(files)
        successful_files = len([f for f in files if 'error' not in f])
        failed_files = total_files - successful_files
        
        file_types = {}
        total_size = 0
        total_words = 0
        
        for file_data in files:
            if 'error' not in file_data:
                file_type = file_data['file_type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
                total_size += file_data['file_size']
                total_words += file_data['word_count']
        
        return jsonify({
            'success': True,
            'data': {
                'total_files': total_files,
                'successful_files': successful_files,
                'failed_files': failed_files,
                'file_types': file_types,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_words': total_words,
                'average_words_per_file': round(total_words / successful_files, 2) if successful_files > 0 else 0,
                'processing_success_rate': round((successful_files / total_files) * 100, 2) if total_files > 0 else 0
            }
        })
        
    except Exception as e:
        print(f"Get file stats error: {e}")
        return handle_error('Failed to get file statistics. Please try again.', 500) 