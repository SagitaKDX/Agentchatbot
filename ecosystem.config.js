module.exports = {
  apps: [{
    name: 'english-ai-backend',
    script: '/opt/english-ai-agent/backend/start-production.sh',
    cwd: '/opt/english-ai-agent/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env_file: '/opt/english-ai-agent/.env.production',
    error_file: '/opt/english-ai-agent/logs/backend-error.log',
    out_file: '/opt/english-ai-agent/logs/backend-out.log',
    log_file: '/opt/english-ai-agent/logs/backend.log',
    time: true,
    env: {
      NODE_ENV: 'production'
    }
  }]
}; 