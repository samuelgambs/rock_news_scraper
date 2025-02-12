import json
import os

class NewsStorage:
    def __init__(self, file_path="news_storage.json"):
        self.file_path = file_path
        self.news = self.load_news()

    def load_news(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_news(self, news_data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(news_data, file, indent=4, ensure_ascii=False)

    def add_news(self, title, link, date, content, image_url, video_urls):
        if not self.news_exists(title):
            self.news.append({
                "title": title,
                "link": link,
                "date": date,
                "content": content,
                "image_url": image_url,
                "video_urls": video_urls
            })
            self.save_news(self.news)

    def news_exists(self, title):
        return any(news["title"] == title for news in self.news)

    def get_all_news(self):
        return self.news
    
    def _load_titles(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def get_published_titles(self):
        return self._load_titles

    def add_published_title(self, title):
        if title not in self.published_titles:
            self.published_titles.append(title)
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(self.published_titles, file, indent=4, ensure_ascii=False)

