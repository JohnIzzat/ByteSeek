from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import re
import csv


def executar_busca(rede_social, nicho, email, telefone):
    # Monta a query com base nas seleções
    #query = f'site:{rede_social}.com "{nicho}" ("{email}") ("{telefone}")'
    query = (
        f"site:{rede_social.lower()}.com \"{nicho}\" "
        f"({email}) (\"({telefone})\" OR \"+55\")"
    )
    results = search_and_scrape(query, max_pages=5)
    save_to_csv(results)
    return results


def search_and_scrape(query, max_pages=5):
    # Configuração do WebDriver
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Modo headless (invisível
    # Alternativa: para iniciar minimizado ao invés de headless
    # chrome_options.add_argument('--start-minimized')
    chrome_options.add_argument('--disable-dev-shm-usage') # Melhora estabilidade

    #chrome_options.add_argument('--disable-gpu')  # Desativa aceleração GPU
    #chrome_options.add_argument('--no-sandbox')  # Útil para ambientes Linux

    driver = webdriver.Chrome(options=chrome_options)  # Substitua por outro driver se necessário
    driver.get("https://duckduckgo.com/")  # Acessa o DuckDuckGo
    results = []

    try:
        # Localiza a barra de pesquisa e insere a query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Aguarda a página carregar resultados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )

        current_page = 1
        while current_page <= max_pages:
            print(f"Buscando página {current_page}...")

            # Aguarda os resultados carregarem
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "article"))
                )
            except TimeoutException:
                print("Timeout ao carregar os resultados.")
                break

            # Raspagem dos resultados
            page_results = 0
            results_containers = driver.find_elements(
                By.CSS_SELECTOR, "article")
            for container in results_containers:
                try:
                    # Extração dos dados específicos do seletor
                    link_element = container.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute(
                        "href") if link_element else None
                    snippet = container.text.strip()

                    # Busca por e-mails e telefones nos snippets
                    emails = re.findall(
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", snippet
                    )
                    phones = re.findall(
                        r"\(?\d{2}\)?\s?\d{4,5}-\d{4}", snippet
                    )

                    if link or emails or phones:
                        # Adiciona os dados encontrados
                        results.append({
                            "link": link,
                            "emails": emails,
                            "phones": phones,
                            "snippet": snippet
                        })
                        page_results += 1

                    # Delay randômico entre raspagens
                    time.sleep(random.uniform(1.5, 3.0))
                except Exception as e:
                    print(f"Erro ao processar resultado: {e}")

            print(f"Resultados encontrados nesta página: {page_results}")

            # Verifica se há o botão "Mais resultados" para carregar mais dados
            try:
                next_page_button = driver.find_element(By.ID, "more-results")
                next_page_button.click()

                # Aguarda os novos resultados carregarem
                time.sleep(5)
                current_page += 1
            except NoSuchElementException:
                print(
                    "Botão 'Mais resultados' não encontrado ou não há mais resultados.")
                break

    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        # Fecha o navegador
        driver.quit()

    return results


def save_to_csv(results, filename="resultados.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for idx, result in enumerate(results):
            # Formatação de cada resultado no estilo solicitado
            writer.writerow([
                f"Resultado {idx + 1}:",
                f"E-mails: {', '.join(result['emails'])
                            if result['emails'] else 'Nenhum'}",
                f"Telefones: {
                    ', '.join(result['phones']) if result['phones'] else 'Nenhum'}",
                f"Snippet: {result['snippet']}",
                result['link']
            ])


# Busca inicial
# query = 'site:instagram.com "roupas" ("@gmail.com" OR "@hotmail.com") ("(11)" OR "+55")'
# results = search_and_scrape(query, max_pages=5)

# # Exibe e salva os resultados
# if results:
#     print("Resultados encontrados:")
#     for idx, result in enumerate(results):
#         print(f"\nResultado {idx + 1}:")
#         print(
#             f"E-mails: {', '.join(result['emails']) if result['emails'] else 'Nenhum'}")
#         print(f"Telefones: {', '.join(
#             result['phones']) if result['phones'] else 'Nenhum'}")
#         print(f"Snippet: {result['snippet']}")
#         print(f"Link: {result['link']}")
#     # Salva no CSV
#     save_to_csv(results)
#     print("\nResultados salvos no arquivo 'resultados.csv'.")
# else:
#     print("Nenhum resultado encontrado.")

if __name__ == "__main__":
    print("Back-end iniciado. Aguardando chamadas do front-end.")
