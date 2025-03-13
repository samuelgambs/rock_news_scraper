import requests
import os
import base64
from requests.auth import HTTPBasicAuth
import logging

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔧 Configurações do WordPress (use variáveis de ambiente para segurança)
WORDPRESS_URL = "https://metalneverdie.com.br"
WORDPRESS_USER = "mndadmin"
WORDPRESS_APP_PASSWORD = "KUamcBwdMNiPmwKqOT6bY4qO"

# Endpoints da API REST do WordPress
POSTS_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
MEDIA_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/media"
TAGS_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/tags"

# Autenticação com Basic Auth
auth_string = f"{WORDPRESS_USER}:{WORDPRESS_APP_PASSWORD}"
auth_encoded = base64.b64encode(auth_string.encode()).decode()

HEADERS = {
    "Authorization": f"Basic {auth_encoded}",
    "Content-Type": "application/json"
}


def format_videos(video_urls):
    """Gera código embed do YouTube para os vídeos"""
    return "".join([
        f'\n\n<iframe width="560" height="315" src="{video}" frameborder="0" allowfullscreen></iframe>'
        for video in video_urls if "youtube.com" in video or "youtu.be" in video
    ])


def get_published_titles():
    """Obtém títulos dos últimos 100 posts para evitar duplicação"""
    response = requests.get(POSTS_ENDPOINT + "?per_page=100", headers=HEADERS)

    if response.status_code == 200:
        return {post["title"]["rendered"] for post in response.json()}
    else:
        import pdb
        pdb.set_trace()
        print(f"⚠️ Erro ao buscar posts existentes: {response.status_code}, {response.text}")
        return set()


def upload_image_to_wordpress(image_url):
    """Faz upload da imagem destacada para o WordPress e retorna o ID."""
    response = requests.get(image_url, stream=True)

    if response.status_code != 200:
        print(f"⚠️ Erro ao baixar a imagem {image_url}")
        return None

    # Define nome do arquivo
    filename = os.path.basename(image_url).split("?")[0]
    if not filename.endswith((".jpg", ".jpeg", ".png")):
        filename += ".jpg"

    # Salva a imagem temporariamente
    with open(filename, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

    # Lê a imagem para envio
    with open(filename, "rb") as img:
        files = {"file": (filename, img, "image/jpeg")}
        headers = {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Disposition": f"attachment; filename={filename}",
        }
        response = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/media", headers=headers, files=files)

    os.remove(filename)

    if response.status_code == 201:
        print(f"✅ Imagem enviada com sucesso! ID: {response.json()['id']}")
        return response.json()["id"]
    else:
        print(f"⚠️ Erro ao enviar imagem: {response.status_code}, {response.text}")
        return None


def get_or_create_tags(tags):
    """Obtém ou cria tags no WordPress e retorna IDs"""
    tag_ids = []

    for tag in tags:
        search_response = requests.get(f"{TAGS_ENDPOINT}?search={tag}", headers=HEADERS)

        if search_response.status_code == 200 and search_response.json():
            tag_id = search_response.json()[0]["id"]
        else:
            create_response = requests.post(TAGS_ENDPOINT, json={"name": tag}, headers=HEADERS)
            tag_id = create_response.json().get("id") if create_response.status_code == 201 else None

        if tag_id:
            tag_ids.append(tag_id)

    return tag_ids


def postar_no_wordpress(storage):
    """Publica notícias no WordPress via API REST"""
    published_titles = get_published_titles()

    for news in storage.get_all_news():
        titulo = news["translated_title"]
        conteudo = news["translated_content"]
        image_url = news.get("image_url", "")
        video_urls = news.get("video_urls", [])
        tags = news["tags"]

        if titulo in published_titles:
            print(f"⚠️ Notícia já publicada: {titulo}")
            continue  # Pula para a próxima notícia

        conteudo += format_videos(video_urls)

        tag_ids = get_or_create_tags(tags)

        # Upload da imagem destacada
        image_id = upload_image_to_wordpress(image_url) if image_url else None

        post_data = {
            "title": titulo,
            "content": conteudo,
            "status": "draft",  # Publica como rascunho (mude para "publish" para publicar direto)
            "categories": [1],  # ID da categoria
            "tags": tag_ids,
        }

        if image_id:
            post_data["featured_media"] = image_id

        try:
            response = requests.post(POSTS_ENDPOINT, json=post_data, headers=HEADERS)

            if response.status_code == 201:
                logging.info(f"Post publicado com sucesso! ID: {response.json().get('id')}")
                storage.mark_as_published(news["link"])  # Marca como publicado no Supabase
            else:
                logging.error(f"Erro ao publicar: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de requisição ao publicar: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Erro inesperado ao publicar: {e}", exc_info=True)

