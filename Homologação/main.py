import logging
import time
import random
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do logging
logging.basicConfig(
    filename="app.log",             # Nome do arquivo onde os logs serão salvos
    # Define o nível dos logs (DEBUG registra tudo)
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato do log
    datefmt="%Y-%m-%d %H:%M:%S",     # Formato da data
)


def accept_cookies(driver):
    """
    Tenta localizar e clicar no botão de aceite de cookies com o texto "Aceitar".
    Aguarda 7 segundos antes de clicar.
    """
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Aceitar"))
        )
        time.sleep(7)  # Aguarda 7 segundos antes de clicar
        cookie_button.click()
        time.sleep(2)  # Aguarda um instante após clicar
    except Exception as e:
        logging.debug("Erro ao aceitar cookies: " + str(e))


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Configura e retorna um driver do Chrome com as opções especificadas.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Ignora erros de certificado
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def executar_busca(rede_social: str, nicho: str, email: str, telefone: str, telefone2: str,
                   max_pages: int, search_engine: str = "google") -> list:
    """
    Executa a busca e o scraping utilizando os parâmetros informados e salva os resultados em CSV.
    """
    query = (
        f"site:{rede_social.lower()}.com {nicho} "
        f"({email}) (\"({telefone})\" OR \"({telefone2})\" OR \"+55\")"
    )
    logging.info(f"Executando busca com query: {query}")
    logging.debug(f"Parâmetros: Rede Social={rede_social}, Nicho={nicho}, "
                  f"Email={email}, Telefones=({telefone}, {telefone2}), "
                  f"Máx. Páginas={max_pages}, Motor de busca={search_engine}")

    results = search_and_scrape(query, rede_social, max_pages, search_engine)
    save_to_csv(results)
    return results


def search_and_scrape(query: str, rede_social: str, max_pages: int = 5,
                      search_engine: str = "google") -> list:
    """
    Realiza o scraping dos resultados da busca, navegando pelas páginas e extraindo os dados.
    """
    logging.info(f"Iniciando scraping no {search_engine}...")
    driver = get_driver(headless=True)

    try:
        # Acessa o site de busca conforme o search_engine
        if search_engine.lower() == "duckduckgo":
            driver.get("https://duckduckgo.com/")
            time.sleep(15)  # Aguarda 15 segundos para o navegador abrir
            accept_cookies(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
        elif search_engine.lower() == "bing":
            driver.get("https://www.bing.com/")
            time.sleep(15)  # Aguarda 15 segundos para o navegador abrir
            accept_cookies(driver)
            time.sleep(5)  # Intervalo adicional para o Bing
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo"))
            )
        else:  # Google
            driver.get("https://google.com/")
            time.sleep(15)  # Aguarda 15 segundos para o navegador abrir
            accept_cookies(driver)
            time.sleep(5)
            logging.info(f"Pesquisa iniciada para query: {query}")
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb")
                )
            )

        results = []
        current_page = 1
        while current_page <= max_pages:
            logging.info(f"Buscando resultados na página {current_page}...")
            print(f"Buscando página {current_page}...")
            try:
                if search_engine.lower() == "duckduckgo":
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "article"))
                    )
                    containers = driver.find_elements(
                        By.CSS_SELECTOR, "article")
                elif search_engine.lower() == "bing":
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "li.b_algo"))
                    )
                    containers = driver.find_elements(
                        By.CSS_SELECTOR, "li.b_algo")
                else:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR,
                             "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb")
                        )
                    )
                    containers = driver.find_elements(
                        By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb"
                    )
                    logging.info(
                        f"{len(containers)} resultados encontrados na página {current_page}.")
            except TimeoutException:
                print("Timeout ao carregar os resultados.")
                logging.warning(
                    f"Timeout ao carregar resultados na página {current_page}.")
                break

            page_results = 0
            for container in containers:
                try:
                    if search_engine.lower() == "bing":
                        snippet = ""
                        selectors = [
                            "div.b_caption p.b_lineclamp4",
                            "div.b_caption p.b_lineclamp2",
                            "div.b_caption p.b_lineclamp3"
                        ]
                        for sel in selectors:
                            try:
                                element = container.find_element(
                                    By.CSS_SELECTOR, sel)
                                snippet_text = element.text.strip()
                                if snippet_text:
                                    snippet = snippet_text
                                    break
                            except NoSuchElementException:
                                continue
                        if snippet == "":
                            snippet = container.text.strip()
                    else:
                        snippet = container.text.strip()

                    emails = re.findall(
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", snippet
                    )
                    phones = re.findall(
                        r"\(?\d{2}\)?\s?\d{4,5}-\d{4}", snippet
                    )

                    logging.debug(f"Snippet encontrado: {snippet[:50]}...")
                    logging.debug(f"E-mails encontrados: {emails}")
                    logging.debug(f"Telefones encontrados: {phones}")

                    # Extração da URL e do username varia conforme o search engine
                    url = ""
                    if search_engine.lower() == "duckduckgo":
                        try:
                            a_tag = container.find_element(By.TAG_NAME, "a")
                            url = a_tag.get_attribute("href")
                        except Exception:
                            pass
                    elif search_engine.lower() == "bing":
                        try:
                            a_tag = container.find_element(By.TAG_NAME, "a")
                            url = a_tag.get_attribute("href")
                        except Exception:
                            pass
                    else:
                        try:
                            parent = container.find_element(
                                By.XPATH, "./ancestor::div[@class='g']")
                            a_tag = parent.find_element(By.TAG_NAME, "a")
                            url = a_tag.get_attribute("href")
                        except Exception:
                            pass
                    username = extract_username(
                        url, rede_social) if url else ""
                    results.append({
                        "emails": emails,
                        "phones": phones,
                        "snippet": snippet,
                        "rede_social_user": username
                    })
                    page_results += 1
                    time.sleep(random.uniform(1.5, 3.0))
                except Exception as e:
                    logging.exception("Erro ao processar resultado:")
                    print(f"Erro ao processar resultado: {e}")

            print(f"Resultados encontrados nesta página: {page_results}")
            try:
                if search_engine.lower() == "duckduckgo":
                    next_page_button = driver.find_element(
                        By.ID, "more-results")
                    next_page_button.click()
                    time.sleep(random.uniform(2, 4))
                    current_page += 1
                elif search_engine.lower() == "bing":
                    try:
                        next_page_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//a[.//svg[@viewBox='0 0 16 16']]"))
                        )
                    except TimeoutException:
                        logging.warning(
                            "Botão 'Próxima página' não encontrado pelo SVG, tentando seletor antigo.")
                        try:
                            next_page_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.CSS_SELECTOR, "a.sb_pagN"))
                            )
                        except TimeoutException:
                            logging.critical(
                                "Botão 'Próxima página' do Bing não encontrado. Fim da pesquisa.")
                            print(
                                "Botão 'Próxima página' não encontrado. Fim da pesquisa.")
                            break
                    # Rola a página para que o botão fique visível e clica nele
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", next_page_button)
                    time.sleep(1)
                    next_page_button.click()
                    time.sleep(5)  # Intervalo de 5 segundos para o Bing
                    current_page += 1
                else:
                    next_page_button = driver.find_element(
                        By.LINK_TEXT, "Mais")
                    next_page_button.click()
                    time.sleep(5)
                    current_page += 1
            except NoSuchElementException as e:
                logging.critical(f"Erro grave no scraping: {e}")
                if search_engine.lower() == "duckduckgo":
                    print("Botão 'Mais resultados' não encontrado. Fim da pesquisa.")
                elif search_engine.lower() == "bing":
                    print("Botão 'Próxima página' não encontrado. Fim da pesquisa.")
                else:
                    print("Não há mais páginas.")
                break

        logging.info(
            f"Scraping finalizado. Total de resultados: {len(results)}")
        return results
    finally:
        driver.quit()


def extract_username(url: str, rede_social: str) -> str:
    """
    Extrai o username da URL com base no formato da rede social.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    parts = path.split("/")
    return parts[0]


def save_to_csv(results: list, filename: str = "resultados.csv") -> None:
    """
    Salva os resultados obtidos em um arquivo CSV.
    """
    logging.info(f"Salvando {len(results)} resultados em {filename}...")
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Rede Social", "E-mails", "Telefones", "Snippet"])
        for result in results:
            writer.writerow([
                result.get("rede_social_user", ""),
                ", ".join(result['emails']) if result['emails'] else 'Nenhum',
                ", ".join(result['phones']) if result['phones'] else 'Nenhum',
                result['snippet']
            ])
    logging.info(f"Arquivo {filename} salvo com sucesso.")


if __name__ == "__main__":
    print("Back-end iniciado. Aguardando chamadas do front-end.")
