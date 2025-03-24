import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# Carrega as credenciais do Supabase do .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectar ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL do Eventim para eventos de Rock em Belo Horizonte
URL = "https://www.eventim.com.br/search/?affiliate=BR1&searchterm=rock&cityNames=Belo+Horizonte"

# Configuração do Selenium
options = Options()
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

def iniciar_driver():
    """Inicia o WebDriver do Selenium"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def aceitar_cookies(driver):
    """Tenta fechar o banner de cookies do Eventim"""
    try:
        time.sleep(2)
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar todos os cookies')]"))
        )
        cookie_button.click()
        print("🍪 Cookies aceitos!")
    except:
        print("⚠️ Nenhum banner de cookies encontrado (ou já aceito).")

def scrape_eventim_events():
    """Scrapea eventos de rock do Eventim sem paginação"""
    eventos = []
    driver = iniciar_driver()
    
    print(f"📄 Acessando URL: {URL}")
    driver.get(URL)

    time.sleep(5)
    aceitar_cookies(driver)

    # Scroll para carregar todos os eventos
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "product-item"))
        )
    except:
        print("❌ Timeout: Nenhum evento foi carregado.")
        driver.quit()
        return eventos

    event_cards = driver.find_elements(By.TAG_NAME, "product-item")

    if not event_cards:
        print("🚫 Nenhum evento encontrado, finalizando scraping.")
        driver.quit()
        return eventos

    print(f"📄 Extraindo {len(event_cards)} eventos...")

    for index, event in enumerate(event_cards):
        try:
            # Extrair título do evento
            title_tag = event.find_element(By.XPATH, ".//span[contains(@class, 'u-font-weight-bold')]")
            title = title_tag.text.strip() if title_tag else "Título desconhecido"

            # Extrair link do evento
            link_tag = event.find_element(By.XPATH, ".//a[contains(@class, 'btn link')]")
            link = f"https://www.eventim.com.br{link_tag.get_attribute('href')}" if link_tag else "Sem link"

            # Extrair imagem do evento
            try:
                image_tag = event.find_element(By.XPATH, ".//img")
                image = image_tag.get_attribute("src")
            except:
                image = "Sem imagem"

            # Extrair cidade e data
            location_tag = event.find_element(By.XPATH, ".//span[contains(@class, 'u-text-color theme-text-color')]")
            location_text = location_tag.text.strip() if location_tag else "Localização desconhecida"
            cidade, estado, data = extrair_cidade_estado_data(location_text)

            evento = {
                "titulo": title,
                "data": data,
                "cidade": cidade,
                "estado": estado,
                "imagem": image,
                "link": link
            }

            # ✅ Agora clicamos no evento para obter o endereço
            event.click()
            time.sleep(3)

            # ✅ Coletar o endereço do local dentro da página de detalhes
            try:
                address_tag = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'listing-subheadline')]"))
                )
                endereco = address_tag.text.strip()
            except:
                endereco = "Endereço não disponível"

            # ✅ Voltar para a lista de eventos
            driver.back()
            time.sleep(3)

            evento["endereco"] = endereco  # ✅ Salvamos o endereço aqui
            eventos.append(evento)

        except Exception as e:
            print(f"⚠️ Erro ao extrair evento {index + 1}: {e}")
            continue

    driver.quit()
    return eventos

def extrair_cidade_estado_data(localizacao):
    """Separa cidade, estado e data de uma string no formato 'Cidade, data'"""
    partes = localizacao.split(", ")
    if len(partes) >= 2:
        cidade = partes[0]
        data = partes[1]
        estado = "MG"  # Eventim não mostra estado diretamente, assumimos que é MG
        return cidade, estado, data
    return "Desconhecido", "Desconhecido", "Desconhecida"

def salvar_eventos_supabase(eventos):
    """Salva ou atualiza eventos no Supabase"""
    for evento in eventos:
        try:
            # Verifica se o evento já existe no banco pelo link
            existe = supabase.table("eventos_rock").select("id", "endereco").eq("link", evento["link"]).execute()

            if existe.data:
                evento_id = existe.data[0]["id"]
                endereco_existente = existe.data[0]["endereco"]

                if not endereco_existente or endereco_existente == "Endereço não disponível":
                    # Se o evento já existe mas sem endereço, atualiza o endereço
                    supabase.table("eventos_rock").update({"endereco": evento["endereco"]}).eq("id", evento_id).execute()
                    print(f"✅ Endereço atualizado para: {evento['titulo']}")
                else:
                    print(f"⚠️ Evento já cadastrado e endereço já salvo: {evento['titulo']}")
            else:
                # Insere o novo evento
                supabase.table("eventos_rock").insert(evento).execute()
                print(f"✅ Novo evento salvo: {evento['titulo']}")

        except Exception as e:
            print(f"❌ Erro ao salvar evento {evento['titulo']}: {e}")

# Executando o scraper e salvando os eventos no Supabase
eventos_eventim = scrape_eventim_events()
salvar_eventos_supabase(eventos_eventim)
