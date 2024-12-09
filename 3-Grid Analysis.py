#calcolo senza smoothing
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import random

Tag_image = "400"

# Percorso dell'immagine BMP sul desktop (includendo OneDrive)
desktop_path = "C:\\Users\\simob\\OneDrive - Consiglio Nazionale delle Ricerche\\Desktop\\pippo\\31"
#image_path = os.path.join(desktop_path, 'filtered_griglia6.bmp')
image_path = os.path.join(desktop_path, 'smoothed_image' + Tag_image + '.bmp')

# Apri l'immagine
img = Image.open(image_path)

# Converti l'immagine in bianco e nero (8 bit)
bw_img = img.convert('L')

# Binarizza l'immagine usando una soglia
threshold = 128
binary_img = bw_img.point(lambda p: p > threshold and 255)
bw_array = np.array(binary_img)

# Trova le aree nere all'interno della griglia bianca
heights, widths = bw_array.shape
areas = []
visited = np.zeros((heights, widths), dtype=bool)


def dfs(x, y, area):
    stack = [(x, y)]
    touches_border = False
    while stack:
        cx, cy = stack.pop()
        if 0 <= cx < widths and 0 <= cy < heights and bw_array[cy, cx] == 0 and not visited[cy, cx]:
            visited[cy, cx] = True
            area.append((cx, cy))
            if cx == 0 or cx == widths-1 or cy == 0 or cy == heights-1:
                touches_border = True
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))
    return touches_border

# Rileva tutte le aree nere
for y in range(heights):
    for x in range(widths):
        if bw_array[y, x] == 0 and not visited[y, x]:
            area = []
            dfs(x, y, area)
            if area:
                areas.append(area)

# Calcola il perimetro e l'area di ciascuna area nera
area_stats = []
for index, area in enumerate(areas):
    perimeter = 0
    for x, y in area:
        # Controlla i vicini per determinare il perimetro
        if (x == 0 or x == widths-1 or y == 0 or y == heights-1 or
            bw_array[y-1, x] == 255 or bw_array[y+1, x] == 255 or
            bw_array[y, x-1] == 255 or bw_array[y, x+1] == 255):
            perimeter += 1
    perimeter = perimeter * 1.085 #Conversion factor Fiji like
    area_size = len(area)
    #if 500 <= area_size <= 500000:  # Filtra le aree con dimensione compresa tra 500 e 500000 pixel-per immmagine prova
    if 40000 <= area_size <= 300000:  # Filtra le aree con dimensione compresa tra 40000 e 500000 pixel
        area_stats.append((area, perimeter, area_size))

# Crea un'immagine a colori per la maschera delle aree
area_mask = Image.new('RGB', (widths, heights), 'white')
draw = ImageDraw.Draw(area_mask)
font_path = "arial.ttf"  # Assicurati che il font sia disponibile
font = ImageFont.truetype(font_path, 50)

# Colora l'area interna di giallo e disegna il perimetro di ciascuna area in viola con bordi sottili
for index, (area, perimeter, area_size) in enumerate(area_stats):
    # Colora l'area interna di giallo
    for (x, y) in area:
        area_mask.putpixel((x, y), (255, 255, 0))
    # Disegna il perimetro dell'area in viola con bordi sottili
    perimeter_points = [(x, y) for (x, y) in area if (
        x == 0 or x == widths-1 or y == 0 or y == heights-1 or
        bw_array[y-1, x] == 255 or bw_array[y+1, x] == 255 or
        bw_array[y, x-1] == 255 or bw_array[y, x+1] == 255)]
    for px, py in perimeter_points:
        area_mask.putpixel((px, py), (148, 0, 211))
        if px + 1 < widths: area_mask.putpixel((px + 1, py), (148, 0, 211))
        if py + 1 < heights: area_mask.putpixel((px, py + 1), (148, 0, 211))
        if px - 1 >= 0: area_mask.putpixel((px - 1, py), (148, 0, 211))
        if py - 1 >= 0: area_mask.putpixel((px, py - 1), (148, 0, 211))
    # Calcola il centro dell'area
    center_x = sum([x for x, _ in area]) // len(area)
    center_y = sum([y for _, y in area]) // len(area)
    # Aggiungi la numerazione al centro dell'area
    draw.text((center_x, center_y), str(index + 1), fill="black", font=font, anchor="mm")


# Salva l'immagine maschera delle aree
mask_path = os.path.join(desktop_path, 'area_mask_colored' + Tag_image + '.bmp')
area_mask.save(mask_path)


# Calcola media e deviazione standard del perimetro e dell'area
all_perimeters = [stat[1] for stat in area_stats]
all_areas = [stat[2] for stat in area_stats]
mean_perimeter = np.mean(all_perimeters)
std_perimeter = np.std(all_perimeters)
mean_area = np.mean(all_areas)
std_area = np.std(all_areas)

# Scrivi le statistiche delle aree in un file di testo
output_file_path = os.path.join(desktop_path, 'area_stats' + Tag_image + '.txt')
with open(output_file_path, 'w') as f:
    for index, (area, perimeter, area_size) in enumerate(area_stats):
        f.write(f"Area {index + 1}: Perimetro = {perimeter}, Area = {area_size}, Pritability = {(perimeter*perimeter)/(16*area_size)}, C = {(4*3.14*area_size)/(perimeter*perimeter)} \n")
    f.write(f"\nPerimetro medio: {mean_perimeter:.2f}, Deviazione standard del perimetro: {std_perimeter:.2f}\n")
    f.write(f"Area media: {mean_area:.2f}, Deviazione standard dell'area: {std_area:.2f}\n")


# Stampa un messaggio di conferma
print(f"Immagine della maschera delle aree salvata in: {mask_path}")
print(f"I dati delle aree sono stati salvati in: {output_file_path}")
print(f"Perimetro medio: {mean_perimeter:.2f}, Deviazione standard del perimetro: {std_perimeter:.2f}")
print(f"Area media: {mean_area:.2f}, Deviazione standard dell'area: {std_area:.2f}")




