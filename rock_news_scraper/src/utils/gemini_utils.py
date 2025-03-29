import os
import google.generativeai as genai

class GeminiUtils:
    def __init__(self):
        """Inicializa a API do Gemini com a chave fornecida."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ A chave da API GEMINI_API_KEY não foi definida.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def translate_text(self, text, target_language="Portuguese"):
        """
        Usa o Gemini para traduzir um texto para o idioma desejado.
        :param text: Texto original em inglês (ou outro idioma).
        :param target_language: Idioma para traduzir. Padrão: Português.
        :return: Texto traduzido.
        """
        if not text.strip():
            return ""

        prompt = f"Analise o {text}, e retorne somente a tradução em portugues sem mais textos e/ou comentários adicionais, pois estamos publicando no wordpress "
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Erro na tradução: {e}")
            return text  # Retorna o texto original em caso de falha

    def extract_tags(self, text):
        """
        Usa o Gemini para extrair tags relevantes de um texto de rock/metal.
        :param text: Conteúdo da matéria ou notícia.
        :return: Lista de tags extraídas.
        """
        prompt = f"""
        Analise o seguinte texto e extraia palavras-chave relevantes como bandas, artistas, festivais, 
        eventos, álbuns e termos relacionados ao rock e heavy metal. 

        Retorne as palavras separadas por vírgulas, limitado até 10 palavras.

        Texto: {text}
        """

        try:
            response = self.model.generate_content(prompt)
            tags = response.text.strip().split(", ")
            return [tag.strip() for tag in tags if tag]  # Limpeza básica
        except Exception as e:
            print(f"⚠️ Erro ao extrair tags: {e}")
            return []
        
    def translate_news(self, storage):
        """Traduz notícias para português e atualiza no Supabase."""
        
        for news in storage.get_all_news():
            if not news.get("translated_content"):  # Evita retraduzir notícias já traduzidas
                print(f"🌎 Traduzindo: {news['title']}...")

                translated_title = self.translate_text(news["title"])
                translated_content = self.translate_text(news["content"])
                tags = self.extract_tags(translated_content)
                news["translated_title"] = translated_title
                news["translated_content"] = translated_content
                news["tags"] = tags


                # Atualiza no Supabase
                storage.update_translated_news_db(news["title"], translated_title, translated_content, tags)


# 📌 Exemplo de uso
if __name__ == "__main__":
    gemini = GeminiUtils()
