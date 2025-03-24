import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client
from datetime import datetime

# 🔹 Carregar credenciais do Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔹 Conectar ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔹 URL do Ticket360 para eventos de Rock
TICKET360_URL = "https://www.ticket360.com.br/eventos/pesquisar?s=rock"

# 🔹 Configuração do Selenium
options = Options()
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # Roda em background

# 🔹 Mapeamento de meses para conversão correta
MESES = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12",
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
    "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12",
}

def iniciar_driver():
    """Inicia o WebDriver do Selenium"""
    print("🚀 Iniciando WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_ticket360_events():
    """Scrapea eventos de rock do Ticket360"""
    eventos = []
    driver = iniciar_driver()

    print(f"📄 Acessando URL: {TICKET360_URL}")
    driver.get(TICKET360_URL)

    # Esperar a página carregar completamente
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m-portlet"))
        )
    except Exception as e:
        print(f"❌ Timeout ao carregar a página principal: {e}")
        driver.quit()
        return eventos

    # Scroll para carregar todos os eventos
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 800);")
        WebDriverWait(driver, 2)

    # Encontrar todos os eventos
    event_cards = driver.find_elements(By.CLASS_NAME, "m-portlet")

    if not event_cards:
        print("🚫 Nenhum evento encontrado, finalizando scraping.")
        driver.quit()
        return eventos

    print(f"📄 {len(event_cards)} eventos encontrados!")

    for event in event_cards:
        try:
            title = event.find_element(By.CLASS_NAME, "card-name-evento").text.strip()
            link_tag = event.find_element(By.TAG_NAME, "a")
            link = link_tag.get_attribute("href") if link_tag else None

            if not link or not link.startswith("https://www.ticket360.com.br"):
                print(f"⚠️ Link inválido encontrado: {link}")
                continue

            print(f"🔍 Extraindo evento: {title}")

            # 📌 **Extração correta da data**
            mes_texto = event.find_element(By.CLASS_NAME, "data-mes").text.strip()
            dia = event.find_element(By.CLASS_NAME, "data-layer").text.strip()

            # Normalizar o texto do mês para corresponder às chaves do dicionário
            mes_texto_normalizado = mes_texto.upper()

            # 📌 **Correção do erro do mês**
            mes = MESES.get(mes_texto_normalizado, None)
            if not mes:
                print(f"⚠️ Mês desconhecido: {mes_texto}. Definindo data como None.")
                data_formatada = None
                data_completa = "Data desconhecida"
            else:
                horario = extrair_horario_evento(link)
                data_completa = f"{dia} de {mes_texto} às {horario}"
                # Definindo o ano como 2025 diretamente
                data_formatada = f"2025-{mes}-{dia.zfill(2)} {horario}"

            # 📌 **Busca de endereço e imagem correta na página do evento**
            endereco, cidade, estado, imagem = scrape_event_details(link)

            evento = {
                "titulo": title,
                "data": data_completa,
                "data_formatada": data_formatada,
                "cidade": cidade,
                "estado": estado,
                "imagem": imagem,
                "link": link,
                "endereco": endereco if endereco else "Endereço não disponível"
            }

            # Imprimir as informações coletadas
            print("\n--- Informações Coletadas ---")
            for key, value in evento.items():
                print(f"{key}: {value}")
            print("---------------------------\n")

            eventos.append(evento)

        except Exception as e:
            print(f"⚠️ Erro ao extrair evento: {e}")
            continue

    driver.quit()  # Fecha o navegador
    return eventos

def extrair_horario_evento(event_url):
    """Acessa a página do evento e extrai o horário corretamente"""
    try:
        response = requests.get(event_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a página do evento: {response.status_code}")
            return "00:00"

        soup = BeautifulSoup(response.text, "html.parser")

        # Busca por qualquer horário disponível dentro da div com a classe info-detail
        horario_texto = "00:00"
        info_detail_div = soup.find("div", class_="info-detail")
        if info_detail_div:
            horario_paragraph = info_detail_div.find("p")
            if horario_paragraph:
                matches = re.search(r"Abertura:\s*(\d{2}:\d{2})\s*(?:-\s*Início:\s*(\d{2}:\d{2}))?", horario_paragraph.text)
                if matches:
                    horario_texto = matches.group(1)
                else:
                    matches = re.search(r"Início:\s*(\d{2}:\d{2})", horario_paragraph.text)
                    if matches:
                        horario_texto = matches.group(1)

        return horario_texto

    except Exception as e:
        print(f"⚠️ Erro ao acessar detalhes do horário: {e}")
        return "00:00"
    
    
import requests
from bs4 import BeautifulSoup
import re

def parece_endereco(texto):
    """Heurística para identificar se o texto parece conter endereço"""
    palavras_chave = ["Rua", "Av.", "Praça", "Rodovia", "São Paulo", "MG", "SP", "CEP", "Bloco", "Barra Funda", "Água Branca"]
    return any(palavra.lower() in texto.lower() for palavra in palavras_chave)

def scrape_event_details(event_url):
    """Extrai detalhes como endereço, cidade, estado e imagem"""

    try:
        response = requests.get(event_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None, None, None, None

        soup = BeautifulSoup(response.text, "html.parser")

        endereco = "Endereço não informado"
        cidade = "Desconhecido"
        estado = "Desconhecido"

        # Buscar todos os blocos possíveis contendo o local
        all_info_rows = soup.find_all("div", class_="row m--padding-bottom-10")
        for row in all_info_rows:
            address_col = row.find("div", class_=lambda value: value and "col-10" in value)
            if address_col:
                lines = [text.strip() for text in address_col.stripped_strings]
                texto_completo = " ".join(lines)
                texto_completo = re.sub(r'\s+', ' ', texto_completo).strip()  # Limpa espaços e quebras

                if parece_endereco(texto_completo):
                    endereco = texto_completo

                    # Tentando extrair cidade e estado pelo hífen
                    parts = endereco.split('-')
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) >= 3:
                        cidade = parts[-2]
                        estado = parts[-1]
                    break  # Achou um bloco válido, para

        # Extração da imagem
        imagem_block = soup.find("img", class_="img-fluid")
        imagem = imagem_block["src"] if imagem_block else "Sem imagem"

        return endereco, cidade, estado, imagem

    except Exception as e:
        print(f"⚠️ Erro ao acessar detalhes do evento: {e}")
        return "Endereço Erro", "Cidade Erro", "Estado Erro", None


def salvar_eventos_supabase(eventos):
    """Salva eventos no Supabase, evitando duplicatas e atualizando informações."""
    for evento in eventos:
        try:
            resultado = supabase.table("eventos_rock").select("id", "endereco").eq("link", evento["link"]).execute()

            if resultado.data:
                print(f"⚠️ Evento já cadastrado: {evento['titulo']}")
                continue

            supabase.table("eventos_rock").insert(evento).execute()
            print(f"✅ Evento salvo: {evento['titulo']}")

        except Exception as e:
            print(f"❌ Erro ao salvar evento {evento['titulo']}: {e}")

# Executa o scraper e salva no Supabase
eventos_ticket360 = scrape_ticket360_events()
salvar_eventos_supabase(eventos_ticket360)