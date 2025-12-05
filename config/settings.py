# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

# External APIs
NCBI_API_KEY = os.getenv("NCBI_API_KEY")  # PubMed
