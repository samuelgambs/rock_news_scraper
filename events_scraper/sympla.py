import requests
from bs4 import BeautifulSoup
import os
import re
import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar credenciais do Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectar ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL base do Sympla (Eventos de Rock em BH)
BASE_URL = "https://www.sympla.com.br/eventos/belo-horizonte-mg?s=rock&page={}"

# Headers para evitar bloqueios
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Mapeamento de meses para conversão
MESES = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12"
}

def formatar_data(data_texto):
    """Converte a data do formato 'Sábado, 12 de Abr às 12:00' para 'YYYY-MM-DD HH:MM'"""
    try:
        padrao = r"(\d{1,2}) de (\w+) às (\d{2}:\d{2})"
        match = re.search(padrao, data_texto)

        if match:
            dia, mes, hora = match.groups()
            mes_num = MESES.get(mes, "00")  # Converte para número
            ano_atual = datetime.datetime.now().year  # Assume o ano atual
            data_formatada = f"{ano_atual}-{mes_num}-{dia.zfill(2)} {hora}"
            return data_formatada
    except Exception as e:
        print(f"❌ Erro ao converter data: {data_texto} -> {e}")

    return None

def scrape_event_address(event_url):
    """Acessa a página do evento para extrair o endereço"""
    print(f"📄 Acessando detalhes do evento: {event_url}")

    try:
        response = requests.get(event_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a página do evento: {response.status_code}")
            return None, None, "Desconhecido", "Desconhecido"

        soup = BeautifulSoup(response.text, "html.parser")
        local_block = soup.find("h3", id="event-location")

        if local_block:
            endereco_container = local_block.find_next("div")  
            if endereco_container:
                nome_local = endereco_container.find("h4").text.strip()
                endereco_partes = endereco_container.find_all("p")
                endereco_completo = ", ".join([p.text.strip() for p in endereco_partes])

                cidade = "Desconhecido"
                estado = "Desconhecido"

                for p in endereco_partes:
                    if "," in p.text:
                        cidade_estado = p.text.strip().rsplit(",", 1)
                        if len(cidade_estado) == 2:
                            cidade = cidade_estado[0].strip()
                            estado = cidade_estado[1].strip()

                # Caso o estado esteja vazio, definir um valor padrão
                if not estado or estado == "Desconhecido":
                    estado = "MG"  # Assume MG para eventos de BH

                print(f"📍 Endereço encontrado: {nome_local} - {endereco_completo} ({cidade}, {estado})")
                return nome_local, endereco_completo, cidade, estado

        print("⚠️ Endereço não encontrado na página do evento.")
        return None, None, "Desconhecido", "Desconhecido"

    except Exception as e:
        print(f"⚠️ Erro ao acessar detalhes do evento: {e}")
        return None, None, "Desconhecido", "Desconhecido"

def scrape_sympla_events(max_pages=5):
    """Faz scraping de eventos do Sympla paginando automaticamente"""
    eventos = []
    page = 1  

    while True:
        url = BASE_URL.format(page)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erro ao acessar a página {page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        event_cards = soup.find_all("a", class_="sympla-card")

        if not event_cards:
            print(f"🚫 Nenhum evento encontrado na página {page}, finalizando scraping.")
            break

        print(f"📄 Extraindo eventos da página {page}...")

        for event in event_cards:
            try:
                title = event.get("data-name").strip()
                link = event.get("href")

                if not link.startswith("https"):
                    link = f"https://www.sympla.com.br{link}"

                image = event.find("img")["src"]
                date = event.find("div", class_="qtfy413").text.strip()
                data_formatada = formatar_data(date)

                # Verificar se já está salvo no Supabase
                existe = supabase.table("eventos_rock").select("id", "endereco").eq("link", link).execute()

                if existe.data:
                    print(f"⚠️ Evento já cadastrado: {title}, verificando atualização de endereço...")

                    evento_id = existe.data[0]["id"]
                    endereco_atual = existe.data[0].get("endereco", None)

                    if not endereco_atual:
                        local, endereco, cidade, estado = scrape_event_address(link)
                        if endereco:
                            supabase.table("eventos_rock").update({
                                "endereco": endereco, 
                                "cidade": cidade,
                                "estado": estado,
                                "data_formatada": data_formatada
                            }).eq("id", evento_id).execute()
                            print(f"✅ Endereço atualizado para: {title}")
                    continue

                # Buscar endereço antes de salvar
                local, endereco, cidade, estado = scrape_event_address(link)

                evento = {
                    "titulo": title,
                    "data": date,
                    "data_formatada": data_formatada,
                    "cidade": cidade,
                    "estado": estado,  # Agora sempre terá um valor válido
                    "imagem": image,
                    "link": link,
                    "endereco": endereco if endereco else "Endereço não disponível"
                }

                eventos.append(evento)

            except AttributeError:
                continue

        page += 1
        if page > max_pages:
            print(f"🔄 Parando na página {max_pages} para evitar sobrecarga.")
            break

    return eventos

def salvar_eventos_supabase(eventos):
    """Salva eventos no Supabase, evitando duplicatas"""
    for evento in eventos:
        try:
            # Verifica se o evento já existe no banco pelo link
            existe = supabase.table("eventos_rock").select("id").eq("link", evento["link"]).execute()

            if existe.data:
                print(f"⚠️ Evento já cadastrado: {evento['titulo']}, verificando atualização de endereço...")

                evento_id = existe.data[0]["id"]
                endereco_atual = existe.data[0].get("endereco", None)

                if not endereco_atual and evento["endereco"]:
                    supabase.table("eventos_rock").update({
                        "endereco": evento["endereco"],
                        "cidade": evento["cidade"],
                        "estado": evento["estado"],
                        "data_formatada": evento["data_formatada"]
                    }).eq("id", evento_id).execute()
                    print(f"✅ Endereço atualizado para: {evento['titulo']}")
                continue
            
            supabase.table("eventos_rock").insert(evento).execute()
            print(f"✅ Evento salvo: {evento['titulo']}")

        except Exception as e:
            print(f"❌ Erro ao salvar evento {evento['titulo']}: {e}")

# Executa o scraper e salva no Supabase
eventos_encontrados = scrape_sympla_events()
salvar_eventos_supabase(eventos_encontrados)
