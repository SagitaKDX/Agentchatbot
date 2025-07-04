import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from services.bedrock_service import bedrock_service
from middleware.error_handler import handle_error, handle_validation_error

chat_bp = Blueprint('chat', __name__)

class ChatMessageSchema(Schema):
    message = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 5000)
    conversationHistory = fields.List(fields.Dict(), missing=[])
    context = fields.Str(missing='')

class LessonPlanSchema(Schema):
    topic = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 200)
    level = fields.Str(required=True, validate=lambda x: x in ['beginner', 'intermediate', 'advanced'])
    duration = fields.Int(required=True, validate=lambda x: 15 <= x <= 180)

@chat_bp.route('/message', methods=['POST'])
def send_message():
    try:
        schema = ChatMessageSchema()
        data = schema.load(request.json)
        
        message = data['message']
        conversation_history = data['conversationHistory']
        context = data['context']

        response = bedrock_service.generate_response(
            message, context, conversation_history
        )

        return jsonify({
            'success': True,
            'data': {
                'message': response['text'],
                'timestamp': datetime.now().isoformat() + 'Z',
                'usage': response['usage']
            }
        })

    except ValidationError as e:
        return handle_validation_error(e.messages)
    except Exception as e:
        print(f"Chat message error: {e}")
        return handle_error('Failed to generate response. Please try again.', 500)

@chat_bp.route('/lesson-plan', methods=['POST'])
def generate_lesson_plan():
    try:
        schema = LessonPlanSchema()
        data = schema.load(request.json)
        
        topic = data['topic']
        level = data['level']
        duration = data['duration']

        lesson_plan = bedrock_service.generate_lesson_plan(topic, level, duration)

        return jsonify({
            'success': True,
            'data': {
                'lessonPlan': lesson_plan,
                'topic': topic,
                'level': level,
                'duration': duration,
                'timestamp': datetime.now().isoformat() + 'Z'
            }
        })

    except ValidationError as e:
        return handle_validation_error(e.messages)
    except Exception as e:
        print(f"Lesson plan generation error: {e}")
        return handle_error('Failed to generate lesson plan. Please try again.', 500)

@chat_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Chat service is healthy',
        'timestamp': datetime.now().isoformat() + 'Z'
    }) 