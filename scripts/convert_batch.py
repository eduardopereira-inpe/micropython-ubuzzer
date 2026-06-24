import csv
from melodies import export_song_to_bytes
from melodies.melodies import MELODY_CATALOG, MELODY_LIST

# Abre o arquivo em modo texto com codificação UTF-8 e prevenção de quebras de linha extras
with open("catalog.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    
    # Escreve o cabeçalho do CSV
    writer.writerow(["Melody Name", "Length", "Bytes String"])
    
    # Varre o catálogo e as músicas
    for i, melody_name in enumerate(MELODY_CATALOG):
        melody = MELODY_LIST[i]
        melody_bytes = export_song_to_bytes(melody)
        
        # Converte os bytes puros para a string literal que o Python entende (ex: b'\x00\x8c...')
        bytes_string_format = str(melody_bytes)
        
        # Escreve a linha no CSV
        writer.writerow([melody_name, len(melody_bytes), bytes_string_format])

print("Catálogo de músicas exportado com sucesso no formato string de bytes!")