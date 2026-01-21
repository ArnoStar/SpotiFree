from pydantic_settings import BaseSettings, SettingsConfigDict

class _Settings(BaseSettings):
    sql_database_url:str
    
    redis_host:str
    redis_port:int

    jwt_secret_key:str
    jwt_algorithm:str

    register_expiration_time:int

    audio_dir:str
    img_dir:str

    #Mail config

    mail_username:str
    mail_password:str
    mail_from:str
    mail_port:int
    mail_server:str
    mail_tls:bool
    mail_ssl:bool
    use_credentials:bool

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )