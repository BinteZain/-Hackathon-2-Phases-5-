from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "recurring-service"
    APP_PORT: int = 8081
    DEBUG: bool = False
    
    # Database settings
    DATABASE_HOST: str = "postgresql.postgres.svc.cluster.local"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "todo_chatbot"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres123"
    
    # Dapr settings
    DAPR_HTTP_PORT: int = 3500
    DAPR_PUBSUB_NAME: str = "pubsub-kafka"
    DAPR_STATE_STORE_NAME: str = "state-redis"
    
    # Kafka topics
    KAFKA_TOPIC_TASK_EVENTS: str = "task-events"
    KAFKA_TOPIC_TASK_UPDATES: str = "task-updates"
    
    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def dapr_base_url(self) -> str:
        """Construct Dapr base URL."""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
