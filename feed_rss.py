import time
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.compat import xmlrpc_client

POSTED_NEWS_FILE = "posted_news.json"

WORDPRESS_URL = "https://o18.277.myftpupload.com/xmlrpc.php"
WORDPRESS_USER = ""
WORDPRESS_PASSWORD = ""
OPENAI_API_KEY = ""

# Carregar notícias já postadas
def load_posted_news():
    try:
        with open(POSTED_NEWS_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Salvar notícias já postadas
def save_posted_news(posted_news):
    existing_news = load_posted_news()
    existing_news.update(posted_news)  # Atualiza o conjunto existente
    with open(POSTED_NEWS_FILE, "w") as file:
        json.dump(list(existing_news), file)

PROCESSED_NEWS = load_posted_news()

def fetch_news(limit=22):
    feed_url = "https://blabbermouth.net/feed"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        return []
    
    news_list = []
    count = 0
    
    for entry in feed.entries:
        if count >= limit:
            break
        
        title = entry.title
        link = entry.link
        date = entry.published
        
        if title in PROCESSED_NEWS:
            continue  # Pula notícias já postadas
        
        content, image_url = fetch_news_content(link) if link else ("No content available", None)
        
        news_list.append({
            "title": title,
            "link": link,
            "date": date,
            "content": content,
            "image_url": image_url
        })
        
        PROCESSED_NEWS.add(title)
        count += 1
    
    return news_list

def fetch_news_content(news_url):
    response = requests.get(news_url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        return "No content found", None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', class_='news-content margin__top-xlarge margin__bottom-xlarge')
    
    if content_div:
        content = content_div.get_text(separator='\n', strip=True)
        
        # Clean up content to ensure proper formatting
        content = content.replace('"', "'")
        paragraphs = content.split('\n')
        formatted_content = '\n\n'.join(paragraphs)
        
        # Extract YouTube video links and generate embed code
        youtube_embeds = []
        for iframe in content_div.find_all('iframe'):
            src = iframe.get('src')
            if 'youtube.com' in src or 'youtu.be' in src:
                youtube_embeds.append(f'<iframe width="560" height="315" src="{src}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>')
        
        if youtube_embeds:
            formatted_content += "\n\nVideos:\n" + "\n".join(youtube_embeds)
        
        # Extract image URL from the container__content div
        container_div = soup.find('div', class_='container__content')
        image_url = None
        if container_div:
            img_tag = container_div.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
        
        # if image_url:
            # Add the extracted image to the beginning of the formatted content
            # formatted_content = f'<img src="{image_url}">\n\n' + formatted_content
        
        # formatted_content += f"\n\nFonte: {news_url}"  # Append the reference URL
        return formatted_content, image_url
    return "No content found", None

def translate_to_portuguese(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "Translate the following text to Portuguese."},
                     {"role": "user", "content": text}]
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error translating text: {e}")
        return "Translation failed."

def extract_tags_from_title(title):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "Extract rock and metal artist names from the following title and return them as a comma-separated list."},
                     {"role": "user", "content": title}]
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        tags = response.json()["choices"][0]["message"]["content"]
        # Split tags by comma and clean up
        tags = [tag.strip().title() for tag in tags.split(',')]
        return tags
    except requests.exceptions.RequestException as e:
        print(f"Error extracting tags: {e}")
        return []

def upload_image_to_wordpress(image_url):
    client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        image_name = image_url.split("/")[-1]
        
        data = {
            'name': image_name,
            'type': 'image/jpeg',  # You might need to adjust this based on the image type
        }
        
        data['bits'] = xmlrpc_client.Binary(image_data)
        response = client.call(UploadFile(data))
        return response['id']
    return None

def postar_no_wordpress(titulo, conteudo, image_url, tags):
    client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
    post = WordPressPost()
    post.title = titulo
    post.content = conteudo
    post.post_status = "publish"
    post.terms_names = {
        'category': ['Notícias do Metal'],
        'post_tag': tags  # Add tags to the post
    }
    
    if image_url:
        image_id = upload_image_to_wordpress(image_url)
        if image_id:
            post.thumbnail = image_id
    
    try:
        post_id = client.call(NewPost(post))
        print(f"Post publicado com sucesso! ID: {post_id}")
    except Exception as e:
        print("Erro ao publicar no WordPress:", e)

        
news_items = fetch_news(limit=20)
if news_items:
    for news_item in news_items:
        translated_title = translate_to_portuguese(news_item['title'])
        content, image_url = fetch_news_content(news_item['link'])
        translated_content = translate_to_portuguese(content)
        tags = extract_tags_from_title(news_item['title'])

        if translated_title != "Translation failed." and translated_content != "Translation failed.":
            print(translated_title, translated_content)
            save_posted_news(PROCESSED_NEWS)
            # Add a delay to avoid hitting the rate limit
            time.sleep(10)
            # Optionally, post to WordPress
            postar_no_wordpress(translated_title, translated_content, image_url, tags)
