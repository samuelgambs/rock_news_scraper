import torch
from transformers import MarianMTModel, MarianTokenizer

class Translator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-tc-big-en-pt"):
        """Inicializa o tradutor com o modelo escolhido"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name).to(self.device)

    def translate_text(self, text, chunk_size=400):
        """Traduz um texto do inglês para o português, evitando truncamento"""
        if not text.strip():
            return ""

        # Divide o texto em partes menores para evitar truncamento
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        translated_chunks = []

        for chunk in text_chunks:
            inputs = self.tokenizer(chunk, return_tensors="pt", padding=True, truncation=False).to(self.device)
            with torch.no_grad():
                translated = self.model.generate(
                    **inputs,
                    max_length=512,  # Garante espaço suficiente para resposta completa
                    num_return_sequences=1,  # Apenas uma resposta
                    do_sample=False  # Evita aleatoriedade na tradução
                )
            translated_chunks.append(self.tokenizer.decode(translated[0], skip_special_tokens=True))

        return " ".join(translated_chunks)
    
def translate_news(storage):
    """Traduz notícias para português e atualiza o JSON sem duplicar"""
    translator = Translator()
    updated = False  # Flag para evitar salvamentos desnecessários
    
    for news in storage.get_all_news():
        # Verifica se já foi traduzido para evitar duplicação
        if "translated_content" not in news or not news["translated_content"]:
            print(f"🌎 Traduzindo título: {news['title']}...")
            translated_title = translator.translate_text(news["title"])
            print(f"✅ Título traduzido: {translated_title}")

            print(f"🌎 Traduzindo conteúdo: {news['title']}...")
            translated_text = translator.translate_text(news["content"])
            print(f"✅ Tradução concluída para: {news['title']}!")

            # Armazena as traduções
            news["translated_title"] = translated_title
            news["translated_content"] = translated_text
            updated = True  # Marca que houve alteração
            
            # Salvamento progressivo para evitar perdas
            storage.save_news(storage.get_all_news())

    # Salva novamente no final para garantir integridade
    if updated:
        storage.save_news(storage.get_all_news())
        print("✅ Todas as traduções foram salvas!")
    

# def translate_news(storage):
#     """Traduz notícias para português e atualiza o JSON sem duplicar"""
#     translator = Translator()
    
#     for news in storage.get_all_news():
#         if "translated_content" not in news or not news["translated_content"]:  # Evita traduzir duplicado
#             print(f"🌎 Traduzindo: {news['title']}...")
#             translated_text = translator.translate_text(news["content"])
#             news["translated_content"] = translated_text
#             print(f"✅ Tradução concluída para: {news['title']}!")

#     # Salva apenas no final
#     storage.save_news(storage.get_all_news())
