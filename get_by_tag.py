import requests
from requests.auth import HTTPBasicAuth

# Configuração da API WooCommerce
base_url = "https://o18.277.myftpupload.com/wp-json/wc/v3/products"
tags_url = "https://o18.277.myftpupload.com/wp-json/wc/v3/products/tags"
consumer_key = "ck_2f74125c5bff04e207c08bdfbbc08cafec85af3c"
consumer_secret = "cs_c7f5c1f03323c2e4bdc0c3d569fc45ad731bb220"

# Definir a tag a ser filtrada (Substitua pelo nome da tag)
tag_name = "Judas Priest"

# Obter a lista de todas as tags e mapear os nomes para seus IDs
def get_tag_id(tag_name):
    response = requests.get(tags_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    if response.status_code == 200:
        tags = response.json()
        tag_map = {tag['name'].lower(): tag['id'] for tag in tags}
        return tag_map.get(tag_name.lower())
    else:
        print(f"Erro ao obter tags: {response.status_code}")
        return None

tag_id = get_tag_id(tag_name)

if tag_id:
    # Faz a requisição GET para obter produtos filtrados pela tag
    params = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "tag": tag_id,  # Filtra por tag específica
        "per_page": 5  # Número de produtos a exibir
    }

    # Verificar se a tag está sendo passada corretamente
    print(f"URL da requisição: {base_url}?tag={tag_id}&per_page=5")

    response = requests.get(base_url, params=params, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # Verifica se a resposta foi bem-sucedida
    if response.status_code == 200:
        products = response.json()
        
        # Exibir os produtos encontrados
        for product in products:
            print(f"Nome: {product['name']}")
            print(f"Preço: {product['price']}")
            print(f"Link: {product['permalink']}")
            print(f"Imagem: {product['images'][0]['src']}" if product['images'] else "Sem imagem")
            print("=" * 40)
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)  # Exibe a mensagem de erro caso haja problemas
else:
    print(f"Tag '{tag_name}' não encontrada.")
