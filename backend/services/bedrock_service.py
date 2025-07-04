import os
import json
import boto3
from botocore.exceptions import ClientError

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID')
    
    def generate_response(self, message, context='', conversation_history=None):
        if conversation_history is None:
            conversation_history = []
            
        try:
            system_prompt = """You are Veron, an expert English AI teaching assistant specializing in technical English for AI, IoT, and chip technology education. Your role is to:

1. Help teachers explain complex technical concepts in simple English
2. Provide vocabulary, grammar, and pronunciation guidance
3. Create lesson plans and teaching materials
4. Suggest effective teaching methods for technical subjects
5. Adapt explanations to different English proficiency levels

Context from knowledge base: {context}

Always be encouraging, professional, and educational in your responses. Focus on practical teaching applications.""".format(context=context)

            messages = []
            for msg in conversation_history[-10:]:
                role = 'user' if msg.get('sender') == 'user' else 'assistant'
                messages.append({
                    'role': role,
                    'content': msg.get('text', '')
                })
            
            messages.append({
                'role': 'user',
                'content': message
            })

            request_body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'system': system_prompt,
                'messages': messages,
                'temperature': 0.7,
                'top_p': 0.9
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            
            return {
                'text': response_body['content'][0]['text'],
                'usage': response_body.get('usage', {})
            }

        except ClientError as e:
            print(f"Bedrock API Error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def generate_lesson_plan(self, topic, level, duration):
        try:
            system_prompt = "You are Veron, an expert English teaching assistant. Create a detailed lesson plan for teaching technical English. Format the response as a structured lesson plan with clear sections."

            message = f"Create a {duration}-minute lesson plan for teaching \"{topic}\" to {level} level English students. Include objectives, vocabulary, activities, and assessment methods."

            request_body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 3000,
                'system': system_prompt,
                'messages': [{
                    'role': 'user',
                    'content': message
                }],
                'temperature': 0.5,
                'top_p': 0.8
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except ClientError as e:
            print(f"Lesson plan generation error: {e}")
            raise Exception(f"Failed to generate lesson plan: {str(e)}")

    def analyze_document(self, text, filename):
        try:
            system_prompt = "You are Veron, analyzing a teaching document. Extract key vocabulary, concepts, and teaching points that would be useful for English teachers in technical subjects."

            message = f"""Analyze this document "{filename}" and extract:
1. Key technical vocabulary terms
2. Main concepts to teach
3. Suggested teaching activities
4. Difficulty level assessment

Document content: {text[:4000]}"""

            request_body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'system': system_prompt,
                'messages': [{
                    'role': 'user',
                    'content': message
                }],
                'temperature': 0.3,
                'top_p': 0.7
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except ClientError as e:
            print(f"Document analysis error: {e}")
            raise Exception(f"Failed to analyze document: {str(e)}")

bedrock_service = BedrockService() 