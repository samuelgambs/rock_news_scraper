import requests
import os
import base64
from requests.auth import HTTPBasicAuth

# 🔧 Configurações do WordPress (use variáveis de ambiente para segurança)
WORDPRESS_URL = os.getenv("WORDPRESS_URL", "https://metalneverdie.com.br")
WORDPRESS_USER = os.getenv("WORDPRESS_USER", "novoapi")
WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "zDF4YnMjO9YHOVAVNKzB047D")

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
    """Gera o código embed do YouTube para os vídeos"""
    embed_code = ""
    for video in video_urls:
        if "youtube.com" in video or "youtu.be" in video:
            embed_code += f'\n\n<iframe width="560" height="315" src="{video}" frameborder="0" allowfullscreen></iframe>'
    return embed_code

# def get_published_titles():
#     """Obtém títulos dos últimos 100 posts para evitar duplicação"""
#     response = requests.get(POSTS_ENDPOINT + "?per_page=100")

#     if response.status_code == 200:
#         return {post["title"]["rendered"] for post in response.json()}
#     else:
#         import pdb; pdb.set_trace()
#         print(f"⚠️ Erro ao buscar posts existentes: {response.status_code}, {response.text}")
#         return set()

def get_published_titles():
    """Obtém os títulos das últimas 100 postagens para evitar duplicações."""
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts?per_page=100"
    response = requests.get(url, auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD))

    if response.status_code == 200:
        return [post["title"]["rendered"] for post in response.json()]
    else:
        print(f"⚠️ Erro ao buscar posts existentes: {response.status_code}, {response.text}")
        return []

def upload_image_to_wordpress(image_url):
    """Faz upload da imagem destacada para o WordPress e retorna o ID."""

    response = requests.get(image_url, stream=True)
    
    if response.status_code != 200:
        print(f"⚠️ Erro ao baixar a imagem {image_url}")
        return None

    filename = os.path.basename(image_url).split("?")[0]
    if not filename.endswith((".jpg", ".jpeg", ".png")):
        filename += ".jpg"

    with open(filename, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

    # 📌 Envia a imagem para o WordPress
    with open(filename, "rb") as img:
        files = {"file": (filename, img, "image/jpeg")}
        headers = {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Disposition": f"attachment; filename={filename}",
        }
        response = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/media", headers=headers, files=files)

    os.remove(filename)

    if response.status_code == 201:
        image_id = response.json().get("id")
        print(f"✅ Imagem enviada com sucesso! ID: {image_id}")
        return image_id
    else:
        print(f"⚠️ Erro ao enviar imagem: {response.status_code}, {response.text}")
        return None



def get_or_create_tags(tags):
    """Cria tags se não existirem e retorna os IDs"""
    tag_ids = []
    for tag in tags:
        url = f"{WORDPRESS_URL}/wp-json/wp/v2/tags?search={tag}"
        response = requests.get(url, auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD))

        if response.status_code == 200 and response.json():
            tag_id = response.json()[0]["id"]
        else:
            new_tag_data = {"name": tag}
            create_response = requests.post(f"{WORDPRESS_URL}/wp-json/wp/v2/tags", json=new_tag_data, auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD))
            tag_id = create_response.json().get("id") if create_response.status_code == 201 else None

        if tag_id:
            tag_ids.append(tag_id)

    return tag_ids

def postar_no_wordpress(storage):
    """Publica as notícias no WordPress usando a REST API"""
    published_titles = get_published_titles()

    for news in storage.get_all_news():
        titulo = news["translated_title"]
        conteudo = news["translated_content"]
        image_url = news.get("image_url", "")
        video_urls = news.get("video_urls", [])
        tags = news["tags"]

        # Verifica se a notícia já foi publicada
        if titulo in published_titles:
            print(f"⚠️ Notícia já publicada: {titulo}")
            continue  # Pula para a próxima notícia

        conteudo += format_videos(video_urls)

        # Obtém ou cria as tags
        tag_ids = get_or_create_tags(tags)

        # Faz o upload da imagem destacada
        image_id = upload_image_to_wordpress(image_url) if image_url else None

        # 📌 Dados do post
        post_data = {
            "title": titulo,
            "content": conteudo,
            "status": "draft",  # Publica como rascunho (mude para "publish" para publicar direto)
            "categories": [1],  # ID da categoria
            "tags": tag_ids,
        }

        if image_id:
            post_data["featured_media"] = image_id

        # 🔗 URL da API REST
        url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"

        # 🛠️ Enviar requisição
        response = requests.post(url, json=post_data, auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD))

        if response.status_code == 201:
            print(f"✅ Post publicado com sucesso! ID: {response.json().get('id')}")
        else:
            print(f"❌ Erro ao publicar: {response.status_code}, {response.text}")


# import requests
# import json
# import os

# from wordpress_xmlrpc import Client, WordPressPost
# from wordpress_xmlrpc.methods.posts import NewPost, GetPosts
# from wordpress_xmlrpc.methods.media import UploadFile
# from wordpress_xmlrpc.methods.taxonomies import GetTerms, NewTerm
# from collections.abc import Iterable 
# from src.utils.news_storage import NewsStorage
# # CONFIGURAÇÕES DO WORDPRESS
# import os

# # WORDPRESS_URL = os.getenv("WORDPRESS_URL")
# # WORDPRESS_USER = os.getenv("WORDPRESS_USER")
# # WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")


# WORDPRESS_URL = "https://metalneverdie.com.br/xmlrpc.php"
# WORDPRESS_USER = "mndadmin"
# WORDPRESS_PASSWORD = "Metal38COn82zd$(t$h3EI%i"

# # WORDPRESS_URL = os.getenv("WORDPRESS_URL", "https://metalneverdie.com.br")
# # WORDPRESS_USER = os.getenv("WORDPRESS_USER", "mndadmin")
# # WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "sqBRy zKfl dsij Nnuw RaCl Ef93")

# def format_videos(video_urls):
#     """Gera o código embed do YouTube para os vídeos"""
#     embed_code = ""
#     for video in video_urls:
#         if "youtube.com" in video or "youtu.be" in video:
#             embed_code += f'\n\n<iframe width="560" height="315" src="{video}" frameborder="0" allowfullscreen></iframe>'
#     return embed_code

# def get_published_titles():
#     """Lê os títulos já publicados para evitar duplicações."""
#     if os.path.exists("news_storage.json"):
#         with open("news_storage.json", "r", encoding="utf-8") as file:
#             return json.load(file)
#     return []

# def save_published_title(title):
#     """Salva o título publicado para evitar duplicação."""
#     published_titles = get_published_titles()
#     if title not in published_titles:
#         published_titles.append(title)
#         with open("published_titles.json", "w", encoding="utf-8") as file:
#             json.dump(published_titles, file, indent=4, ensure_ascii=False)


# def upload_image_to_wordpress(image_url):
#     """Faz upload da imagem destacada para o WordPress e retorna o ID."""
#     response = requests.get(image_url, stream=True)
    
#     if response.status_code != 200:
#         print(f"⚠️ Erro ao baixar a imagem {image_url}")
#         return None

#     # Certifica que o nome tem a extensão correta
#     filename = os.path.basename(image_url).split("?")[0]  # Remove query params
#     if not filename.endswith((".jpg", ".jpeg", ".png")):
#         filename += ".jpg"  # Força extensão válida

#     # Salva temporariamente a imagem localmente
#     with open(filename, "wb") as file:
#         for chunk in response.iter_content(1024):
#             file.write(chunk)

#     # Upload da imagem para o WordPress
#     client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
#     with open(filename, "rb") as img:
#         data = {
#             'name': filename,
#             'type': 'image/jpeg',
#             'bits': img.read()
#         }
#         response = client.call(UploadFile(data))

#     # Remove a imagem local
#     os.remove(filename)

#     return response['id'] if response else None

# def news_already_published(title):
#     """Verifica se o título já foi publicado no WordPress."""
#     client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
    
#     posts = client.call(GetPosts({'number': 100}))  # Busca os últimos 100 posts
#     return any(post.title == title for post in posts)

# def postar_no_wordpress(storage):
#     # if not self.storage.news_exists(title):

#     """Publica todas as notícias armazenadas no JSON no WordPress."""
#     client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)

#     for news in storage.get_all_news():
#         # import pdb; pdb.set_trace()
#         titulo = news["translated_title"]
#         conteudo = news["translated_content"]
#         image_url = news.get("image_url", "")
#         entities = news.get("entities", [])
#         video_urls = news.get("video_urls", [])
#         tags = news["tags"]
#         conteudo += format_videos(video_urls)
#         # Filtra apenas entidades do tipo ORG (banda) ou PERSON (músico)

#         # tags = list({ent[0] for ent in entities if ent[1] in ["ORG", "PERSON"]})
#         # tag_ids = get_or_create_tags(client, tags)
#         if NewsStorage.news_exists_db(storage, titulo):
#             print(f"⚠️ Notícia já publicada no WordPress: {titulo}")
#             return

#         # Criação do post
#         post = WordPressPost()
#         post.title = titulo
#         post.content = conteudo
#         post.post_status = "draft"
#         post.terms_names = {
#             'category': ['Notícias do Metal'],
#             'post_tag': tags  # Adiciona tags
#         }

#         # Upload da imagem destacada
#         if image_url:
#             image_id = upload_image_to_wordpress(image_url)
#             if image_id:
#                 post.thumbnail = image_id

#         # Publicação no WordPress
#         try:
#             post_id = client.call(NewPost(post))
#             print(f"✅ Post publicado com sucesso! ID: {post_id}")
#             # storage.add_published_title(titulo)  # Adiciona ao JSON de notícias publicadas
#         except Exception as e:
#             print(f"⚠️ Erro ao publicar no WordPress: {e}")