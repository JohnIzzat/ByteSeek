from bs4 import BeautifulSoup

# Supondo que `html_content` contém o HTML da página
html_content = """
<article id="r1-0" data-handled-by-react="true" data-testid="result" data-nrn="result" class="yQDlj3B5DI5YO8c8Ulio CpkrTDP54mqzpuCSn1Fa SKlplDuh9FjtDprgoMxk Fr1jPX9uTqiYNJFs2Cfb mCluLpS0Bxp3cyx5jiG3">
    <div class="OHr0VX9IuNcv6iakvT6A">
        <div class="BdZVYXbdg6Rx9Lrm5wzC">
            <p class="ePXqZzRA466zTvNP6hpa wZ4JdaHxSAhGy1HoNVja d26Geqs1C__RaCO7MUs2">instagram.com</p>
        </div>
    </div>
    <div class="ikg2IXiCD14iVX7AdZo1">
        <h2 class="LnpumSThxEWMIsDdAT17 CXMyPcQ6nDv47DKFeywM Kodf3iC7sTttqmwyeHFw">
            <a href="https://www.instagram.com/yasiclothes/" rel="noopener" target="_self" data-testid="result-title-a" data-handled-by-react="true" class="eVNpHGjtxRBq_gLOfGDr LQNqh2U1kzYxREs65IJu">
                <span class="EKtkFWMYpwzMKOYr0GYm LQVY1Jpkk8nyJ6HBWKAk">YASI CLOTHES | LOJA DE ROUPAS FEMININAS - Instagram</span>
            </a>
        </h2>
    </div>
    <div class="E2eLOJr8HctVnDOTM8fs">
        <div data-result="snippet" class="OgdwYG6KE2qthn9XQWFC">
            <div>
                <span class="kY2IgmnCmOGjharHErah" style="-webkit-line-clamp: 3;">
                    <span>456 Followers, 1 Following, 10 Posts - YASI CLOTHES | LOJA DE <b>ROUPAS</b> FEMININAS (@yasiclothes) on Instagram: " O toque de YASI que seu guarda-<b>roupa</b> precisava Do casual a moda balada! :) 📧yasiclothes.79<b>@gmail.com</b> 💠Visite nosso <b>site</b>"</span>
                </span>
            </div>
        </div>
    </div>
</article>
"""

# Criando o objeto BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Encontrar o artigo
article = soup.find("article")

# Coletar dados relevantes
if article:
    # URL principal
    url = article.find("a", {"data-testid": "result-title-a"})[
        "href"] if article.find("a", {"data-testid": "result-title-a"}) else None
    # Título
    title = article.find("span", class_="EKtkFWMYpwzMKOYr0GYm").text if article.find(
        "span", class_="EKtkFWMYpwzMKOYr0GYm") else None
    # Snippet
    snippet = article.find("span", class_="kY2IgmnCmOGjharHErah").text if article.find(
        "span", class_="kY2IgmnCmOGjharHErah") else None
    # Dominio
    domain = article.find("p", class_="ePXqZzRA466zTvNP6hpa").text if article.find(
        "p", class_="ePXqZzRA466zTvNP6hpa") else None

    # Exibir os resultados
    print("Título:", title)
    print("URL:", url)
    print("Dominio:", domain)
    print("Snippet:", snippet)
else:
    print("Artigo não encontrado.")
