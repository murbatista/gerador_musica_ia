import os
from urllib.request import Request, urlopen

# Cria o diretório para salvar os arquivos
os.makedirs("midis_publicos", exist_ok=True)

# Amostras validadas em Domínio Público / CC0 (Wikimedia Commons)
urls_midis = [
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV772/bach-invention-01/bach-invention-01.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV773/bach-invention-02/bach-invention-02.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BachJS/BWV775/bach-invention-04/bach-invention-04.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/MozartWA/KV545/mozart-piano-sonata-15-1/mozart-piano-sonata-15-1.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/BeethovenLV/O27/moonlight-1/moonlight-1.mid",
    "https://raw.githubusercontent.com/MutopiaProject/MutopiaProject/master/ftp/ChopinFF/O28/chopin-prelude-28-04/chopin-prelude-28-04.mid"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Baixando arquivos MIDI em Domínio Público...")
for i, url in enumerate(urls_midis, start=1):
    nome_arquivo = os.path.join("midis_publicos", f"musica_{i:02d}.mid")
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as response, open(nome_arquivo, 'wb') as out_file:
            out_file.write(response.read())
        print(f"✓ [{i}/{len(urls_midis)}] Baixado com sucesso!")
    except Exception as e:
        print(f"✕ Erro ao baixar música {i}: {e}")