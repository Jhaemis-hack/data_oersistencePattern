from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    genderize_api: str
    
    model_config = SettingsConfigDict(env_file=".env")