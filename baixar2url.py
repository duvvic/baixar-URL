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
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Estado inicial
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    cancel_event = threading.Event()

    # Componentes visuais
    status_text = ft.Text(value="", size=18, color=ft.colors.WHITE, weight=ft.FontWeight.W_500)
    progress_bar = ft.ProgressBar(width=420, visible=False, color=ft.colors.CYAN, bgcolor=ft.colors.BLUE_GREY_900, bar_height=8)
    view_button = ft.ElevatedButton(
        "Ver download",
        icon=ft.icons.FOLDER_OPEN,
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: open_download_folder(download_path)
    )
    cancel_button = ft.ElevatedButton(
        "Cancelar",
        icon=ft.icons.CANCEL,
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.colors.RED_700,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: cancel_event.set()
    )
    url_field = ft.TextField(
        label="Cole a URL aqui",
        width=520,
        bgcolor=ft.colors.BLUE_GREY_800,
        color=ft.colors.WHITE,
        border_radius=12,
        border_color=ft.colors.CYAN,
        focused_border_color=ft.colors.CYAN_ACCENT,
        label_style=ft.TextStyle(size=16, color=ft.colors.CYAN_200),
        text_style=ft.TextStyle(size=16),
        prefix_icon=ft.icons.LINK,
    )

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
        status_text.color = ft.colors.AMBER
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
        icon=ft.icons.DOWNLOAD,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.colors.CYAN_700,
            color=ft.colors.WHITE,
        ),
        on_click=iniciar_download
    )
    choose_btn = ft.OutlinedButton(
        "Escolher pasta",
        icon=ft.icons.FOLDER,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.colors.BLUE_GREY_900,
            color=ft.colors.CYAN_200,
        ),
        on_click=escolher_pasta
    )

    # Layout
    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "🎵 Baixador de URLs Inteligente",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.CYAN_200,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    url_field,
                    ft.Row([download_btn, choose_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=18),
                    progress_bar,
                    status_text,
                    ft.Row([cancel_button, view_button], alignment=ft.MainAxisAlignment.CENTER, spacing=18)
                ], spacing=22, alignment=ft.MainAxisAlignment.CENTER),
                padding=30,
                width=650,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=18,
                shadow=ft.BoxShadow(blur_radius=18, color=ft.colors.CYAN_900, offset=ft.Offset(0, 6)),
            ),
            elevation=0,
        )
    )

ft.app(target=main)

