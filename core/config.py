from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    genderize_api: str
    agify_api:str
    nationalize_api:str
    mongo_db: str
    
    model_config = SettingsConfigDict(env_file=".env")