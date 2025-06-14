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


def accept_cookies(driver):
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Aceitar"))
        )
        time.sleep(7)
        cookie_button.click()
        time.sleep(2)
    except Exception as e:
        logging.debug("Erro ao aceitar cookies: " + str(e))


def get_driver(headless: bool = False) -> webdriver.Chrome:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
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
    logging.info(f"Iniciando scraping no {search_engine}...")
    driver = get_driver(headless=True)

    try:
        if search_engine.lower() == "duckduckgo":
            driver.get("https://duckduckgo.com/")
            time.sleep(15)
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
            time.sleep(10)
            accept_cookies(driver)
            time.sleep(10)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo"))
            )
        else:
            driver.get("https://google.com/")
            time.sleep(15)
            accept_cookies(driver)
            time.sleep(5)
            logging.info(f"Pesquisa iniciada para query: {query}")
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b, div.fzUZNc")
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
                             "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b, div.fzUZNc")
                        )
                    )
                    containers = driver.find_elements(
                        By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b, div.fzUZNc"
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
                            "div.b_caption p.b_lineclamp1",
                            "div.b_caption p.b_lineclamp2",
                            "div.b_caption p.b_lineclamp3",
                            "div.b_caption p.b_lineclamp4"
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
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", next_page_button)
                    time.sleep(3)
                    next_page_button.click()
                    time.sleep(5)
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
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    parts = path.split("/")
    return parts[0]


def save_to_csv(results: list, filename: str = "resultados.csv") -> None:
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
