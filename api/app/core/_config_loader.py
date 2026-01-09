from pydantic_settings import BaseSettings, SettingsConfigDict

class _Settings(BaseSettings):
    sql_database_url:str
    
    redis_host:str
    redis_port:int

    jwt_secret_key:str
    jwt_algorithm:str

    register_expiration_time:int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )