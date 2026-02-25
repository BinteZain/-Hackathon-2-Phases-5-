from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "notification-service"
    APP_PORT: int = 8082
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
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
    KAFKA_TOPIC_REMINDERS: str = "reminders"
    KAFKA_TOPIC_TASK_EVENTS: str = "task-events"
    
    # Email settings (SMTP)
    SMTP_HOST: str = "smtp.mailtrap.io"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@todo-chatbot.com"
    SMTP_FROM_NAME: str = "Todo Chatbot"
    SMTP_USE_TLS: bool = True
    
    # Push notification settings
    FIREBASE_API_KEY: str = ""
    APNS_KEY_ID: str = ""
    APNS_TEAM_ID: str = ""
    APNS_KEY_PATH: str = ""
    
    # Notification settings
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    BATCH_SIZE: int = 100
    
    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def dapr_base_url(self) -> str:
        """Construct Dapr base URL."""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"
    
    @property
    def log_level(self) -> int:
        """Get logging level."""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
