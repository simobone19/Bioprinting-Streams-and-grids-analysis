from PIL import Image
import numpy as np
import os
from scipy.ndimage import gaussian_filter

Tag_image = "800"

# Percorso dell'immagine BMP sul desktop (includendo OneDrive)
desktop_path = "C:\\Users\\simob\\OneDrive - Consiglio Nazionale delle Ricerche\\Desktop\\pippo\\27"
image_path = os.path.join(desktop_path, 'image without blob' + Tag_image + '.bmp')

# Apri l'immagine
img = Image.open(image_path)

# Richiesta del valore di sigma per lo smoothing
sigma = float(input("Inserisci il valore di sigma per lo smoothing: "))

# Converti l'immagine in scala di grigi (8 bit)
bw_img = img.convert('L')

# Applica lo smooth all'immagine
bw_array = np.array(bw_img)
smoothed_array = gaussian_filter(bw_array, sigma=sigma)

# Binarizza l'immagine usando una soglia
threshold = 128
binary_img = (smoothed_array > threshold).astype(np.uint8) * 255

# Salva l'immagine con le aree nere e il resto bianco
smoothed_image = Image.fromarray(binary_img, 'L')
smoothed_image_path = os.path.join(desktop_path, 'smoothed_image' + Tag_image + '.bmp')
smoothed_image.save(smoothed_image_path)

print(f"Immagine smooth salvata in: {smoothed_image_path}")