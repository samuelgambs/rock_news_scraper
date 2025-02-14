import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient

# Carrega variáveis de ambiente do .env
load_dotenv()

# 🔧 Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔧 Configurações do WordPress
WORDPRESS_URL = "https://metalneverdie.com.br"
WORDPRESS_USER = "mndadmin"
WORDPRESS_APP_PASSWORD = "KUamcBwdMNiPmwKqOT6bY4qO"
TAGS_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/tags"


# 🔗 Endpoints do WordPress
POSTS_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
MEDIA_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/media"

# 🔧 Autenticação básica no WordPress
AUTH = HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD)

# 📌 Conectar ao Supabase
supabase = SyncPostgrestClient(f"{SUPABASE_URL}/rest/v1", headers={"apikey": SUPABASE_KEY})
def get_posts_from_supabase():
    """Obtém posts do Supabase com ID entre 823 e 863."""
    try:
        response = supabase.table("news").select("*").gte("id", 823).lte("id", 863).execute()
        return response.data
    except Exception as e:
        print(f"❌ Erro ao buscar posts do Supabase: {e}")
        return []

def upload_image(image_url):
    """Faz upload da imagem para o WordPress."""
    try:
        image_response = requests.get(image_url, stream=True)
        if image_response.status_code != 200:
            print(f"⚠️ Erro ao baixar imagem: {image_url}")
            return None

        files = {
            "file": (os.path.basename(image_url), image_response.raw, "image/jpeg"),
        }
        response = requests.post(MEDIA_ENDPOINT, auth=AUTH, files=files)

        if response.status_code == 201:
            return response.json()["id"]
        else:
            print(f"⚠️ Erro ao enviar imagem: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao fazer upload da imagem: {e}")
        return None

def get_or_create_tags(entities):
    """Verifica se as entidades já existem como tags no WordPress e cria caso necessário."""
    tag_ids = []
    
    for tag in entities:
        tag = tag.strip().title()  # Normaliza o nome da tag
        response = requests.get(f"{TAGS_ENDPOINT}?search={tag}", auth=AUTH)

        if response.status_code == 200 and response.json():
            tag_id = response.json()[0]["id"]  # Tag já existe
        else:
            new_tag_data = {"name": tag}
            create_response = requests.post(TAGS_ENDPOINT, json=new_tag_data, auth=AUTH)
            tag_id = create_response.json().get("id") if create_response.status_code == 201 else None
        
        if tag_id:
            tag_ids.append(tag_id)

    return tag_ids

def check_if_post_exists(title):
    """Verifica se o título do post já existe no WordPress para evitar duplicações."""
    response = requests.get(f"{POSTS_ENDPOINT}?search={title}", auth=AUTH)

    if response.status_code == 200 and response.json():
        print(f"⚠️ Post '{title}' já existe no WordPress. Pulando...")
        return True
    return False

def post_to_wordpress(post_data):
    """Publica um post no WordPress."""
    response = requests.post(POSTS_ENDPOINT, auth=AUTH, json=post_data)

    if response.status_code == 201:
        print(f"✅ Post publicado com sucesso! ID: {response.json()['id']}")
        return response.json()["id"]
    else:
        print(f"❌ Erro ao publicar post: {response.status_code}, {response.text}")
        return None

def mark_as_published(post_id):
    """Marca o post no Supabase como publicado."""
    try:
        supabase.table("news").update({"published": True}).eq("id", post_id).execute()
        print(f"✅ Post {post_id} marcado como publicado no Supabase.")
    except Exception as e:
        print(f"❌ Erro ao marcar post {post_id} como publicado: {e}")

def format_videos(video_urls):
    """Gera o código embed do YouTube para os vídeos"""
    embed_code = ""
    for video in video_urls:
        if "youtube.com" in video or "youtu.be" in video:
            embed_code += f'\n\n<iframe width="560" height="315" src="{video}" frameborder="0" allowfullscreen></iframe>'
    return embed_code

def main():
    posts = get_posts_from_supabase()

    if not posts:
        print("⚠️ Nenhum post encontrado no Supabase.")
        return

    for post in posts:
        title = post["translated_title"]
        content = post["translated_content"]
        image_url = post.get("image_url", "")
        video_urls = post.get("video_urls", [])
        entities = post.get("entities", [])  # Pegando as tags do Supabase

        # Se já existir no WordPress, pula
        if check_if_post_exists(title):
            continue

        # Formata vídeos no conteúdo
        content += format_videos(video_urls)

        # Obtém ou cria tags no WordPress
        tag_ids = get_or_create_tags(entities)

        # Faz upload da imagem
        image_id = upload_image(image_url) if image_url else None

        # Dados do post para o WordPress
        post_data = {
            "title": title,
            "content": content,
            "status": "draft",  # Mude para "publish" se quiser publicar direto
            "categories": [1],  # ID da categoria no WordPress
            "tags": tag_ids,  # Tags vinculadas ao post
        }

        if image_id:
            post_data["featured_media"] = image_id

        # Publica no WordPress
        post_id = post_to_wordpress(post_data)

        if post_id:
            mark_as_published(post["id"])  # Marca no Supabase como publicado

if __name__ == "__main__":
    main()