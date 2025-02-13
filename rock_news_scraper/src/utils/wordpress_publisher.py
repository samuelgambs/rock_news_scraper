import requests
import json
import os

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.methods.taxonomies import GetTerms, NewTerm
import collections.abc

# CONFIGURAÇÕES DO WORDPRESS
import os

WORDPRESS_URL = os.getenv("WORDPRESS_URL")
WORDPRESS_USER = os.getenv("WORDPRESS_USER")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")

WORDPRESS_URL = "https://o18.277.myftpupload.com/xmlrpc.php"
WORDPRESS_USER = "mndadmin"
WORDPRESS_PASSWORD="Metal38COn82zd$(t$h3EI%i"

def format_videos(video_urls):
    """Gera o código embed do YouTube para os vídeos"""
    embed_code = ""
    for video in video_urls:
        if "youtube.com" in video or "youtu.be" in video:
            embed_code += f'\n\n<iframe width="560" height="315" src="{video}" frameborder="0" allowfullscreen></iframe>'
    return embed_code

def get_published_titles():
    """Lê os títulos já publicados para evitar duplicações."""
    if os.path.exists("news_storage.json"):
        with open("news_storage.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_published_title(title):
    """Salva o título publicado para evitar duplicação."""
    published_titles = get_published_titles()
    if title not in published_titles:
        published_titles.append(title)
        with open("published_titles.json", "w", encoding="utf-8") as file:
            json.dump(published_titles, file, indent=4, ensure_ascii=False)

def publish_to_wordpress(title, content, tags, image_url, video_url):
    """Publica uma notícia no WordPress como rascunho."""
    
    # Evita publicar conteúdo duplicado
    if title in get_published_titles():
        print(f"⚠️ Notícia já publicada: {title}")
        return
    
def get_or_create_tags(client, tags):
    """Verifica se as tags existem no WordPress, senão cria."""
    existing_tags = client.call(GetTerms('post_tag'))

    # 🔥 Alteração importante para evitar o erro
    if not isinstance(existing_tags, collections.abc.Iterable):
        existing_tags = []  # Garante que seja uma lista vazia caso necessário

    existing_tag_names = {tag.name.lower(): tag for tag in existing_tags}

    tag_ids = []
    for tag_name in tags:
        tag_name = tag_name.strip().lower()
        if tag_name in existing_tag_names:
            tag_ids.append(existing_tag_names[tag_name].id)
        else:
            new_tag = client.call(NewTerm({'name': tag_name, 'taxonomy': 'post_tag'}))
            tag_ids.append(new_tag['term_id'])

    return tag_ids
    
def upload_image_to_wordpress(image_url):
    """Faz upload da imagem destacada para o WordPress e retorna o ID."""
    response = requests.get(image_url, stream=True)
    
    if response.status_code != 200:
        print(f"⚠️ Erro ao baixar a imagem {image_url}")
        return None

    # Certifica que o nome tem a extensão correta
    filename = os.path.basename(image_url).split("?")[0]  # Remove query params
    if not filename.endswith((".jpg", ".jpeg", ".png")):
        filename += ".jpg"  # Força extensão válida

    # Salva temporariamente a imagem localmente
    with open(filename, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

    # Upload da imagem para o WordPress
    client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
    with open(filename, "rb") as img:
        data = {
            'name': filename,
            'type': 'image/jpeg',
            'bits': img.read()
        }
        response = client.call(UploadFile(data))

    # Remove a imagem local
    os.remove(filename)

    return response['id'] if response else None

def postar_no_wordpress(storage):
    """Publica todas as notícias armazenadas no JSON no WordPress."""
    client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)

    for news in storage.get_all_news():
        # import pdb; pdb.set_trace()
        titulo = news["translated_title"]
        conteudo = news["translated_content"]
        image_url = news.get("image_url", "")
        entities = news.get("entities", [])
        video_urls = news.get("video_urls", [])
        conteudo += format_videos(video_urls)
        # Filtra apenas entidades do tipo ORG (banda) ou PERSON (músico)

        # tags = list({ent[0] for ent in entities if ent[1] in ["ORG", "PERSON"]})
        # tag_ids = get_or_create_tags(client, tags)

        # Criação do post
        post = WordPressPost()
        post.title = titulo
        post.content = conteudo
        post.post_status = "draft"
        post.terms_names = {
            'category': ['Notícias do Metal']
            # 'post_tag': tag_ids  # Adiciona tags
        }

        # Upload da imagem destacada
        if image_url:
            image_id = upload_image_to_wordpress(image_url)
            if image_id:
                post.thumbnail = image_id

        # Publicação no WordPress
        try:
            post_id = client.call(NewPost(post))
            print(f"✅ Post publicado com sucesso! ID: {post_id}")
            # storage.add_published_title(titulo)  # Adiciona ao JSON de notícias publicadas
        except Exception as e:
            print(f"⚠️ Erro ao publicar no WordPress: {e}")