import os
import glob
import numpy as np
from music21 import converter, instrument, note, chord, stream
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.utils import to_categorical

# -------------------------------------------------------------
# 1. EXTRAÇÃO DE NOTAS DOS ARQUIVOS MIDI
# -------------------------------------------------------------
def extrair_notas():
    notes = []
    arquivos = glob.glob("midis_publicos/*.mid")
    
    if not arquivos:
        print("⚠️ Nenhum arquivo MIDI encontrado! Execute o 'python loader.py' primeiro.")
        return []

    for file in arquivos:
        print(f"Lendo notas de: {file}")
        try:
            midi = converter.parse(file)
            try:
                s2 = instrument.partitionByInstrument(midi)
                notes_to_parse = s2.parts[0].recurse() 
            except:
                notes_to_parse = midi.flat.notes

            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))
        except Exception as e:
            print(f"Erro ao processar {file}: {e}")

    return notes

notes = extrair_notas()
print(f"\nTotal de notas extraídas: {len(notes)}")

if len(notes) == 0:
    exit()

# Mapeamento de notas para valores numéricos
pitchnames = sorted(set(item for item in notes))
n_vocab = len(pitchnames)
note_to_int = dict((note, number) for number, note in enumerate(pitchnames))
int_to_note = dict((number, note) for number, note in enumerate(pitchnames))

# Criando sequências de contexto para o treino
sequence_length = 32
network_input = []
network_output = []

for i in range(0, len(notes) - sequence_length, 1):
    sequence_in = notes[i:i + sequence_length]
    sequence_out = notes[i + sequence_length]
    network_input.append([note_to_int[char] for char in sequence_in])
    network_output.append(note_to_int[sequence_out])

n_patterns = len(network_input)
X = np.reshape(network_input, (n_patterns, sequence_length, 1)) / float(n_vocab)
y = to_categorical(network_output, num_classes=n_vocab)

# -------------------------------------------------------------
# 2. CONSTRUÇÃO E TREINAMENTO DO MODELO LSTM
# -------------------------------------------------------------
print("\nConstruindo a Rede Neural...")
model = Sequential([
    LSTM(128, input_shape=(X.shape[1], X.shape[2]), return_sequences=True),
    Dropout(0.2),
    LSTM(128),
    Dense(n_vocab, activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam')

print("Iniciando o treinamento do modelo (Aguarde alguns instantes)...")
model.fit(X, y, epochs=30, batch_size=32)

# -------------------------------------------------------------
# 3. GERAÇÃO DE NOVAS MÚSICAS (AMOSTRAGEM POR TEMPERATURA)
# -------------------------------------------------------------
def sample_with_temperature(predictions, temperature=1.0):
    predictions = np.asarray(predictions).astype('float64')
    predictions = np.log(predictions + 1e-7) / temperature
    exp_preds = np.exp(predictions)
    predictions = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, predictions, 1)
    return np.argmax(probas)

start = np.random.randint(0, len(network_input) - 1)
pattern = list(network_input[start])
prediction_output = []

TEMPERATURE = 1.0 # Altere entre 0.8 e 1.2 para ajustar a criatividade
QTD_NOTAS = 100

print(f"\nGerando {QTD_NOTAS} notas originais...")

for note_index in range(QTD_NOTAS):
    prediction_input = np.reshape(pattern, (1, len(pattern), 1)) / float(n_vocab)
    prediction = model.predict(prediction_input, verbose=0)[0]
    
    index = sample_with_temperature(prediction, temperature=TEMPERATURE)
    result = int_to_note[index]
    prediction_output.append(result)
    
    pattern.append(index)
    pattern = pattern[1:]

# -------------------------------------------------------------
# 4. EXPORTAÇÃO DO ARQUIVO MIDI
# -------------------------------------------------------------
offset = 0
output_notes = []

for pattern_str in prediction_output:
    if ('.' in pattern_str) or pattern_str.isdigit():
        notes_in_chord = pattern_str.split('.')
        notes = [note.Note(int(c)) for c in notes_in_chord]
        new_chord = chord.Chord(notes)
        new_chord.offset = offset
        output_notes.append(new_chord)
    else:
        new_note = note.Note(pattern_str)
        new_note.offset = offset
        output_notes.append(new_note)

    offset += 0.5

midi_stream = stream.Stream(output_notes)
nome_saida = 'minha_musica_gerada.mid'
midi_stream.write('midi', fp=nome_saida)

print(f"\n🎉 Sucesso! Sua música foi gerada e salva como '{nome_saida}' na pasta do projeto.")