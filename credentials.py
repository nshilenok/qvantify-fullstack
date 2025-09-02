# Supabase Database Configuration
# Using direct connection with IPv4
db_config = {
    'host': 'db.lwwyepvurqddbcbggdvm.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'UkjI7gBAgA6p4MGI',
    'port': 5432
}

# OpenAI API Keys - Use environment variables
import os
openaiapi_key = os.environ.get('OPENAI_API_KEY', 'placeholder')
openaiapi_panda_key = os.environ.get('OPENAI_PANDA_KEY', 'placeholder')
azureopenai_key = os.environ.get('AZURE_OPENAI_KEY', 'placeholder')

# Project configuration
panda_project = "your_panda_project_id"
default_prompt = "Default system prompt"
