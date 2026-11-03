
import os
from urllib.request import Request, urlopen

# Pasta onde os arquivos serão armazenados
pasta_destino = "midis_publicos"
os.makedirs(pasta_destino, exist_ok=True)

# Lista de arquivos MIDI disponíveis para download
arquivos_midi = [
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV772/bach-invention-01/bach-invention-01.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV773/bach-invention-02/bach-invention-02.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV775/bach-invention-04/bach-invention-04.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/MozartWA/KV545/mozart-piano-sonata-15-1/mozart-piano-sonata-15-1.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BeethovenLV/O27/moonlight-1/moonlight-1.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/ChopinFF/O28/chopin-prelude-28-04/chopin-prelude-28-04.mid"
]

# Configuração da requisição
cabecalho = {
    "User-Agent": "Mozilla/5.0"
}

print("Iniciando o download das músicas MIDI...\n")

# Percorre a lista e realiza os downloads
for indice, endereco in enumerate(arquivos_midi, 1):

    arquivo = f"musica_{indice:02d}.mid"
    caminho = os.path.join(pasta_destino, arquivo)

    try:
        requisicao = Request(endereco, headers=cabecalho)

        resposta = urlopen(requisicao, timeout=15)

        with resposta, open(caminho, "wb") as arquivo_saida:
            arquivo_saida.write(resposta.read())

        print(f"Download concluído: {arquivo}")

    except Exception as erro:
        print(f"Falha no download {arquivo}: {erro}")

print("\nProcesso de download finalizado!")
