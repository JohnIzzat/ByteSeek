import flet as ft
from main import executar_busca

# Dicionário de nichos com pesquisas personalizadas
niche_queries = {
    "pets": '"pets"',
    "roupas": '"moda" OR "roupas" OR "vestuário"',
    "infantil": '"infantil" OR "criança" OR "kids"',
    "autopeças": '"auto peça" OR "autopeça" OR "auto peças"',
}


def show_snackbar(page, message):
    """Exibe uma snackbar com a mensagem informada."""
    snack_bar = ft.SnackBar(content=ft.Text(message))
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()


def main(page: ft.Page):
    page.title = "SeekBot"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window.width = 411
    page.window.height = 750

    progresso_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Coletando Dados"),
        content=ft.Text("Aguarde enquanto os dados estão sendo coletados..."),
    )

    social_media_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("facebook"),
            ft.dropdown.Option("instagram"),
        ],
        hint_text="Selecione",
        width=200,
    )

    niche_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("roupas"),
            ft.dropdown.Option("pets"),
            ft.dropdown.Option("infantil"),
            ft.dropdown.Option("autopeças"),
        ],
        hint_text="Selecione",
        width=200,
    )

    email_checkboxes = ft.Row([
        ft.Checkbox(label="Gmail"),
        ft.Checkbox(label="Hotmail"),
        ft.Checkbox(label="Outlook"),
        ft.Checkbox(label="Yahoo"),
    ])

    ddds_brasil = ["11", "21", "31"]
    phone_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(ddd) for ddd in ddds_brasil],
        hint_text="Selecione o 1º DDD",
        width=200,
    )
    # Dropdown para o 2º DDD
    phone_dropdown2 = ft.Dropdown(
        options=[ft.dropdown.Option(ddd) for ddd in ddds_brasil],
        hint_text="Selecione o 2º DDD",
        width=200,
    )

    # Dropdown para selecionar o motor de busca
    search_engine_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("Google"),
            ft.dropdown.Option("DuckDuckGo"),
        ],
        hint_text="Defina um buscador",
        width=202,
    )

    # Campo para definir o máximo de páginas a serem pesquisadas
    max_pages_field = ft.TextField(
        label="Máximo de Páginas", width=200, value="5")

    def on_confirm_click(e):
        selected_social_media = social_media_dropdown.value
        selected_niche = niche_dropdown.value
        selected_emails = [
            checkbox.label for checkbox in email_checkboxes.controls if checkbox.value]
        selected_phone = phone_dropdown.value
        selected_phone2 = phone_dropdown2.value  # Novo DDD
        selected_search_engine = search_engine_dropdown.value

        if (not selected_social_media or not selected_niche or not selected_emails or
                not selected_phone or not selected_phone2 or not max_pages_field.value or not selected_search_engine):
            show_snackbar(page, "Por favor, preencha todos os campos.")
            return

        try:
            max_pages = int(max_pages_field.value)
        except ValueError:
            show_snackbar(
                page, "Informe um número válido para o máximo de páginas.")
            return

        # Gera a query de e-mail com aspas duplas
        email_query = " OR ".join(
            [f"\"@{email.lower()}.com\"" for email in selected_emails])

        formatted_niche_query = (
            f"({niche_queries[selected_niche]})"
            if selected_niche in niche_queries else f"(\"{selected_niche}\")"
        )

        query_preview = (
            f"site:{selected_social_media.lower()}.com {formatted_niche_query} "
            f"({email_query}) (\"({selected_phone})\" OR \"({selected_phone2})\" OR \"+55\")"
        )
        print("Query gerada:", query_preview)

        progresso_dialog.open = True
        page.dialog = progresso_dialog
        page.update()

        # Chama o back-end com todos os parâmetros, incluindo o motor de busca (convertido para minúsculo)
        results = executar_busca(
            selected_social_media,
            formatted_niche_query,
            email_query,
            selected_phone,
            selected_phone2,
            max_pages,
            selected_search_engine.lower()
        )

        progresso_dialog.open = False
        page.update()

        show_snackbar(
            page, "Resultados salvos no arquivo 'resultados.csv'." if results else "Nenhum resultado encontrado.")

    confirm_button = ft.ElevatedButton(
        "Confirmar",
        on_click=on_confirm_click,
        color="white",
        bgcolor="green600",
    )

    page.add(
        ft.Column([
            ft.Text("Rede Social:"), social_media_dropdown,
            ft.Text("Nicho:"), niche_dropdown,
            ft.Text("E-mail:"), email_checkboxes,
            ft.Text("Telefone (1º DDD):"), phone_dropdown,
            ft.Text("Telefone (2º DDD):"), phone_dropdown2,
            ft.Text("Motor de Busca:"), search_engine_dropdown,
            max_pages_field,
            confirm_button,
        ], spacing=15, alignment="center")
    )


ft.app(target=main)
