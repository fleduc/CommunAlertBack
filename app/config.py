import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables définies dans le fichier .env

# Clé secrète pour signer les tokens (à changer en production)
SECRET_KEY = os.getenv("SECRET_KEY", "ma_clé_secrète_ultra_complexe")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL")
