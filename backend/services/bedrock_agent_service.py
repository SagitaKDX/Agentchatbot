import boto3
import logging
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockAgentService:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Get agent IDs from environment - required
        self.agent_id = os.getenv('BEDROCK_AGENT_ID')
        self.alias_id = os.getenv('BEDROCK_AGENT_ALIAS_ID')
        
        if not self.agent_id or not self.alias_id:
            raise ValueError("BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID must be set in environment variables")
        
        self.sessions = {}
        self.system_prompt = self._get_default_system_prompt()
        
        logger.info(f"Initialized Bedrock Agent Service with Agent ID: {self.agent_id}, Alias ID: {self.alias_id}")

    def _get_default_system_prompt(self):
        return """You are Veron, an expert English AI teaching assistant specializing in technical English for AI, IoT, and chip technology education. Your role is to:

1. Help teachers explain complex technical concepts in simple English
2. Provide vocabulary, grammar, and pronunciation guidance
3. Create lesson plans and teaching materials
4. Suggest effective teaching methods for technical subjects
5. Adapt explanations to different English proficiency levels

Always be encouraging, professional, and educational in your responses. Focus on practical teaching applications.
"""

    def update_system_prompt(self, new_prompt):
        """Update the system prompt for the agent"""
        self.system_prompt = new_prompt
        logger.info("System prompt updated")

    def get_system_prompt(self):
        """Get the current system prompt"""
        return self.system_prompt

    def invoke_agent(self, prompt, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Invoking agent {self.agent_id} with session {session_id}")
            
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.alias_id,
                enableTrace=True,
                sessionId=session_id,
                inputText=prompt
            )
            
            completion = ""
            trace_info = []
            
            for event in response.get("completion"):
                if 'chunk' in event:
                    chunk = event["chunk"]
                    completion += chunk["bytes"].decode()
                
                if 'trace' in event:
                    trace_event = event.get("trace")
                    trace = trace_event['trace']
                    trace_info.append(trace)
                    for key, value in trace.items():
                        logger.info("%s: %s", key, value)
            
            self.sessions[session_id] = {
                'last_used': datetime.now(),
                'message_count': self.sessions.get(session_id, {}).get('message_count', 0) + 1
            }
            
            logger.info(f"Agent response received successfully for session {session_id}")
            
            return {
                'response': completion,
                'session_id': session_id,
                'trace_info': trace_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error("AWS Client error [%s]: %s", error_code, error_message)
            
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Agent not found. Please check your Agent ID ({self.agent_id}) and Alias ID ({self.alias_id}) are correct and the agent is deployed.")
            elif error_code == 'AccessDeniedException':
                raise Exception(f"Access denied. Check your AWS credentials and agent permissions: {error_message}")
            elif error_code == 'ValidationException':
                raise Exception(f"Invalid request: {error_message}")
            else:
                raise Exception(f"AWS error [{error_code}]: {error_message}")
                
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            raise Exception(f"Failed to invoke agent: {str(e)}")

    def create_new_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_used': datetime.now(),
            'message_count': 0
        }
        return session_id

    def get_session_info(self, session_id):
        return self.sessions.get(session_id, None)

    def list_active_sessions(self):
        active_sessions = {}
        current_time = datetime.now()
        
        for session_id, session_data in self.sessions.items():
            time_diff = (current_time - session_data['last_used']).total_seconds()
            if time_diff < 3600:
                active_sessions[session_id] = session_data
                
        return active_sessions

    def cleanup_old_sessions(self):
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session_data in self.sessions.items():
            time_diff = (current_time - session_data['last_used']).total_seconds()
            if time_diff > 3600:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        return len(sessions_to_remove)

def get_bedrock_agent_service():
    if not hasattr(get_bedrock_agent_service, '_instance'):
        get_bedrock_agent_service._instance = BedrockAgentService()
    return get_bedrock_agent_service._instance 