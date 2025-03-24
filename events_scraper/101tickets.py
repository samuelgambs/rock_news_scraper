import requests

# Substitua com sua chave de API do Google
API_KEY = 'AIzaSyAJWr4DhQuC_4lvtftRlBiHfaUFJEEMtWs'
CX = '14118c0f0da0e4c95'  # O ID do mecanismo de pesquisa customizado

def search_google_custom(query):
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}'
    response = requests.get(url)
    results = response.json()
    links = []
    
    # Extraindo os links dos resultados
    for item in results.get('items', []):
        links.append(item['link'])
    
    return links

# Exemplo de busca
search_results = search_google_custom("101 tickets site:101tickets.com.br")
print(search_results)
