from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase settings
    supabase_url: str
    supabase_key: str
    
    # Azure OpenAI settings
    azure_openai_deployment_name: str
    azure_openai_api_version: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    
    # Azure OpenAI Chat settings
    azure_openai_chat_api_key: str
    azure_openai_chat_api_version: str
    azure_openai_chat_endpoint: str
    azure_openai_chat_model: str

    # Whatsapp settings
    whatsapp_token: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()