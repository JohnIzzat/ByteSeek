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


# def executar_busca(rede_social, nicho, email, telefone):
#     query = (
#         f"site:{rede_social.lower()}.com \"{nicho}\" "
#         f"({email}) (\"({telefone})\" OR \"+55\")"
#     )
#     results, driver = search_and_scrape(query, max_pages=5)
#     if results:
#         save_to_csv(results)
#     return results, driver  # Retorna os resultados e o driver

def executar_busca(rede_social, nicho, email, telefone):
    query = (
        f"site:{rede_social.lower()}.com \"{nicho}\" "
        f"({email}) (\"({telefone})\" OR \"+55\")"
    )
    results, driver = search_and_scrape(
        query, max_pages=5)
    if results:
        save_to_csv(results)
    return results, driver  # Retorna os resultados e o driver


def search_and_scrape(query, max_pages=5):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://duckduckgo.com/")
    results = []    

    try:
        
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )

        current_page = 1
        while current_page <= max_pages:
            print(f"Buscando página {current_page}...")

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "article"))
                )
            except TimeoutException:
                print("Timeout ao carregar os resultados.")
                break

            page_results = 0
            results_containers = driver.find_elements(
                By.CSS_SELECTOR, "article")

            for container in results_containers:
                try:
                    link_element = container.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute(
                        "href") if link_element else None
                    snippet = container.text.strip()

                    emails = re.findall(
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", snippet
                    )
                    phones = re.findall(
                        r"\(?\d{2}\)?\s?\d{4,5}-\d{4}", snippet
                    )

                    if link or emails or phones:
                        results.append({
                            "link": link,
                            "emails": emails,
                            "phones": phones,
                            "snippet": snippet
                        })
                        page_results += 1

                    time.sleep(random.uniform(1.5, 3.0))
                except Exception as e:
                    print(f"Erro ao processar resultado: {e}")

            print(f"Resultados encontrados nesta página: {page_results}")

            try:
                next_page_button = driver.find_element(By.ID, "more-results")
                next_page_button.click()
                time.sleep(5)
                current_page += 1
            except NoSuchElementException:
                print(
                    "Botão 'Mais resultados' não encontrado ou não há mais resultados.")
                break

        return results, driver  # Retorna os resultados e o driver
    except Exception as e:
        print(f"Erro geral: {e}")
        driver.quit()  # Fecha o driver em caso de erro
        return None, None

def save_to_csv(results, filename="resultados.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for idx, result in enumerate(results):
            writer.writerow([
                f"Resultado {idx + 1}:",
                f"E-mails: {', '.join(result['emails'])
                            if result['emails'] else 'Nenhum'}",
                f"Telefones: {
                    ', '.join(result['phones']) if result['phones'] else 'Nenhum'}",
                f"Snippet: {result['snippet']}",
                result['link']
            ])




if __name__ == "__main__":
    print("Back-end iniciado. Aguardando chamadas do front-end.")
