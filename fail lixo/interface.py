import flet as ft
import sys
import os
from main import executar_busca

# Todas as configurações da Interface

def main(page: ft.Page):
    page.title = "Busca e Seleção de Parâmetros"
    page.theme_mode = "black"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Variáveis de controle globais
    cancelar_coleta = False
    driver_atual = None  # Vai armazenar a referência do driver

    # Define o tamanho da Janela
    page.window.width = 400
    page.window.height = 600

    # Impede do usuario redimensionar a Janela
    page.window.resizable = False

    def close_dialog(e):
        nonlocal cancelar_coleta
        cancelar_coleta = True
        page.overlay.clear()  # Use this instead of page.dialog = None
        progresso_dialog.open = False
        page.update()  # Fixed the typo from 'upodate' to 'update'

    # Criando a caixa de diálogo (modal)
    progresso_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Coletando Dados"),
        content=ft.Text("Aguarde enquanto os dados estão sendo coletados..."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog(e))  # Vamos adicionar a ação depois
        ],
    )


    # Função para cancelar a busca e fechar o navegador e o aplicativo
    def cancelar_busca(e):
        # Fecha o modal
        nonlocal cancelar_coleta
        cancelar_coleta = True
        progresso_dialog.open = False
        page.dialog = None
        page.overlay.clear()
        page.update()
        
    # Agora associamos a função ao botão "Cancelar"
    #progresso_dialog.actions[0].on_click = cancelar_busca

    # Função e botão para alterar o tema
    def alterar_tema(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    botao_tema = ft.ElevatedButton(
        "Mudar Tema",
        on_click=alterar_tema,
        width=100,
        height=40
    )
    page.floating_action_button = botao_tema

    # Opções de Rede Social
    social_media_label = ft.Text("Rede Social:")
    social_media_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("facebook"),
            ft.dropdown.Option("instagram"),
        ],
        hint_text="Selecione",
        width=200,
    )

    # Opções de Nicho
    niche_label = ft.Text("Nicho:")
    niche_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("roupas"),
            ft.dropdown.Option("pets"),
        ],
        hint_text="Selecione",
        width=200,
    )

    # Opções de E-mail
    email_label = ft.Text("E-mail:")
    email_checkboxes = ft.Row([
        ft.Checkbox(label="Gmail"),
        ft.Checkbox(label="Hotmail"),
    ])

    # Lista de DDDs do Brasil
    ddds_brasil = [
        "11", "21"
    ]

    # Opções de Telefone
    phone_label = ft.Text("Telefone (DDD):")
    phone_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(ddd) for ddd in ddds_brasil],
        hint_text="Selecione",
        width=200,
    )

    # Botão de Confirmar
    def on_confirm_click(e):
        nonlocal cancelar_coleta, driver_atual
        cancelar_coleta = False
        
        selected_social_media = social_media_dropdown.value
        selected_niche = niche_dropdown.value
        selected_emails = [
            checkbox.label for checkbox in email_checkboxes.controls if checkbox.value
        ]
        selected_phone = phone_dropdown.value

        if not selected_social_media or not selected_niche or not selected_emails or not selected_phone:
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, preencha todos os campos."))
            page.snack_bar.open()
            return

        # Monta a query para o back-end
        email_query = " OR ".join(
            [f"@{email.lower()}.com" for email in selected_emails])

        # Abre a caixa de diálogo informando que a busca está em andamento
        page.overlay.append(progresso_dialog)
        progresso_dialog.open = True
        page.update()

        # Chama a função do back-end para buscar os dados
        results, driver = executar_busca(
            selected_social_media, selected_niche, email_query, selected_phone
        )

        driver_atual = driver  # Armazena o driver para poder cancelar depois

        # Fecha a caixa de diálogo quando a coleta terminar
        progresso_dialog.open = False
        page.update()

        if results:
            page.snack_bar = ft.SnackBar(
                ft.Text("Resultados salvos no arquivo 'resultados.csv'."))
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Nenhum resultado encontrado."))
        page.snack_bar.open()

    confirm_button = ft.ElevatedButton(
        "Confirmar",
        on_click=on_confirm_click,
        color="white",
        bgcolor="green600",
    )

    # Layout
    page.add(
        ft.Column(
            [
                social_media_label,
                social_media_dropdown,
                niche_label,
                niche_dropdown,
                email_label,
                email_checkboxes,
                phone_label,
                phone_dropdown,
                confirm_button,
            ],
            spacing=15,
            alignment="center"
        )
    )


ft.app(target=main)
