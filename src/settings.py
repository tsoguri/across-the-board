from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    weaviate_host: str
    weaviate_port: int
    collection_name: str
    embedding_model: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
