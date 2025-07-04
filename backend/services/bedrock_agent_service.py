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
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.agent_id = "XQLPZTJB60"
        self.alias_id = "PQSMMMIGTM"
        self.sessions = {}
        self.system_prompt = self._get_default_system_prompt()

    def _get_default_system_prompt(self):
        return """IMPORTANT INSTRUCTIONS:
- You are an English teaching AI assistant focused on helping with language learning and technical English.
- NEVER ask users to write functions, code, or technical implementations.
- If you cannot access information, knowledge bases, or external resources, simply respond with "I can't access that information right now."
- Do not request users to provide code examples, write functions, or implement solutions.
- Focus on explaining concepts clearly in simple English rather than asking for technical work.
- Keep responses educational and helpful for English language learners.
- Provide clear, concise explanations without requiring users to do technical work.

User question: """

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
        
        # Combine system prompt with user prompt
        full_prompt = self.system_prompt + prompt
        
        try:
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.alias_id,
                enableTrace=True,
                sessionId=session_id,
                inputText=full_prompt
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
            
            return {
                'response': completion,
                'session_id': session_id,
                'trace_info': trace_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error("Client error: %s", str(e))
            raise Exception(f"Failed to invoke agent: {str(e)}")
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