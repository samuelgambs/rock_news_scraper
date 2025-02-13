import streamlit as st
import pandas as pd
import json
from urllib.parse import urlparse

# Caminho do arquivo JSON
NEWS_STORAGE_FILE = "news_storage.json"

# Função para carregar notícias
def load_news():
    try:
        with open(NEWS_STORAGE_FILE, "r", encoding="utf-8") as file:
            news = json.load(file)
            return news
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Função para extrair a fonte a partir do link
def extract_source_from_url(url):
    """Extrai o nome do site a partir do link."""
    domain = urlparse(url).netloc
    domain = domain.replace("www.", "")  # Remove o 'www.' se existir
    return domain.split(".")[0].capitalize()  # Usa o primeiro nível do domínio como nome da fonte

# Função para extrair entidades como tags
def extract_entities(entities):
    """Extrai apenas os nomes das entidades do JSON e retorna como lista."""
    return [entity[0] for entity in entities] if entities else []

# Carregar dados
news_data = load_news()

st.title("📰 Portal de Notícias de Rock 🤘")
st.subheader("Acompanhe as últimas matérias coletadas e publicadas")

if news_data:
    # Criar DataFrame e adicionar a coluna 'source' dinamicamente
    df = pd.DataFrame(news_data)

    # Se a coluna "source" não existir, cria ela com base no link
    if "source" not in df.columns:
        df["source"] = df["link"].apply(lambda x: extract_source_from_url(x) if pd.notna(x) else "Desconhecido")

    # Criar o filtro de sites
    site_filter = st.selectbox("Filtrar por site", ["Todos"] + list(df["source"].unique()))

    # Aplicar filtro se necessário
    if site_filter != "Todos":
        df = df[df["source"] == site_filter]

    # Exibir notícias
    for _, row in df.iterrows():
        st.subheader(row.get("title", "Título não encontrado"))
        st.write(f"📅 {row.get('date', 'Data indisponível')} | 🏷️ Tags: {', '.join(extract_entities(row.get('entities', [])))}")
        st.write(row.get("translated_content", row.get("content", "Conteúdo indisponível")))

        if row.get("image_url"):
            st.image(row["image_url"], caption=row["title"], use_column_width=True)

        if row.get("video_urls"):
            for video in row["video_urls"]:
                st.video(video)

        st.markdown("---")  # Linha divisória entre notícias
else:
    st.warning("Nenhuma notícia encontrada. Execute o scraper.")

