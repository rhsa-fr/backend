# ============================================================================
# FILE: app/config.py
# ============================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Sistem Koperasi Simpan Pinjam"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API untuk Sistem Informasi Koperasi Simpan Pinjam"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "koperasi_simpan_pinjam"
    
    # Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # JWT & Security Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Password Hashing
    BCRYPT_ROUNDS: int = 12
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # File Upload Settings
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    
    # Koperasi Business Rules
    DEFAULT_BUNGA_PERSEN: float = 2.0
    DENDA_KETERLAMBATAN_PERSEN: float = 0.5
    MAX_LAMA_ANGSURAN: int = 60
    MIN_NOMINAL_PINJAMAN: float = 1000000.0
    MAX_NOMINAL_PINJAMAN: float = 100000000.0
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL from components"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert allowed extensions string to list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]


settings = Settings()