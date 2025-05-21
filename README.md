# BaixarURL.py

Um aplicativo simples para **baixar vídeos do YouTube** de forma prática e visual, usando uma interface gráfica amigável feita com Python (Tkinter).

## 📥 Funcionalidade

Cole a URL de um vídeo do YouTube, escolha a pasta de destino e clique em **"Baixar"**. O download será feito automaticamente.

Recomendação:
Quando for colar um URL do youtube music ficara assim: "https://music.youtube.com/..."

Remova: "music.". Dessa forma: "https://youtube.com/..."



## 🖼️ Interface

### Tela inicial

![tela_inicial](https://github.com/duvvic/baixar-URL/blob/main/sem%20url.png)



- Campo para colar a URL
- Botões: `Baixar` e `Escolher pasta`

### Após colar o link

![link_colado](https://github.com/duvvic/baixar-URL/blob/main/verificando%20url.png)


- Mensagem de sucesso exibida ao final do download

## ✅ Requisitos

- Python 3.8+
- [pytube](https://github.com/duvvic/baixar-URL/blob/main/baixando%20a%20url.png)
- tkinter (já vem com o Python)

Para instalar o `pytube`, rode:
```bash
pip install pytube
```

## ▶️ Como executar

```bash
python baixarURL.py
```

## 📁 Estrutura

- `baixarURL.py` – Arquivo principal do aplicativo
- `README.md` – Este arquivo de documentação
- Imagens: capturas de tela para demonstrar o uso

## 📌 Observação

Este projeto é voltado para fins educacionais e uso pessoal. Não utilize para baixar conteúdo protegido por direitos autorais sem permissão.
