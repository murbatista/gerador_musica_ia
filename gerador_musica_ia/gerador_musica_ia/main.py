
import os
import glob
import numpy as np

from music21 import converter, instrument, note, chord, stream

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.utils import to_categorical


# -------------------------------------------------------------
# 1. LEITURA E EXTRAÇÃO DOS ARQUIVOS MIDI
# -------------------------------------------------------------

def carregar_musicas():
    lista_notas = []
    caminhos_midi = glob.glob("midis_publicos/*.mid")

    if len(caminhos_midi) == 0:
        print("Nenhum arquivo MIDI foi encontrado. Execute o loader.py.")
        return []

    for caminho in caminhos_midi:
        print(f"Analisando arquivo: {caminho}")

        try:
            musica = converter.parse(caminho)

            try:
                partes = instrument.partitionByInstrument(musica)
                elementos = partes.parts[0].recurse()
            except:
                elementos = musica.flatten().notes

            for item in elementos:
                if isinstance(item, note.Note):
                    lista_notas.append(str(item.pitch))

                elif isinstance(item, chord.Chord):
                    notas_acorde = ".".join(
                        str(n) for n in item.normalOrder
                    )
                    lista_notas.append(notas_acorde)

        except Exception as erro:
            print(f"Não foi possível ler {caminho}: {erro}")

    return lista_notas


notas_musicais = carregar_musicas()

print(f"\nQuantidade de elementos encontrados: {len(notas_musicais)}")

if not notas_musicais:
    exit()


# -------------------------------------------------------------
# 2. PREPARAÇÃO DOS DADOS PARA A REDE NEURAL
# -------------------------------------------------------------

vocabulario = sorted(set(notas_musicais))
total_notas = len(vocabulario)

nota_para_numero = {
    valor: indice for indice, valor in enumerate(vocabulario)
}

numero_para_nota = {
    indice: valor for indice, valor in enumerate(vocabulario)
}

tamanho_sequencia = 32

entradas = []
saidas = []

for posicao in range(len(notas_musicais) - tamanho_sequencia):

    trecho = notas_musicais[posicao:posicao + tamanho_sequencia]
    proxima_nota = notas_musicais[posicao + tamanho_sequencia]

    entradas.append([
        nota_para_numero[valor] for valor in trecho
    ])

    saidas.append(nota_para_numero[proxima_nota])


total_sequencias = len(entradas)

X = np.reshape(
    entradas,
    (total_sequencias, tamanho_sequencia, 1)
) / float(total_notas)

y = to_categorical(saidas, num_classes=total_notas)


# -------------------------------------------------------------
# 3. CRIAÇÃO E TREINAMENTO DA REDE NEURAL
# -------------------------------------------------------------

print("\nPreparando o modelo de inteligência artificial...")

modelo = Sequential([
    LSTM(
        128,
        input_shape=(X.shape[1], X.shape[2]),
        return_sequences=True
    ),

    Dropout(0.2),

    LSTM(128),

    Dense(total_notas, activation="softmax")
])

modelo.compile(
    loss="categorical_crossentropy",
    optimizer="adam"
)

print("Treinamento iniciado!")

modelo.fit(
    X,
    y,
    epochs=30,
    batch_size=32
)

print("\nTreinamento concluído!")


# -------------------------------------------------------------
# 4. GERAÇÃO DE UMA NOVA COMPOSIÇÃO
# -------------------------------------------------------------

def escolher_nota(probabilidades, temperatura=1.0):

    probabilidades = np.asarray(probabilidades).astype("float64")

    probabilidades = np.log(probabilidades + 1e-7) / temperatura

    probabilidades = np.exp(probabilidades)

    probabilidades = probabilidades / np.sum(probabilidades)

    escolha = np.random.multinomial(1, probabilidades, 1)

    return np.argmax(escolha)


indice_inicio = np.random.randint(0, len(entradas))

sequencia_atual = list(entradas[indice_inicio])

musica_gerada = []

TEMPERATURA = 1.0
QUANTIDADE_NOTAS = 100

print(f"\nCriando uma composição com {QUANTIDADE_NOTAS} notas...")

for contador in range(QUANTIDADE_NOTAS):

    dados_entrada = np.reshape(
        sequencia_atual,
        (1, len(sequencia_atual), 1)
    ) / float(total_notas)

    probabilidades = modelo.predict(
        dados_entrada,
        verbose=0
    )[0]

    nota_escolhida = escolher_nota(
        probabilidades,
        temperatura=TEMPERATURA
    )

    musica_gerada.append(numero_para_nota[nota_escolhida])

    sequencia_atual.append(nota_escolhida)
    sequencia_atual = sequencia_atual[1:]


# -------------------------------------------------------------
# 5. CONVERSÃO E SALVAMENTO DA MÚSICA
# -------------------------------------------------------------

tempo = 0
elementos_musicais = []

for elemento in musica_gerada:

    if "." in elemento or elemento.isdigit():

        valores_acorde = elemento.split(".")

        notas_acorde = [
            note.Note(int(valor))
            for valor in valores_acorde
        ]

        acorde = chord.Chord(notas_acorde)
        acorde.offset = tempo

        elementos_musicais.append(acorde)

    else:

        nova_nota = note.Note(elemento)
        nova_nota.offset = tempo

        elementos_musicais.append(nova_nota)

    tempo += 0.5


composicao = stream.Stream(elementos_musicais)

arquivo_final = "minha_musica_gerada.mid"

composicao.write("midi", fp=arquivo_final)

print("\nMúsica criada com sucesso!")
print(f"Arquivo salvo: {os.path.abspath(arquivo_final)}")
