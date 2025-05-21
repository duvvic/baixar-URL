import flet as ft
from moviepy.audio.io.AudioFileClip import AudioFileClip
import os

def main(page: ft.Page):
    page.title = "Conversor WEBM para MP3 (lote + subpastas)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 540
    page.window_height = 400
    page.padding = 25
    page.spacing = 20
    page.scroll = ft.ScrollMode.AUTO

    result_text = ft.Text(color=ft.colors.WHITE70, size=14)
    percent_text = ft.Text(color=ft.colors.WHITE70, size=16, weight=ft.FontWeight.BOLD)
    progress_bar = ft.ProgressBar(width=420, height=20, border_radius=10)

    dir_picker = ft.FilePicker()

    def convert_folder(e):
        if not dir_picker.result or not dir_picker.result.path:
            result_text.value = "⚠️ Nenhuma pasta selecionada."
            page.update()
            return

        folder_path = dir_picker.result.path

        webm_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".webm"):
                    full_path = os.path.join(root, file)
                    mp3_path = os.path.splitext(full_path)[0] + ".mp3"
                    if not os.path.exists(mp3_path):  # Ignora se .mp3 já existe
                        webm_files.append(full_path)

        total = len(webm_files)
        if total == 0:
            result_text.value = "✔️ Todos os arquivos já foram convertidos!"
            progress_bar.value = 0
            percent_text.value = ""
            page.update()
            return

        converted = 0
        errors = 0

        for i, input_path in enumerate(webm_files, start=1):
            output_path = os.path.splitext(input_path)[0] + ".mp3"
            try:
                audio_clip = AudioFileClip(input_path)
                audio_clip.write_audiofile(output_path, logger=None)
                audio_clip.close()
                os.remove(input_path)
                converted += 1
            except Exception as ex:
                errors += 1
                print(f"Erro ao converter {input_path}: {ex}")

            progress = i / total
            progress_bar.value = progress
            percent_text.value = f"{int(progress * 100)}% concluído"
            page.update()

        result_text.value = f"✅ Conversão finalizada: {converted} convertidos, {errors} erros."
        page.update()

    def pick_folder_result(e):
        convert_folder(e)

    dir_picker.on_result = pick_folder_result

    pick_button = ft.ElevatedButton(
        text="📂 Selecionar pasta com .webm",
        on_click=lambda _: dir_picker.get_directory_path(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
            bgcolor=ft.colors.BLUE_GREY_700,
            color=ft.colors.WHITE,
            overlay_color=ft.colors.BLUE_200
        )
    )

    card = ft.Container(
        content=ft.Column(
            [
                ft.Text("🎧 Conversor WEBM → MP3", size=24, weight="bold", color=ft.colors.WHITE),
                ft.Text("Converta todos os vídeos .webm para .mp3 de uma pasta (e subpastas).",
                        size=14, color=ft.colors.WHITE60),
                pick_button,
                progress_bar,
                percent_text,
                result_text
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=25,
        border_radius=16,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    page.overlay.append(dir_picker)
    page.add(ft.Column([card], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

ft.app(target=main)
