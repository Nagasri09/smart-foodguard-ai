import os
from dotenv import load_dotenv
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-this-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "CHANGE_ME_DEVICE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodguard.db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
