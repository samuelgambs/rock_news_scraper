import requests
import json
import os

class Translator:
    def __init__(self):
        """Inicializa o tradutor usando a API Key do Google Cloud Translation"""
        self.api_key = os.getenv("GOOGLE_CLOUD_TRANSLATE_API_KEY")  # Lê a chave das variáveis de ambiente
        self.endpoint = f"https://translation.googleapis.com/language/translate/v2?key={self.api_key}"

        if not self.api_key:
            raise ValueError("⚠️ API Key do Google Cloud Translation não encontrada! Defina a variável de ambiente GOOGLE_CLOUD_TRANSLATE_API_KEY.")

    def translate_text(self, texto):
        payload = json.dumps({
            "q": texto,
            "target": "pt",
            "source": "en"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self.endpoint, headers=headers, data=payload)

        if response.status_code != 200:
            raise Exception(f"Erro na tradução: {response.status_code} - {response.text}")

        result = response.json()
        return result["data"]["translations"][0]["translatedText"]

def translate_news(storage):
    """Traduz notícias para português e atualiza no JSON"""
    translator = Translator()

    for news in storage.get_all_news():
        if "translated_content" not in news:  # Evita traduções duplicadas
            print(f"🌎 Traduzindo: {news['title']}...")
            translated_title = translator.translate_text(news["title"])
            translated_content = translator.translate_text(news["content"])
            news["translated_title"] = translated_title
            news["translated_content"] = translated_content
    storage.save_news(storage.get_all_news())