import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


class KafkaSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC: str = "stock-events"
    KAFKA_CONSUMER_GROUP: str = "default-group"

    class Config:
        env_file = ".env"
        extra = "ignore"


kafka_settings = KafkaSettings()
