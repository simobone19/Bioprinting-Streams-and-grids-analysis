# Importa le librerie necessarie per la gestione delle immagini
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import random
import matplotlib.pyplot as plt

# Definizione del rapporto tra pixel e millimetri
PIXELS_PER_MM = 260
Tag_image = "800"

# Percorso della cartella sul desktop (includendo OneDrive)
desktop_path = "C:\\Users\\simob\\OneDrive - Consiglio Nazionale delle Ricerche\\Desktop\\pippo\\31"

# Percorso dell'immagine BMP
image_path = os.path.join(desktop_path, 'diff area 800 - 250um h_crop_BW.bmp')

# Apri l'immagine
img = Image.open(image_path)

# Converti l'immagine in bianco e nero (8 bit)
bw_img = img.convert('L')

# Binarizza l'immagine usando una soglia
threshold = 128
binary_img = bw_img.point(lambda p: p > threshold and 255)
bw_array = np.array(binary_img)

# Trova gli streams bianchi verticali
heights, widths = bw_array.shape
streams = []
visited = np.zeros((heights, widths), dtype=bool)


# Identifica gli streams bianchi usando DFS (Depth-First Search)
def dfs(x, y, stream):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if 0 <= cx < widths and 0 <= cy < heights and bw_array[cy, cx] == 255 and not visited[cy, cx]:
            visited[cy, cx] = True
            stream.append((cx, cy))
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))


# Rileva tutti gli streams bianchi
for y in range(heights):
    for x in range(widths):
        if bw_array[y, x] == 255 and not visited[y, x]:
            stream = []
            dfs(x, y, stream)
            if stream:
                streams.append(stream)

# Filtra gli streams con larghezza minore di 40 pixel - Valore che ho visto ottimale per scartare i difetti del vetrino
streams = [stream for stream in streams if (max([p[0] for p in stream]) - min([p[0] for p in stream]) + 1) >= 40]

# Calcola la larghezza media e la deviazione standard per ogni stream
stream_stats = []
for stream in streams:
    xs = [p[0] for p in stream]
    ys = [p[1] for p in stream]
    min_x = min(xs)
    max_x = max(xs)
    width = max_x - min_x + 1
    length = max(ys) - min(ys) + 1

    # Escludi lo stream se la lunghezza è inferiore a 300 pixel
    if length < 300:
        continue

    # Calcola la larghezza media e la deviazione standard delle righe di pixel
    row_widths = []
    for y in range(min(ys), max(ys) + 1, 10):  # Prendi una larghezza ogni 10 righe
        row_pixels = [x for x, yy in stream if yy == y]
        if row_pixels:
            row_width = max(row_pixels) - min(row_pixels) + 1
            row_widths.append(row_width)

    mean_width = np.mean(row_widths)
    std_dev = np.std(row_widths)

    # Converte le dimensioni da pixel a millimetri
    width_mm = width / PIXELS_PER_MM
    mean_width_mm = mean_width / PIXELS_PER_MM
    std_dev_mm = std_dev / PIXELS_PER_MM

    stream_stats.append((stream, width, width_mm, length, mean_width, mean_width_mm, std_dev, std_dev_mm))

# Crea un'immagine a colori per la maschera degli streams
line_mask = Image.new('RGB', (widths, heights), 'black')
draw = ImageDraw.Draw(line_mask)

# Usa un font più grande per i numeri
try:
    font = ImageFont.truetype("arial.ttf", 50)
except IOError:
    font = ImageFont.load_default()

# Colora ogni stream con un colore diverso e aggiungi la numerazione al centro
for index, (stream, width, width_mm, length, mean_width, mean_width_mm, std_dev, std_dev_mm) in enumerate(stream_stats):
    color = random.choice([(255, 30, 0), (30, 255, 0), (60, 30, 255),(255, 30, 80), (30, 255, 70), (80, 30, 255),(255, 30, 90), (30, 255, 110), (120, 30, 255),(255, 120, 90), (30, 15, 110), (120, 0, 255),(60, 30, 255),(160, 0, 230),(100, 0, 245),(140, 0, 210)])  # Selezione casuale del colore
    for (x, y) in stream:
        draw.point((x, y), fill=color)
    # Calcola il centro dello stream
    center_x = min([x for x, _ in stream]) + (max([x for x, _ in stream]) - min([x for x, _ in stream])) // 2
    center_y = min([y for _, y in stream]) + (max([y for _, y in stream]) - min([y for _, y in stream])) // 2
    # Aggiungi la numerazione al centro dello stream
    draw.text((center_x, center_y), str(index + 1), fill="white", font=font, anchor="mm")

# Salva l'immagine maschera
mask_path = os.path.join(desktop_path, 'line_mask_colored' + Tag_image + '.bmp')
line_mask.save(mask_path)

# Scrivi le larghezze, lunghezze, medie e deviazioni standard degli streams in un file di testo
output_file_path = os.path.join(desktop_path, 'stream_stats' + Tag_image + '.txt')
with open(output_file_path, 'w') as f:
    for index, (stream, width, width_mm, length, mean_width, mean_width_mm, std_dev, std_dev_mm) in enumerate(stream_stats):
        f.write(
            f"Stream {index + 1}: Larghezza = {width} pixel ({width_mm:.2f} mm), Lunghezza = {length}, Media larghezza = {mean_width} pixel ({mean_width_mm:.2f} mm), Deviazione standard = {std_dev} pixel ({std_dev_mm:.2f} mm)\n")

# Stampa un messaggio di conferma
print(f"Immagine della maschera degli streams salvata in: {mask_path}")
print(f"I dati degli streams sono stati salvati inin: {output_file_path}")


# Estrai le larghezze medie e le deviazioni standard da stream_stats
mean_widths_mm = [mean_width_mm for _, _, _, _, _, mean_width_mm, _, _ in stream_stats]
std_devs_mm = [std_dev_mm for _, _, _, _, _, _, _, std_dev_mm in stream_stats]

# Genera un grafico
plt.figure(figsize=(10, 6))
plt.errorbar(range(1, len(stream_stats) + 1), mean_widths_mm, yerr=std_devs_mm, fmt='o', markersize=5, capsize=5)
plt.title('Larghezze Medie degli Streams con Deviazioni Standard')
plt.xlabel('Stream')
plt.ylabel('Larghezza Media (mm)')
plt.grid(True)
plt.ylim(0)  # Imposta l'origine dell'asse y a 0
plt.tight_layout()

# Mostra il grafico
plt.show()
