# Usa uma imagem Python oficial
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Entra na pasta rock_news_scraper
WORKDIR /app/rock_news_scraper
CMD ["python", "main.py"]
