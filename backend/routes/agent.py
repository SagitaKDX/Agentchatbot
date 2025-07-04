import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from services.bedrock_agent_service import get_bedrock_agent_service
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

        response = get_bedrock_agent_service().invoke_agent(message, session_id)

        return jsonify({
            'success': True,
            'data': {
                'message': response['response'],
                'session_id': response['session_id'],
                'timestamp': response['timestamp'],
                'trace_info': response.get('trace_info', [])
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