import torch
from transformers import MarianMTModel, MarianTokenizer

class Translator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-tc-big-en-pt"):
        """Inicializa o tradutor com o modelo escolhido"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name).to(self.device)

    def translate_text(self, text):
        """Traduz um texto do inglês para o português"""
        if not text.strip():
            return ""

        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            translated = self.model.generate(**inputs)

        return self.tokenizer.decode(translated[0], skip_special_tokens=True)

def translate_news(storage):
    """Traduz notícias para português e atualiza o JSON sem duplicar"""
    translator = Translator()
    
    for news in storage.get_all_news():
        if "translated_content" not in news:  # Evita traduzir duplicado
            print(f"🌎 Traduzindo: {news['title']}...")
            translated_text = translator.translate_text(news["content"])
            news["translated_content"] = translated_text
            print(f"✅ Tradução concluída para: {news['title']}!")

    # Salva apenas no final
    storage.save_news(storage.get_all_news())
