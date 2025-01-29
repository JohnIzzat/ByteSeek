import requests
from bs4 import BeautifulSoup
import re

### REALIZANDO SOMENTE A RASPAGEM NÃO ESTÁ PERCORRENDO POR TODA A PAGINA

# Função para realizar a busca no DuckDuckGo e extrair links e dados dos snippets


def search_and_scrape(query):
    base_url = "https://duckduckgo.com/html/"
    params = {"q": query}  # Query de busca
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Fazendo a requisição
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        print("Erro ao acessar o mecanismo de busca")
        return None

    # Analisa o HTML retornado
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # Procura os resultados de busca
    for result in soup.find_all("div", class_="result"):
        link = result.find("a", href=True)["href"] if result.find(
            "a", href=True) else None
        snippet = result.get_text()

        # Busca por e-mails e telefones nos snippets
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", snippet)
        phones = re.findall(r"\(?\d{2}\)?\s?\d{4,5}-\d{4}", snippet)

        # Adiciona os dados encontrados
        results.append({
            "link": link,
            "emails": emails,
            "phones": phones,
            "snippet": snippet.strip()
        })

    return results


# Busca inicial
query = 'site:instagram.com "roupas" ("@gmail.com" OR "@hotmail.com") ("(11)" OR "+55")'
results = search_and_scrape(query)

# Exibe os resultados
if results:
    print("Resultados encontrados:")
    for idx, result in enumerate(results):
        print(f"\nResultado {idx + 1}:")
        print(f"Link: {result['link']}")
        print(
            f"E-mails: {', '.join(result['emails']) if result['emails'] else 'Nenhum'}")
        print(f"Telefones: {', '.join(
            result['phones']) if result['phones'] else 'Nenhum'}")
        print(f"Snippet: {result['snippet']}")
else:
    print("Nenhum resultado encontrado.")
