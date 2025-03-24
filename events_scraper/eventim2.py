import os
import asyncio
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://www.eventim.com.br/search/?affiliate=BR1&searchterm=rock&page={page}"

llm = ChatOpenAI(model='gpt-4o')

def extrair_json_bruto(result_list):
    """Extrai o JSON puro da lista retornada pelo Agent"""
    for item in result_list:
        if "Extracted from page" in item:
            match = re.search(r'```.*?\n(.*?)```', item, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json_str
    return None

def converter_para_timestamp(data_str):
    """Converte data dd/mm/yyyy para timestamp"""
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return dt.isoformat()
    except:
        return None

def corrigir_link(link):
    """Corrige links incompletos"""
    if isinstance(link, str):
        if link.startswith("/event/"):
            return f"https://www.eventim.com.br{link}"
        return link
    return ""

async def processar_pagina(page):
    url = BASE_URL.format(page=page)
    print(f"🚀 Processando página {page}: {url}")

    TASK = f"""
    Go to {url},
    accept cookies if needed, scroll down to load all events, and extract a list of events including:
    - Title
    - Date(s)
    - City
    - Venue
    - Link
    - Time
    - Image URL (collect the image displayed in the event card)

    Some events might have multiple dates, include all of them.

    Return the result in JSON format, with keys:
    - title
    - dates (list of strings, list of dicts, or string depending on availability)
    - city
    - venue
    - link
    - time
    - image_url
    """
    agent = Agent(task=TASK, llm=llm)
    result = await agent.run(max_steps=25)

    extracted = result.extracted_content()
    json_str = extrair_json_bruto(extracted)

    if not json_str:
        print(f"❌ Não foi possível extrair JSON da página {page}.")
        return []

    # Salvar JSON bruto local para backup
    try:
        with open(f'backup_eventim_page_{page}.json', 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"📁 Backup salvo: backup_eventim_page_{page}.json")
    except Exception as e:
        print(f"❌ Erro ao salvar backup página {page}: {e}")

    try:
        events_json = json.loads(json_str)
        events = events_json.get("events", [])
        print(f"✅ Página {page}: {len(events)} eventos extraídos!")
        return events
    except Exception as e:
        print(f"❌ Erro ao processar JSON da página {page}: {e}")
        return []

async def salvar_eventos(events):
    for event in events:
        title = event["title"]

        # Normalizando dates:
        if "dates" in event:
            if isinstance(event["dates"], str):
                dates_list = [{"date": event["dates"]}]
            elif isinstance(event["dates"], list):
                # Pode ser lista de strings OU lista de dicts
                if isinstance(event["dates"][0], dict):
                    dates_list = event["dates"]
                else:
                    dates_list = [{"date": d} for d in event["dates"]]
            else:
                dates_list = []
        elif "date" in event:
            dates_list = [{"date": event["date"]}]
        else:
            dates_list = []

        for idx, date_info in enumerate(dates_list):
            date_str = date_info["date"] if isinstance(date_info, dict) else date_info
            cidade = date_info.get("city", event.get("city", ""))
            venue = date_info.get("venue", event.get("venue", ""))
            link = date_info.get("link", event.get("link", ""))
            time = date_info.get("time", event.get("time", ""))

            # Corrigir link incompleto
            link_corrigido = corrigir_link(link)

            data_formatada = converter_para_timestamp(date_str)

            new_event = {
                "titulo": title,
                "data": date_str,
                "data_formatada": data_formatada,
                "cidade": cidade,
                "estado": "Brasil",
                "imagem": event.get("image_url", ""),
                "link": link_corrigido,
                "endereco": venue
                # campo hora removido
            }

            try:
                existe = supabase.table("eventos_rock").select("id").eq("link", new_event["link"]).execute()
                if existe.data:
                    print(f"⚠️ Evento já cadastrado: {title} ({new_event['data']})")
                else:
                    supabase.table("eventos_rock").insert(new_event).execute()
                    print(f"✅ Evento salvo: {title} ({new_event['data']})")
            except Exception as e:
                print(f"❌ Erro ao salvar evento {title}: {e}")

async def main():
    all_events = []
    for page in range(1, 4):
        events = await processar_pagina(page)
        all_events.extend(events)

    print(f"🎯 Total de eventos extraídos: {len(all_events)}")
    await salvar_eventos(all_events)

if __name__ == "__main__":
    asyncio.run(main())
