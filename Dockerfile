# Usa uma imagem Python oficial
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta exigida pelo Cloud Run
EXPOSE 8080

# Entra na pasta rock_news_scraper
WORKDIR /app/rock_news_scraper
# Comando para rodar o servidor FastAPI
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
