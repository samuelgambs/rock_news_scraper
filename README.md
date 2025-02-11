# 🎸 Rock News Scraper 🎸
## 📋 **Índice**
1. [Funcionalidades](#-funcionalidades)
2. [Configuração do Projeto](#️-configuração-do-projeto)
3. [Como Usar](#-como-usar)
4. [Estrutura do Projeto](#-estrutura-do-projeto)
5. [Próximos Passos](#-próximos-passos)
6. [Contribuições](#-contribuições)

---

## 🚀 **Funcionalidades**
✅ **Coleta automática** de notícias de sites renomados do rock/metal.  
✅ **Suporte a múltiplas fontes**: Blabbermouth, Loudwire, Metal Injection, MetalSucks, BraveWords, MetalTalk, Metal Hammer.  
✅ **Armazenamento em JSON** para fácil manipulação.  
✅ **Processamento de texto com NLP** (Named Entity Recognition) usando **spaCy e Hugging Face Transformers**.  
✅ **Extração de imagens e vídeos das matérias**.  
✅ **Integração com Google Cloud Platform** (Cloud Functions e Cloud Scheduler).  

---

## 🛠️ **Configuração do Projeto**
### **1️⃣ Clone o repositório**
```bash
git clone https://github.com/seu-usuario/rock-news-scraper.git
cd rock-news-scraper
```

### **2️⃣ Crie um ambiente virtual e instale as dependências**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### **3️⃣ Baixe o modelo do spaCy**
```bash
python -m spacy download en_core_web_sm
```

---

## 🎯 **Como Usar**
### **Executar o scraper manualmente**
```bash
python main.py
```

### **Rodar o processamento de NLP**
```bash
python -m src.utils.ner_extractor
```

---

## 📁 **Estrutura do Projeto**
```plaintext
rock-news-scraper/
│── src/
│   ├── scrapers/               # Scripts de scraping por site
│   │   ├── blabbermouth_scraper.py
│   │   ├── loudwire_scraper.py
│   │   ├── metalinjection_scraper.py
│   │   ├── ...
│   ├── utils/
│   │   ├── news_storage.py      # Gerencia o armazenamento das notícias
│   │   ├── ner_extractor.py     # Extração de entidades nomeadas (NLP)
│   ├── main.py                  # Arquivo principal
│── requirements.txt              # Dependências do projeto
│── .gitignore                    # Arquivos a serem ignorados no Git
│── README.md                     # Documentação do projeto
│── news_storage.json              # Arquivo JSON que armazena as notícias coletadas
```

---

## 🧠 **Próximos Passos**
- Melhorar a precisão do Named Entity Recognition (NER).
- Implementar tradução automática de notícias para PT-BR.
- Criar uma API para expor os dados coletados.
- Criar uma interface web para visualizar as notícias.

---

## 🏆 **Contribuições**
Quer contribuir? Faça um fork do projeto e envie um PR! 🤘
![Python](https://img.shields.io/badge/Python-3.10-blue) ![Web Scraping](https://img.shields.io/badge/Web%20Scraping-BeautifulSoup%20%7C%20Selenium-orange) ![GCP](https://img.shields.io/badge/Cloud-GCP-yellow)

