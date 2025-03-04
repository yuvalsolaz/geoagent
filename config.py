import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", "0.0")

# Database configuration
DB_CONNECTION_STRING=os.getenv("DB_CONNECTION_STRING", "")
if not DB_CONNECTION_STRING:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "change_detection")
    DB_CONNECTION_STRING=f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SCHEMA_NAME = os.getenv("SCHEMA_NAME", "change_detection")
TABLE_NAME = os.getenv("TABLE_NAME", "detections_new")
SIMPLIFY_SHAPE_TOLERANCE = 0.0
DEFAULT_MAX_DISTANCE_OUTSIDE_MENTIONED_GEOGRAPHIC_ENTITY_KM = os.getenv('DEFAULT_MAX_DISTANCE_OUTSIDE_MENTIONED_GEOGRAPHIC_ENTITY_KM', 10)
REGION = os.getenv("REGION", "")
GEO_DATA_DIR = os.getenv("GEO_DATA_DIR", r"./data/borderlines")