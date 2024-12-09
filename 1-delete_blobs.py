from PIL import Image
import numpy as np
import os

Tag_image = "800"

# Percorso dell'immagine BMP sul desktop (includendo OneDrive)
desktop_path = "C:\\Users\\simob\\OneDrive - Consiglio Nazionale delle Ricerche\\Desktop\\pippo\\27"
image_path = os.path.join(desktop_path, '800gg_crop_BW.bmp')

# Apri l'immagine
img = Image.open(image_path)

# Converti l'immagine in bianco e nero (8 bit)
bw_img = img.convert('L')

# Binarizza l'immagine usando una soglia
threshold = 128
binary_img = bw_img.point(lambda p: p > threshold and 255)
bw_array = np.array(binary_img)

# Trova i blob bianchi all'interno della griglia nera
heights, widths = bw_array.shape
blobs = []
visited = np.zeros((heights, widths), dtype=bool)

# Identifica i blob bianchi usando DFS (Depth-First Search)
def dfs(x, y, blob):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if 0 <= cx < widths and 0 <= cy < heights and bw_array[cy, cx] == 255 and not visited[cy, cx]:
            visited[cy, cx] = True
            blob.append((cx, cy))
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))

# Rileva tutti i blob bianchi
for y in range(heights):
    for x in range(widths):
        if bw_array[y, x] == 255 and not visited[y, x]:
            blob = []
            dfs(x, y, blob)
            if blob:
                blobs.append(blob)

# Filtra i blob con area minore di 3000 pixel
blobs = [blob for blob in blobs if len(blob) >= 3000]

# Crea una nuova immagine binaria senza i blob piccoli
filtered_bw_array = np.zeros_like(bw_array)  # Inizializza con sfondo nero
for blob in blobs:
    for (x, y) in blob:
        filtered_bw_array[y, x] = 255  # Imposta i blob filtrati su bianco

# Salva l'immagine binaria filtrata
filtered_img = Image.fromarray(filtered_bw_array.astype(np.uint8))
filtered_image_path = os.path.join(desktop_path, 'image without blob' + Tag_image + '.bmp')
filtered_img.save(filtered_image_path)

# Stampa un messaggio di conferma
print(f"Immagine filtrata dei blob salvata in: {filtered_image_path}")