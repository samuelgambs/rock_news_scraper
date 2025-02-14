import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configura Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def news_exists(title: str) -> bool:
    """Verifica se uma notícia com o título já existe no banco."""
    response = supabase.table("news").select("title").eq("title", title).execute()
    return len(response.data) > 0

def save_news(news):
    """Salva uma notícia no banco."""
    response = supabase.table("news").insert(news).execute()
    return response
