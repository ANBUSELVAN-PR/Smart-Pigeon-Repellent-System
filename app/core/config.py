from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "change-me"
    device_token: str = "change-device-token"
    database_url: str = "sqlite:///./smart_pigeon.db"
    upload_dir: str = "runtime_images"
    max_image_bytes: int = 5 * 1024 * 1024
    inference_provider: str = "mock"
    model_path: str = "models/pigeon_detector.pt"
    confidence_threshold: float = .65
    detection_distance_cm: float = 150
    buzzer_min_hz: int = 1800
    buzzer_max_hz: int = 4200
    frequency_change_interval_s: int = 8
    max_repellent_duration_s: int = 120
    cooldown_s: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

