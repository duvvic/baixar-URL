import flet as ft
import os
import platform
import threading
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

# Logger personalizado para capturar warnings e errors do yt_dlp
class CustomLogger:
    def __init__(self, status_text, page):
        self.status_text = status_text
        self.page = page

    def debug(self, msg):
        pass  # ignora mensagens de debug

    def warning(self, msg):
        self.status_text.value = f"⚠️ {msg}"
        self.status_text.color = ft.colors.ORANGE
        self.page.update()

    def error(self, msg):
        self.status_text.value = f"❌ {msg}"
        self.status_text.color = ft.colors.RED
        self.page.update()


def is_supported_url(url, status_text, page):
    try:
        # Correção da URL do YouTube Music
        if "music.youtube.com" in url:
            url = url.replace("music.youtube.com", "www.youtube.com")
        
        # Se for playlist, ajusta para o formato correto do YouTube
        if url.startswith("playlist?list="):
            url = "https://www.youtube.com/" + url

        # Definir opções do yt-dlp
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,  # para não baixar o conteúdo, mas apenas pegar as informações
            "logger": CustomLogger(status_text, page),
            "format": "bestaudio/best",
            "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",}],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Verifica se a URL corresponde a uma playlist ou vídeo
            return info
        
    except Exception as e:
        return None


def open_download_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        os.system(f"open '{path}'")
    else:
        os.system(f"xdg-open '{path}'")


def download_thread(page, url, download_path, progress_bar, status_text, cancel_event, view_button, cancel_button):
    def progress_hook(d):
        if cancel_event.is_set():
            raise Exception("Download cancelado pelo usuário.")
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            downloaded = d.get("downloaded_bytes", 0)
            percent = int(downloaded / total * 100)
            progress_bar.value = percent / 100
            status_text.value = f"Baixando: {d.get('filename', '')} ({percent}%)"
            page.update()
        elif d.get("status") == "finished":
            progress_bar.value = 1
            page.update()

    # configurações do yt_dlp
    ydl_opts = {
        "logger": CustomLogger(status_text, page),
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "quiet": True,
        "noplaylist": False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                count = len(info['entries'])
                status_text.value = f"🎧 Playlist completa: {count} vídeos"
            else:
                status_text.value = "✅ Download concluído com sucesso!"
            status_text.color = ft.colors.GREEN
            view_button.visible = True
    except DownloadError as e:
        status_text.value = f"❌ Erro ao baixar: {e}"
        status_text.color = ft.colors.RED
    except Exception as e:
        status_text.value = f"⚠️ Interrompido: {e}"
        status_text.color = ft.colors.ORANGE
    finally:
        progress_bar.visible = False
        cancel_button.visible = False
        page.update()


def main(page: ft.Page):
    page.title = "Baixador de URLs Inteligente"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.colors.BLACK
    page.window_width = 600
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Estado inicial
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    cancel_event = threading.Event()

    # Componentes visuais
    status_text = ft.Text(value="", size=16, color=ft.colors.WHITE)
    progress_bar = ft.ProgressBar(width=420, visible=False, color=ft.colors.CYAN, height=20, border_radius=10)
    view_button = ft.ElevatedButton("Ver download", visible=False, on_click=lambda e: open_download_folder(download_path))
    cancel_button = ft.ElevatedButton("Cancelar", visible=False, bgcolor=ft.colors.RED, on_click=lambda e: cancel_event.set())
    url_field = ft.TextField(label="Cole a URL aqui", width=500, bgcolor=ft.colors.WHITE, color=ft.colors.BLACK)

    # FilePicker para escolher pasta
    def on_folder_selected(e: ft.FilePickerResultEvent):
        nonlocal download_path
        if e.path:
            download_path = e.path
            status_text.value = f"📁 Pasta selecionada: {download_path}"
            page.update()

    folder_picker = ft.FilePicker(on_result=on_folder_selected)
    page.overlay.append(folder_picker)

    def escolher_pasta(e):
        folder_picker.get_directory_path(dialog_title="Selecione a pasta")

    # Iniciar download
    def iniciar_download(e):
        url = url_field.value.strip()
        if not url:
            status_text.value = "⚠️ Insira uma URL válida."
            status_text.color = ft.colors.RED
            page.update()
            return

        # Reset UI
        status_text.value = "🔍 Verificando URL..."
        status_text.color = ft.Colors.AMBER
        progress_bar.value = 0
        progress_bar.visible = True
        view_button.visible = False
        cancel_button.visible = True
        page.update()

        info = is_supported_url(url, status_text, page)
        if not info:
            status_text.value = "❌ URL inválida ou não suportada."
            status_text.color = ft.colors.RED
            progress_bar.visible = False
            cancel_button.visible = False
            page.update()
            return

        status_text.value = f"⏬ Baixando de: {info.get('extractor_key', '')}"
        status_text.color = ft.colors.CYAN
        cancel_event.clear()
        threading.Thread(
            target=download_thread,
            args=(page, url, download_path, progress_bar, status_text, cancel_event, view_button, cancel_button),
            daemon=True
        ).start()

    # Botões
    download_btn = ft.ElevatedButton(
        "Baixar",
        on_click=iniciar_download,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
            bgcolor=ft.colors.BLUE_GREY_700,
            color=ft.colors.WHITE,
            overlay_color=ft.colors.BLUE_200
        )
    )
    choose_btn = ft.ElevatedButton(
        "Escolher pasta",
        on_click=escolher_pasta,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
            bgcolor=ft.colors.BLUE_GREY_700,
            color=ft.colors.WHITE,
            overlay_color=ft.colors.BLUE_200
        )
    )

    # Layout
    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column([ 
                    url_field,
                    ft.Row([download_btn, choose_btn], alignment=ft.MainAxisAlignment.CENTER),
                    progress_bar,
                    status_text,
                    ft.Row([cancel_button, view_button], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=20),
                padding=25, width=600, bgcolor=ft.colors.SURFACE_VARIANT, border_radius=16
            ),
            elevation=5, shadow_color=ft.colors.BLUE_200
        )
    )

ft.app(target=main)