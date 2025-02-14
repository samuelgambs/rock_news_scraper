import os
import sys
from openai import OpenAI

class OpenAIUtils:
    """Classe utilitária para tradução e extração de tags usando a API da OpenAI."""

    def __init__(self):
        self.api_key = os.getenv("CHATGPT_API_URL")
        if not self.api_key:
            raise ValueError("❌ CHATGPT_API_URL não foi definida como variável de ambiente.")

        # Inicializa o cliente OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def _call_openai(self, prompt: str, model="gpt-4-turbo"):
        """Chama a API da OpenAI e retorna a resposta."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Erro ao chamar OpenAI: {e}", file=sys.stderr)
            return None

    def translate_text(self, text: str, target_language="pt") -> str:
        """Traduz um texto para o idioma desejado."""
        if not text.strip():
            return ""

        prompt = f"Traduza o seguinte texto para {target_language} mantendo o contexto original:\n\n{text}"
        return self._call_openai(prompt) or ""

    def extract_tags(self, text: str) -> list:
        """Extrai tags relevantes do conteúdo da matéria, focando em rock, metal e eventos."""
        if not text.strip():
            return []

        prompt = (
            "Analise o seguinte texto e extraia palavras-chave relevantes como bandas, artistas, festivais, "
            "eventos, álbuns e termos relacionados ao rock e heavy metal. "
            "Retorne as palavras separadas por vírgulas.\n\n" + text
        )

        tags = self._call_openai(prompt)
        return [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

    def translate_news(self, storage):
        """Traduz notícias para português e atualiza no Supabase."""
        for news in storage.get_all_news():
            if news.get("translated_content"):
                continue  # Evita retraduzir notícias já processadas
            
            print(f"🌎 Traduzindo: {news['title']}...")

            news["translated_title"] = self.translate_text(news["title"])
            news["translated_content"] = self.translate_text(news["content"])
            news["tags"] = self.extract_tags(news["translated_content"])

            # Atualiza no Supabase
            storage.update_translated_news_db(
                news["title"], news["translated_title"], news["translated_content"], news["tags"]
            )

if __name__ == "__main__":
    openai_utils = OpenAIUtils()
